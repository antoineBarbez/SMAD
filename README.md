# SMAD (SMart Aggregation of Anti-patterns Detectors)
A machine-learning based ensemble method to aggregate various anti-patterns detection approaches on the basis of their 
internal detection rules and, thus, improve detection performances.

SMAD is implemented for the detection of **God Class** and **Feature Envy**.

## Repository Structure
This repository is organized as follows:
* **approaches:** Source code of all the approaches implemented in this work, including the replication of HIST, InCode, Vote, ASCI as well as the Tensorflow code of the NN used by our approach SMAD.
* **data:** Contains necessary data to run the experiments.
  * **antipatterns:** The oracle, i.e., manually-tagged occurrences of God Class and Feature Envy in eight software systems.
  * **entities:** Names of classes and methods in all the systems considered in this study (classes_all includes nested classes).
  * **history:** Change history of the subject systems at class and method granularity.
  * **metric_files:** Files containing the *core metrics* related to each detection tool to be aggregated. Note that for HIST, these core metrics are computed from the system's history.
* **data_construction:** Code used to generate the data.
  * **oracle_feature_envy:** To create the data contained in *~/data/antipatterns/feature_envy/* from the answers collected via our survey.
  * **repository_miner:** To mine systems' repository and create the rest of the data.
* **experiments:** The source code of our experiments: training, comparison, parameter tuning, etc.
* **java:** Jars and src of the Java code implemented in this work. These jars are used in *~/data_construction/repository_miner/repository_miner.py* to create the metric files.
* **utils:** Modules used to access and manipulate the data.

## Research
The paper associated to this repository is under review at *Journal of Systems and Software*.

  


  
