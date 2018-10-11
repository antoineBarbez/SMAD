import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;


public class JDMetricsFileCreator {
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
	//private static List<String> metricsFileLines = new ArrayList<String>();
	
	private static ASTReader reader;
	
	private static void createMetricsFile(
		String aName, 
		String[] sourcePaths,
		String metricsFilePath) {
		
		System.out.println("Begin creating metrics-file for " + aName + "...");
		
		reader = new ASTReader(sourcePaths);
		
		//The Header ,e.g, the column names of the csv file.
		String firstLine = "Method;TargetClass;NbAccessedEntities;Distance_TC";
		
		//Write each lines in the metrics file.
		final Iterator<String> iter = getLines().iterator();
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
	
	private static List<String> getLines() {
		List<String> lines = new ArrayList<String>();
		for (Map.Entry<String, Set<String>> entry : reader.getMethodToTargetClassSetMap().entrySet()) {
			String method = entry.getKey();
			
			//Avoid foreign classes
			Set<String> targetClassSet = new HashSet<String>();
			for (String targetClass : entry.getValue()) {
				if (reader.getClassToEntitySetMap().containsKey(targetClass))
					targetClassSet.add(targetClass);
			}
			
			//Avoid targetClass sets that only contains the owner class
			if (!(targetClassSet.size() == 1 && method.startsWith(targetClassSet.iterator().next()))) {
				for (String targetClass : targetClassSet) {
					StringBuffer lineBuffer = new StringBuffer();
					lineBuffer.append(method);
					lineBuffer.append(";");
					lineBuffer.append(targetClass);
					lineBuffer.append(";");
					
					int nbAccessedField = getNbAccessedEntities(targetClass, reader.getMethodToEntitySetMap().get(method));
					lineBuffer.append(String.valueOf(nbAccessedField));
					lineBuffer.append(";");
					
					double distanceToTargetClass = getDistance(reader.getMethodToEntitySetMap().get(method), reader.getClassToEntitySetMap().get(targetClass));
					lineBuffer.append(String.valueOf(distanceToTargetClass));
					
					lines.add(lineBuffer.toString());
				}
			}
		}
		
		return lines;
	}
	
	private static int getNbAccessedEntities(String targetClass, Set<String> entitySet) {
		int count = 0;
		for (String entity : entitySet) {
			if (entity.startsWith(targetClass)) {
				count++;
			}
		}
		return count;
	}
	
	
	private static double getDistance(Set<String> set1, Set<String> set2) {
        if(set1.isEmpty() && set2.isEmpty())
            return 1.0;
        return 1.0 - (double)intersection(set1,set2).size()/(double)union(set1,set2).size();
    }

    private static Set<String> union(Set<String> set1, Set<String> set2) {
        Set<String> set = new HashSet<String>();
        set.addAll(set1);
        set.addAll(set2);
        return set;
    }

    private static Set<String> intersection(Set<String> set1, Set<String> set2) {
        Set<String> set = new HashSet<String>();
        set.addAll(set1);
        set.retainAll(set2);
        return set;
    }
}