import java.io.File;
//import java.io.FileNotFoundException;
//import java.io.FilenameFilter;
//import java.io.IOException;
//import java.io.LineNumberReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Set;
//import java.util.Properties;
import java.util.HashMap;
import java.util.Map;
import java.util.HashSet;
import padl.analysis.UnsupportedSourceModelException;
import padl.analysis.repository.AACRelationshipsAnalysis;
//import padl.creator.classfile.CompleteClassFileCreator;
import padl.creator.javafile.eclipse.CompleteJavaFileCreator;
//import padl.kernel.IAbstractLevelModel;
import padl.kernel.ICodeLevelModel;
import padl.kernel.IFirstClassEntity;
import padl.kernel.IEntity;
import padl.kernel.IClass;
import padl.kernel.IGhost;
import padl.kernel.IIdiomLevelModel;
import padl.kernel.exception.CreationException;
import padl.kernel.impl.Factory;
import padl.kernel.IUseRelationship;
import padl.kernel.ICreation;
import pom.metrics.IUnaryMetric;
import pom.metrics.MetricsRepository;
//import ptidej.solver.Occurrence;
//import ptidej.solver.OccurrenceBuilder;
//import ptidej.solver.OccurrenceComponent;
//import sad.designsmell.detection.IDesignSmellDetection;
import sad.codesmell.detection.repository.Blob.ControllerClassDetection;
import sad.codesmell.detection.repository.Blob.DataClassDetection;
import sad.kernel.ICodeSmell;
import sad.util.BoxPlot;
import util.io.ProxyConsole;
//import util.io.ProxyDisk;
//import util.io.ReaderInputStream;
import java.util.Iterator;
//import java.util.regex.*;

import org.apache.commons.lang.ArrayUtils;


public class PtidejSmellDetection {

	public static void main(String[] args) {
		final String[] directories = args[1].split("@", -1);
		
		PtidejSmellDetection.analyseCodeLevelModelFromJavaSourceFiles(
				args[0],
				directories,
				args[2], 
				"Ptidej_detection_results/", 
				args[3]);

	}
	
	public static final void analyseCodeLevelModelFromJavaSourceFiles(
			final String aSmell,
			final String [] someSourcePaths,
			final String aName,
			final String anOutputDirectoryName,
			final String smellFile) {

			System.out.print("Analysing ");
			System.out.print(aName);
			System.out.println("...");

			try {
				final long startTime = System.currentTimeMillis();
				final CompleteJavaFileCreator creator =
					new CompleteJavaFileCreator(
						someSourcePaths,
						new String[] { "" },
						someSourcePaths);
				final ICodeLevelModel codeLevelModel =
					Factory.getInstance().createCodeLevelModel(aName);
				codeLevelModel.create(creator);
				final long endTime = System.currentTimeMillis();
				System.out.print("Model built in ");
				System.out.print(endTime - startTime);
				System.out.println(" ms.");
				System.out.print("Model contains ");
				System.out.print(codeLevelModel.getNumberOfTopLevelEntities());
				System.out.println(" top-level entities.");

				//	try {
				final padl.creator.javafile.eclipse.astVisitors.LOCModelAnnotator annotator2 =
					new padl.creator.javafile.eclipse.astVisitors.LOCModelAnnotator(
						codeLevelModel);
				creator.applyAnnotator(annotator2);
				
				final padl.creator.javafile.eclipse.astVisitors.ConditionalModelAnnotator annotator1 =
					new padl.creator.javafile.eclipse.astVisitors.ConditionalModelAnnotator(
						codeLevelModel);
				creator.applyAnnotator(annotator1);

				// Create the output directory if needed.
				final String newOutputDirectoryName =
					anOutputDirectoryName + aName + File.separatorChar;

				/*List<String> smells = PtidejSmellDetection.analyseCodeLevelModel(
											aSmell,
											aName,
											codeLevelModel,
											newOutputDirectoryName);*/
				List<String> smells = PtidejSmellDetection.analyse(codeLevelModel);
				
				String firstLine = "";
				if (aSmell.equals("Blob")) {
					firstLine = "ClassName;NMD+NAD;nmdNadBound;LCOM5;lcom5Bound;ControllerClass;nbDataClass";
				}
				
				final Iterator<String> iter = smells.iterator();
				
				try (PrintWriter out = new PrintWriter(smellFile)) {
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
			catch (final SecurityException e) {
				e.printStackTrace(ProxyConsole.getInstance().errorOutput());
			}
			catch (final IllegalArgumentException e) {
				e.printStackTrace(ProxyConsole.getInstance().errorOutput());
			}
			catch (final CreationException e) {
				e.printStackTrace(ProxyConsole.getInstance().errorOutput());
			}
		}
	
	
	public static final List<String> analyse(final ICodeLevelModel codeLevelModel) {

			List<String> smells = new ArrayList<String>();
			
			try {
				final IIdiomLevelModel idiomLevelModel =
					(IIdiomLevelModel) new AACRelationshipsAnalysis()
						.invoke(codeLevelModel);

				smells = PtidejSmellDetection.analyse(idiomLevelModel);
			}
			catch (final UnsupportedSourceModelException e) {
				e.printStackTrace(ProxyConsole.getInstance().errorOutput());
			}
			
			return smells;
		}
	
	public static final List<String> analyse(final IIdiomLevelModel idiomLevelModel) {
		List<String> lines = new ArrayList<String>();

		final HashMap<String, String> boundsDictionnary = PtidejSmellDetection.getBounds(idiomLevelModel);
		final Set dataClasses = PtidejSmellDetection.getDataClasses(idiomLevelModel);
		final List<String> ccNames = PtidejSmellDetection.getControllerClassesNames(idiomLevelModel);
		final MetricsRepository metricsRepository = MetricsRepository.getInstance();

		final Iterator entityIterator =
				idiomLevelModel.getIteratorOnTopLevelEntities();
		while (entityIterator.hasNext()) {
			final IFirstClassEntity firstClassEntity =
					(IFirstClassEntity) entityIterator.next();

			if (!(firstClassEntity instanceof IGhost)) {
				StringBuffer buffer = new StringBuffer();
				double nmdNad = 0;
				double lcom5 = 0;
				int cc = 0;
				int nbDc = PtidejSmellDetection.getNumberOfAssociatedDataClasses(firstClassEntity, dataClasses);
				
				if (ccNames.contains(String.valueOf(firstClassEntity.getID()))) {
					cc = 1;
				}

				final IUnaryMetric[] metrics =
						metricsRepository.getUnaryMetrics();


				for (int i = 0; i < metrics.length; i++) {
					final IUnaryMetric unaryMetric = metrics[i];
					final String metricName = unaryMetric.getName();
					try {
						if (ArrayUtils.contains(
								new String[] { "NMD","NAD" },
								metricName)) {

							final double value = unaryMetric.compute(idiomLevelModel, firstClassEntity);
							nmdNad += value;
						}
					} catch (final Exception e) {
						nmdNad = 0;
					}

					try {
						if  (metricName.equals("LCOM5")) {
							lcom5 = unaryMetric.compute(idiomLevelModel, firstClassEntity);
						}
					} catch (final Exception e) {
						lcom5 = 0;
					}
				}

				buffer.append(firstClassEntity.getID());
				buffer.append(';');
				buffer.append(String.valueOf(nmdNad));
				buffer.append(';');
				buffer.append(boundsDictionnary.get("nmdNad"));
				buffer.append(';');
				buffer.append(String.valueOf(lcom5));
				buffer.append(';');
				buffer.append(boundsDictionnary.get("lowCohesion"));
				buffer.append(';');
				buffer.append(cc);
				buffer.append(';');
				buffer.append(nbDc);

				lines.add(buffer.toString());
			}
		}

		return lines;
	}
	
	public static final Set getDataClasses(IIdiomLevelModel idiomLevelModel) {
		DataClassDetection dcDetection = new DataClassDetection();
		dcDetection.detect(idiomLevelModel);
		
		return dcDetection.getCodeSmells();
	}
	
	public static final int getNumberOfAssociatedDataClasses(IFirstClassEntity refClass, Set setCodeSmells) {
		final Map classes = new HashMap();

		final Iterator iterCodeSmell = setCodeSmells.iterator();
		while (iterCodeSmell.hasNext()) {
			final ICodeSmell aCodeSmell = (ICodeSmell) iterCodeSmell.next();
			classes.put(aCodeSmell.getIClass(), aCodeSmell);
		}

		Set subset = new HashSet();

		final Iterator iterRelations =
				refClass.getConcurrentIteratorOnConstituents(
						IUseRelationship.class);
		while (iterRelations.hasNext()) {
			final IUseRelationship relationship =
					(IUseRelationship) iterRelations.next();
			final IFirstClassEntity target = relationship.getTargetEntity();

			// Yann 2007/03/08: Self-reference
			// An entity always knows itself so I prevent
			// self-reference to be used to distinguish
			// code smells.
			if (!(relationship instanceof ICreation)
					&& target instanceof IClass
					&& !target.equals(refClass)) {

				// Get the codesmell related to the class
				final Object tmpCodeSmell = classes.get(target);
				if (tmpCodeSmell != null) {
					subset.add(tmpCodeSmell);
				}
			}
		}

		return subset.size();
	}
	
	public static final List<String> getControllerClassesNames(IIdiomLevelModel idiomLevelModel) {
		ControllerClassDetection ccDetection = new ControllerClassDetection();
		ccDetection.detect(idiomLevelModel);
		
		final Iterator iter = ccDetection.getCodeSmells().iterator();
		List<String> names = new ArrayList<String>();
		while (iter.hasNext()) {
			final ICodeSmell codeSmell = (ICodeSmell) iter.next();
			names.add(codeSmell.getIClassID());
		}
		
		return names;
	}
	
	public static final HashMap<String, String> getBounds(IIdiomLevelModel idiomLevelModel) {
		HashMap<String, String> boundsDictionnary = new HashMap<String, String>();
		
		final HashMap mapOfLowCohesionValues = new HashMap();
		final HashMap mapOfLargeClassValues = new HashMap();
		
		final Iterator iter = idiomLevelModel.getIteratorOnTopLevelEntities();
		while (iter.hasNext()) {
			final IEntity entity = (IEntity) iter.next();
			if (entity instanceof IClass) {
				final IClass aClass = (IClass) entity;
				
				//Low Cohesion Metrics
				final double LCOM5 = ((IUnaryMetric) MetricsRepository.getInstance().getMetric("LCOM5")).compute(idiomLevelModel, aClass);
				mapOfLowCohesionValues.put(aClass, new Double[] {new Double(LCOM5), new Double(0)});

				//Large Class Metrics
				final double NMD = ((IUnaryMetric) MetricsRepository.getInstance().getMetric("NMD")).compute(idiomLevelModel, aClass);
				final double NAD = ((IUnaryMetric) MetricsRepository.getInstance().getMetric("NAD")).compute(idiomLevelModel, aClass);
				mapOfLargeClassValues.put(aClass, new Double[] {new Double (NMD + NAD), new Double(0)});
				
			}
		}
		BoxPlot boxPlot = new BoxPlot(mapOfLargeClassValues, 0.0);
		boundsDictionnary.put("nmdNad", String.valueOf(boxPlot.getMaxBound()));
		
		boxPlot = new BoxPlot(mapOfLowCohesionValues, 20.0);
		boundsDictionnary.put("lowCohesion", String.valueOf(boxPlot.getMaxBound()));
		
		return boundsDictionnary;
	}
/*	
	public static final List<String> analyseCodeLevelModel(
			final String aSmell,
			final String aName,
			final IIdiomLevelModel idiomLevelModel,
			final String anOutputDirectory) {
			
			List<String> smells = new ArrayList<String>();
		
			try {
				final String antipatternName = aSmell;

				final long startTime = System.currentTimeMillis();
				final Class<?> detectionClass =
					Class.forName("sad.designsmell.detection.repository."
							+ antipatternName + '.' + antipatternName
							+ "Detection");
				final IDesignSmellDetection detection =
						(IDesignSmellDetection) detectionClass.newInstance();

				detection.detect(idiomLevelModel);

				final String path =
						anOutputDirectory + "DetectionResults-" + aName
								+ "-" + antipatternName + ".ini";
				detection.output(new PrintWriter(ProxyDisk
					.getInstance()
					.fileTempOutput(path)));

				final Properties properties = new Properties();
				properties.load(new ReaderInputStream(ProxyDisk
					.getInstance()
					.fileTempInput(path)));
				
				final OccurrenceBuilder solutionBuilder =
					OccurrenceBuilder.getInstance();
				final Occurrence[] solutions =
					solutionBuilder.getCanonicalOccurrences(properties);

				System.out.print(solutions.length);
				System.out.print(" solutions for ");
				System.out.print(antipatternName);
				System.out.print(" in ");
				System.out.print(aName);
				System.out.print(" in ");
				System.out.print(System.currentTimeMillis() - startTime);
				System.out.println(" ms.");
				
				
				for (int j = 0; j < solutions.length; j++) {
					final String csvLine = PtidejSmellDetection.getCSVLine(solutions[j], aSmell);
					
					smells.add(csvLine);
				}
				
			}
			catch (final Exception e) {
				e.printStackTrace(ProxyConsole.getInstance().errorOutput());
				throw new RuntimeException(e);
			}
			
			return smells;
		}
	
	public static final List<String> analyseCodeLevelModel(
		final String aSmell,
		final String aName,
		final ICodeLevelModel codeLevelModel,
		final String anOutputDirectory) {

		List<String> smells = new ArrayList<String>();
		
		try {
			final IIdiomLevelModel idiomLevelModel =
				(IIdiomLevelModel) new AACRelationshipsAnalysis()
					.invoke(codeLevelModel);

			smells = PtidejSmellDetection.analyseCodeLevelModel(
						aSmell,
						aName,
						idiomLevelModel,
						anOutputDirectory);
		}
		catch (final UnsupportedSourceModelException e) {
			e.printStackTrace(ProxyConsole.getInstance().errorOutput());
		}
		
		return smells;
	}
	
	
	
	public static final String getCSVLine(Occurrence occurence, String aSmell) {
		final List<?> occComponents = occurence.getComponents();
		final Iterator<?> iter = occComponents.iterator();
		Pattern largeClassPattern = Pattern.compile("LargeClass");
		Pattern controllerClassPattern = Pattern.compile("ControllerClass");
		
		final StringBuffer buffer = new StringBuffer();
		int count = 0;
		while (iter.hasNext()) {
			final OccurrenceComponent occ = (OccurrenceComponent) iter.next();
			final String name = occ.getDisplayName();
			final String value = occ.getDisplayValue();
			if (largeClassPattern.matcher(name).find()) {
				count++;
				if(count == 1) {
					buffer.append(value);
					buffer.append(";LargeClass;");
				}
				
				if (count == 2) {
					buffer.append(value);
					buffer.append(";");
				}
				if (count == 3) {
					Pattern boundPattern = Pattern.compile("\\D*(\\d+\\.\\d+)\\D*");
					Matcher m = boundPattern.matcher(value);
					
					if(m.matches()) {
						buffer.append(m.group(1));
					}
					return buffer.toString();
				}
			}
			
			if (controllerClassPattern.matcher(name).find()) {
				buffer.append(value);
				buffer.append(";ControllerClass;0;0");
				
				return buffer.toString();
			}
			
		}
		
		return null;
	}*/
	
}