import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.CompilationUnit;

public class ASTReader {
	private List<String> types =  new ArrayList<String>();
	private Set<String> staticEntities = new HashSet<String>();
	private Map<String, String> accessorToAccessedFieldMap = new LinkedHashMap<String,String>();
	private Map<String, Set<String>> classToEntitySetMap = new LinkedHashMap<String,Set<String>>();
	private Map<String, Set<String>> methodToEntitySetMap = new LinkedHashMap<String,Set<String>>();
	private Map<String, Set<String>> methodToTargetClassSetMap = new LinkedHashMap<String,Set<String>>();
	
	public ASTReader(String[] sourcePaths) {
		int nbProcessedFiles = 0;
		for (int i=0;i<sourcePaths.length;i++) {
			Collection<File> filesInDirectory = FileUtils.listFiles(new File(sourcePaths[i]), new String[]{"java"}, true);
			for (File file : filesInDirectory) {
				String fileName = FilenameUtils.normalize(file.getAbsolutePath(), true).substring(sourcePaths[i].length());
				try {
					parseAST(file, fileName, sourcePaths);
				}
				catch (IOException e) {
					e.printStackTrace();
				}
				
				nbProcessedFiles++;
				if ((nbProcessedFiles % 500) == 0) {
					System.out.println(nbProcessedFiles + " files have been processed.");
				}
			}
		}
		
		replaceAccessorsByAccessedFields(methodToEntitySetMap);

		removeSystemMemberAccesses(classToEntitySetMap);
		removeSystemMemberAccesses(methodToEntitySetMap);
		
		removeStaticEntities(methodToEntitySetMap);
	}
	
	private void parseAST(File file, String fileName, String[] sourcePaths) throws IOException {
		String fileString = FileUtils.readFileToString(file, "UTF-8");
		
		ASTParser parser = ASTParser.newParser(AST.JLS8);
		parser.setKind(ASTParser.K_COMPILATION_UNIT);
		parser.setResolveBindings(true);
		parser.setBindingsRecovery(true);
		parser.setCompilerOptions(JavaCore.getOptions());
		parser.setUnitName(fileName);
		
		parser.setEnvironment(null, sourcePaths, null, true);
		parser.setSource(fileString.toCharArray());
		
		CompilationUnit cu = (CompilationUnit) parser.createAST(null);
		
		FileVisitor visitor = new FileVisitor();
		cu.accept(visitor);
		
		types.addAll(visitor.getTypes());
		staticEntities.addAll(visitor.getStaticEntities());
		accessorToAccessedFieldMap.putAll(visitor.getaccessorToAccessedFieldMap());
		classToEntitySetMap.putAll(visitor.getClassToEntitySetMap());
		methodToEntitySetMap.putAll(visitor.getMethodToEntitySetMap());
		methodToTargetClassSetMap.putAll(visitor.getMethodToTargetClassSetMap());
	}
	
	public Map<String, Set<String>> getClassToEntitySetMap() {
		return this.classToEntitySetMap;
	}
	
	public Map<String, Set<String>> getMethodToEntitySetMap() {
		return this.methodToEntitySetMap;
	}
	
	public Map<String, Set<String>> getMethodToTargetClassSetMap() {
		return this.methodToTargetClassSetMap;
	}
	
	private void replaceAccessorsByAccessedFields(Map<String, Set<String>> map) {
		for(Map.Entry<String, Set<String>> entry : map.entrySet()) {
			List<String> entitiesToRemove = new ArrayList<String>();
			List<String> entitiesToAdd = new ArrayList<String>();
			for(String entity :entry.getValue()) {
				if (accessorToAccessedFieldMap.containsKey(entity)) {
					entitiesToRemove.add(entity);
					entitiesToAdd.add(accessorToAccessedFieldMap.get(entity));
				}	
			}
			map.get(entry.getKey()).removeAll(entitiesToRemove);
			map.get(entry.getKey()).addAll(entitiesToAdd);
		}
	}
	
	private void removeSystemMemberAccesses(Map<String, Set<String>> map) {
		Pattern p = Pattern.compile(".+:(.+)");
		
		for(Map.Entry<String, Set<String>> entry : map.entrySet()) {
			List<String> entitiesToRemove = new ArrayList<String>();
			for(String entity :entry.getValue()) {
				Matcher m = p.matcher(entity);
				if (m.matches()) 
					if(types.contains(m.group(1)))
						entitiesToRemove.add(entity);
			}
			map.get(entry.getKey()).removeAll(entitiesToRemove);
		}
	}
	
	private void removeStaticEntities(Map<String, Set<String>> map) {
		for(Map.Entry<String, Set<String>> entry : map.entrySet()) {
			List<String> entitiesToRemove = new ArrayList<String>();
			for(String entity :entry.getValue()) {
				if (staticEntities.contains(entity))
					entitiesToRemove.add(entity);
			}
			map.get(entry.getKey()).removeAll(entitiesToRemove);
		}
	}
}