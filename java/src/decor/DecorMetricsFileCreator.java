import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;
import padl.analysis.UnsupportedSourceModelException;
import padl.analysis.repository.AACRelationshipsAnalysis;
import padl.creator.javafile.eclipse.CompleteJavaFileCreator;
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
import sad.codesmell.detection.repository.Blob.ControllerClassDetection;
import sad.codesmell.detection.repository.Blob.DataClassDetection;
import sad.kernel.ICodeSmell;
import sad.util.BoxPlot;
import util.io.ProxyConsole;
import org.apache.commons.lang.ArrayUtils;


public class DecorMetricsFileCreator {

	// The (csv) lines that compose the metrics file 
	private static List<String> metricsFileLines = new ArrayList<String>();
	
	public static void main(String[] args) throws IOException {
		String name;
		String repositoryPath;
		String[] dirsToAnalyze;
		String metricsFilePath;
		
		if (args.length < 3) {
			System.out.println("Too few arguments");
			return;
		}else if (args.length == 3) {
			// Happens when the directories to analyze are "",e.g, analyze all directories. 
			name = args[0];
			repositoryPath = args[1];
			dirsToAnalyze = new String[] {""};
			metricsFilePath = args[2];
		}else {
			name = args[0];
			repositoryPath = args[1];
			dirsToAnalyze = args[2].split("@", -1);
			metricsFilePath = args[3];
		}
		
		createMetricsFile(name, repositoryPath, dirsToAnalyze, metricsFilePath);
	}
	
	private static void createMetricsFile(
			String aName,
			String repositoryPath, 
			String[] dirsToAnalyze,
			String metricsFilePath) {

			System.out.println("Begin creating metrics file for " + aName + "...");
			String[] someSourcePaths = new String[dirsToAnalyze.length];
			for (int i=0;i<dirsToAnalyze.length;i++) {
				someSourcePaths[i] = repositoryPath + dirsToAnalyze[i];
			}

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

				
				analyse(codeLevelModel);
				
				//The Header ,e.g, the column names of the csv file.
				String firstLine = "ClassName;NMD+NAD;nmdNadBound;LCOM5;lcom5Bound;ControllerClass;nbDataClass";
				
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
	
	
	private static void analyse(final ICodeLevelModel codeLevelModel) {
			
			try {
				final IIdiomLevelModel idiomLevelModel =
					(IIdiomLevelModel) new AACRelationshipsAnalysis()
						.invoke(codeLevelModel);

				analyse(idiomLevelModel);
			}
			catch (final UnsupportedSourceModelException e) {
				e.printStackTrace(ProxyConsole.getInstance().errorOutput());
			}
		}
	
	private static void analyse(final IIdiomLevelModel idiomLevelModel) {
		final HashMap<String, String> boundsDictionnary = getBounds(idiomLevelModel);
		final Set dataClasses = getDataClasses(idiomLevelModel);
		final List<String> ccNames = getControllerClassesNames(idiomLevelModel);
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
				int nbDc = getNumberOfAssociatedDataClasses(firstClassEntity, dataClasses);
				
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

				metricsFileLines.add(buffer.toString());
			}
		}
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
}