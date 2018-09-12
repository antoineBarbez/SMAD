import java.io.File;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Iterator;
import java.util.List;

import org.apache.commons.io.FileUtils;
import org.apache.commons.io.FilenameUtils;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.CompilationUnit;


public class FeatureEnvyMetricsFileCreator {
	public static void main(String[] args) {
		String name;
		String repositoryPath;
		String[] sources;
		String metricsFilePath;			
		
		if (args.length < 3) {
			System.out.println("Too few arguments");
			return;
		}else if (args.length == 3) {
			// Happens when the directories to analyze are "",e.g, analyze all directories. 
			name = args[0];
			repositoryPath = args[1];
			sources = new String[] {""};
			metricsFilePath = args[2];
		}else {
			name = args[0];
			repositoryPath = args[1];
			sources = args[2].split("@", -1);
			metricsFilePath = args[3];
		}
		
		String[] sourcePaths = new String[sources.length];
		for (int i=0;i<sources.length;i++) {
			sourcePaths[i] = repositoryPath + sources[i];
		}
		
		createMetricsFile(name, sourcePaths, metricsFilePath);
	}
	
	// The (csv) lines that compose the metrics file 
	private static List<String> metricsFileLines = new ArrayList<String>();
	
	private static void createMetricsFile(
			String aName, 
			String[] sourcePaths,
			String metricsFilePath) {
			
			System.out.println("Begin creating metrics-file for " + aName + "...");
			
			int nbProcessedFiles = 0;
			for (int i=0;i<sourcePaths.length;i++) {
				Collection<File> filesInDirectory = FileUtils.listFiles(new File(sourcePaths[i]), new String[]{"java"}, true);
				for (File file : filesInDirectory) {
					String fileName = FilenameUtils.normalize(file.getAbsolutePath(), true).substring(sourcePaths[i].length());
					try {
						analyze(file, fileName, sourcePaths);
					}
					catch (IOException e) {
						System.out.println("IOExeption when analyzing the file: " + file.toString());
					}
					
					nbProcessedFiles++;
					if ((nbProcessedFiles % 500) == 0) {
						System.out.println(nbProcessedFiles + " files have been processed.");
					}
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
	
		
	private static void  analyze(File file, String fileName, String[] sourcePaths) throws IOException {
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
		
		ATFDFileVisitor v = new ATFDFileVisitor();
		cu.accept(v);
		
		metricsFileLines.addAll(v.getLines());
	}
}