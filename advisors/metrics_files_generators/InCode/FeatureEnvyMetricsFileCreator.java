package metricsExtractor;

import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.*;
import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;
import org.apache.commons.lang.StringUtils;
import org.repositoryminer.metrics.parser.Language;
import org.repositoryminer.metrics.parser.Parser;
import org.repositoryminer.metrics.parser.java.JavaParser;
import org.repositoryminer.metrics.ast.AbstractFieldAccess;
import org.repositoryminer.metrics.ast.AbstractMethod;
import org.repositoryminer.metrics.ast.AbstractMethodInvocation;
import org.repositoryminer.metrics.ast.AST;
import org.repositoryminer.metrics.ast.AbstractStatement;
import org.repositoryminer.metrics.ast.AbstractType;
import org.repositoryminer.metrics.ast.NodeType;
import org.repositoryminer.util.RMFileUtils;

public class FeatureEnvyMetricsFileCreator {
	private static Map<String, Parser> parsersToUse = new LinkedHashMap<>();
	private static Map<Language, String[]> sourceFolders = new LinkedHashMap<>();
	
	// The (csv) lines that compose the metrics file 
	private static List<String> metricsFileLines = new ArrayList<String>();
	
	public static void main(String[] args) throws IOException {
		String repositoryPath;
		String[] dirsToAnalyze;
		String metricsFilePath;
		
		if (args.length < 2) {
			System.out.println("Too few arguments");
			return;
		}else if (args.length == 2) {
			// Happens when the directories to analyze is "",e.g, analyze all directories. 
			repositoryPath = args[0];
			dirsToAnalyze = new String[] {""};
			metricsFilePath = args[1];
		}else {
			repositoryPath = args[0];
			dirsToAnalyze = args[1].split("@", -1);
			metricsFilePath = args[2];
		}
		
		createMetricsFile(repositoryPath, dirsToAnalyze, metricsFilePath);
		
	}
	
	private static void createMetricsFile(
		String repositoryPath, 
		String[] dirsToAnalyze,
		String metricsFilePath) {
		
		System.out.println("Begin creating metrics file...");
		
		List<Parser> parsers = new ArrayList<>();
		parsers.add(new JavaParser());
		for (Parser p : parsers) {
			if (p.getSourceFolders() == null || p.getSourceFolders().length == 0) {
				p.setSourceFolders(RMFileUtils.getAllDirsAsString(repositoryPath).toArray(new String[0]));
			} else {
				p.setSourceFolders(RMFileUtils.concatFilePath(repositoryPath, p.getSourceFolders()));
			}

			for (String ext : p.getExtensions()) {
				parsersToUse.put(ext, p);
			}
		}
		
		Collection<File> filesInSystem = FileUtils.listFiles(new File(repositoryPath), parsersToUse.keySet().toArray(new String[0]), true);
		System.out.println("System contains " + filesInSystem.size() + " files.");
		int nbProcessedFiles = 0;
		for (File file : filesInSystem) {
			String fileName = FilenameUtils.normalize(file.getAbsolutePath(), true).substring(repositoryPath.length());
			if (StringUtils.startsWithAny(fileName, dirsToAnalyze)){
				try {
					analyzeFile(file, fileName);
				}
				catch (IOException e) {
					System.out.println("IOExeption when analyzing the file: " + file.toString());
				}
			}
			
			nbProcessedFiles++;
			if ((nbProcessedFiles % 1000) == 0) {
				System.out.println(nbProcessedFiles + " files have been processed.");
			}
		}
		//The Header ,e.g, the column names of the csv file.
		String firstLine = "Class;Method;DeclaringClass;NbFields";
		
		//Write each lines in the metrics file.
		final Iterator<String> iter = metricsFileLines.iterator();
		try (PrintWriter out = new PrintWriter(metricsFilePath)) {
			out.println(firstLine);
			while (iter.hasNext()) {
				String csvLine = iter.next();
				if (csvLine != null) {
					out.println(csvLine);
				}
			}
			out.close();
		}
		catch (final java.io.FileNotFoundException e) {
			System.out.print("file not found");
		}
	}
	
	private static void analyzeFile(File file, String fileName) throws IOException {
		Parser parser = parsersToUse.get(FilenameUtils.getExtension(file.getAbsolutePath()));
		if (parser == null) {
			return;
		}

		//Parse the file into an AST object
		AST ast = parser.generate(fileName, FileUtils.readFileToString(file, "UTF-8"),
				sourceFolders.get(parser.getId()));

		for (AbstractType type : getTypes(ast)) {
			String className = type.getName();
			
			for (AbstractMethod method : type.getMethods()) {
				String methodName = normalizeMethodName(method.getName());
				
				Map<String, Integer> atfMap = getAccessToFieldMap(method);
				for (Map.Entry<String, Integer> entry : atfMap.entrySet()) {
					StringBuffer buffer = new StringBuffer();
					
					buffer.append(className);
					buffer.append(";");
					buffer.append(methodName);
					buffer.append(";");
					buffer.append(entry.getKey());
					buffer.append(";");
					buffer.append(entry.getValue());
					
					metricsFileLines.add(buffer.toString());
				}
			}
		}
	}
	
	// To take care of Inner Classes
	private static List<AbstractType> getTypes(AST ast) {
		//We must first sort the types by size to avoid wrong renaming
		List<AbstractType> types = ast.getTypes();
		int[] sizes = new int[types.size()];
		for (int i=0;i<types.size();i++) {
			sizes[i] = types.get(i).getEndPosition() - types.get(i).getStartPosition();
		}
		int[] argsortSizes = argsort(sizes, false);
		
		for (int j=0;j<types.size();j++) {
			AbstractType type = types.get(argsortSizes[j]);
			
			int startPosition = type.getStartPosition();
			int endPosition = type.getEndPosition();
			Set<String> innerMethods = new HashSet<String>();
			for (AbstractType klass : types) {
				if ((klass.getStartPosition() > startPosition) && (klass.getEndPosition() < endPosition)) {
					//Change the name of the class
					String[] splittedName = klass.getName().split("\\.");
					String name = splittedName[splittedName.length -1];
					klass.setName(type.getName() + "." + name);
					
					//remove it's methods from the wrapping class
					for (AbstractMethod method : klass.getMethods()) {
						innerMethods.add(method.getName());
					}
				}
			}
			
			
			Iterator<AbstractMethod> methodsIterator = type.getMethods().iterator();
			List<AbstractMethod> methodsList = new ArrayList<AbstractMethod>();
			while (methodsIterator.hasNext()) {
				AbstractMethod method = methodsIterator.next();
				if (!innerMethods.contains(method.getName())) {
					methodsList.add(method);
				}
			}
			type.setMethods(methodsList);
		}
		
		return types;
	}
	
	// Returns a Map whose keys are classes whose fields/attributes are accessed within the method body,
	// and values are the number of accessed fields per class.
	private static Map<String, Integer> getAccessToFieldMap(AbstractMethod method) {
		Set<String> accessedFields = new HashSet<String>();
		for (AbstractStatement stmt : method.getStatements()) {
			String field = null;
			String declarringClass = null;

			if (stmt.getNodeType() == NodeType.FIELD_ACCESS) {
				AbstractFieldAccess fieldAccess = (AbstractFieldAccess) stmt;
				field = fieldAccess.getExpression();
				declarringClass = fieldAccess.getDeclaringClass();
			} else if (stmt.getNodeType() == NodeType.METHOD_INVOCATION) {
				AbstractMethodInvocation methodInvocation = (AbstractMethodInvocation) stmt;
				if (!methodInvocation.isAccessor()) {
					continue;
				}
				field = methodInvocation.getAccessedField();
				declarringClass = methodInvocation.getDeclaringClass();
				
			} else { 
				continue;
			}
			
			accessedFields.add(declarringClass + '+' + field);
		}
		
		Map<String, Integer> atfMap = new HashMap<String, Integer>();
		for (String accessedField : accessedFields) {
			String [] accessedFieldList = accessedField.split("\\+");
			String declaringClass = accessedFieldList[0];
			
			if (!declaringClass.equals("") && !declaringClass.equals("null")) {	
				int count = atfMap.containsKey(declaringClass) ? atfMap.get(declaringClass) : 0;
				atfMap.put(declaringClass, count + 1);
			}
		}
		
		return atfMap;
	}
	
	private static final String normalizeMethodName(String methodName) {
		Pattern methodPattern = Pattern.compile("(.+)\\((.*)\\)");
		Matcher m1 = methodPattern.matcher(methodName);
		
		try {
			m1.matches();
			String name = m1.group(1);
			String parameters = m1.group(2);
			String[] paramList = parameters.split(",", -1);
			
			List<String> normalizedParamList = new ArrayList<String>();
			for (int i=0; i<paramList.length;i++) {
				String[] splittedType = paramList[i].split("\\.", -1);
				String normalizedParam = splittedType[splittedType.length-1];
				Pattern paramPattern = Pattern.compile("(\\w*)\\W*");
				Matcher m2 = paramPattern.matcher(normalizedParam);
				
				m2.matches();
				normalizedParamList.add(m2.group(1));
			}
			Collections.sort(normalizedParamList, String.CASE_INSENSITIVE_ORDER);
			
			StringBuffer buffer = new StringBuffer();
			buffer.append(name);
			buffer.append("(");
			buffer.append(String.join(", ", normalizedParamList));
			buffer.append(")");
			
			return buffer.toString();
		}
		catch (java.lang.IllegalStateException e) {
			return methodName;
		}
	}
	

    private static int[] argsort(final int[] a, final boolean ascending) {
        Integer[] indexes = new Integer[a.length];
        for (int i = 0; i < indexes.length; i++) {
            indexes[i] = i;
        }
        Arrays.sort(indexes, new Comparator<Integer>() {
            public int compare(final Integer i1, final Integer i2) {
                return (ascending ? 1 : -1) * Integer.compare(a[i1], a[i2]);
            }
        });
        return asArray(indexes);
    }
    
    private static int[] asArray(Integer[] a) {
        int[] b = new int[a.length];
        for (int i = 0; i < b.length; i++) {
            b[i] = a[i].intValue();
        }
        return b;
    }
}