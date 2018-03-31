
'''
	List of the systems used for training, validation and test
'''


train = [
	{
	"name"     :'pmd', 
	"url"      :'https://github.com/pmd/pmd.git', 
	"snapshot" :'6063aaf', 
	"directory":'pmd/src/main/'
	},
	{
	"name"     :'apache-log4j1', 
	"url"      :'https://github.com/apache/log4j.git',
	"snapshot" :'7cf64b6c9692e596193a0b11e38367721cf1c938',
	"directory":'src/java/'
	},
	{
	"name"     :'apache-log4j2', 
	"url"      :'https://github.com/apache/log4j.git', 
	"snapshot" :'0663eb2a1301f7622f017496c5983789b1cbae38', 
	"directory":'src/java/'
	},
	{
	"name"     :'mongodb', 
	"url"      :'https://github.com/mongodb/mongo-java-driver.git', 
	"snapshot" :'b67c0c43', 
	"directory":'src/main'
	},
	{
	"name"     :'apache-derby', 
	"url"      :'https://github.com/apache/derby.git', 
	"snapshot" :'c30c7da', 
	"directory":'java/engine/'
	},
	{
	"name"     :'junit', 
	"url"      :'https://github.com/junit-team/junit4.git', 
	"snapshot" :'751f75986b11336ac8310d73c89003b0b09ecb92', 
	"directory":'src/main/java/'
	},
	{
	"name"     :'jgraphx', 
	"url"      :'https://github.com/jgraph/jgraphx.git', 
	"snapshot" :'25c9cfc539564de53d71a022815f3033630ba7c2', 
	"directory":'src/'
	}
]


test = [
	{
	"name"     :'android-frameworks-opt-telephony', 
	"url"      :'https://android.googlesource.com/platform/frameworks/opt/telephony',
	"snapshot" :'c241cad754ecf27c96b09f1e585b8be341dfcb71',
	"directory":'src/java/'
	},
	{
	"name"     :'android-platform-support',
	"url"      :'https://android.googlesource.com/platform/frameworks/support',
	"snapshot" :'38fc0cf9d7e38258009f1a053d35827e24563de6',
	"directory":'v4/java/'
	},
	{
	"name"     :'apache-ant', 
	"url"      :'https://git-wip-us.apache.org/repos/asf/ant.git', 
	"snapshot" :'e7734def8b0961af37c37eb1964a7e9ffdd052ca', 
	"directory":'src/main/'
	},
	{
	"name"     :'apache-tomcat',
	"url"      :'https://github.com/apache/tomcat.git',
	"snapshot" :'398ca7ee',
	"directory":'java/org/'
	},
	{
	"name"     :'lucene', 
	"url"      :'https://github.com/apache/lucene-solr.git', 
	"snapshot" :'39f6dc1', 
	"directory":'src/java/'
	},
	{
	"name"     :'xerces-2_7_0', 
	"url"      :'https://github.com/apache/xerces2-j.git', 
	"snapshot" :'c986230', 
	"directory":'src/'
	}
]


# List of the systems that uses Git as versionning system
systems_git = [
	{
	"name"     :'pmd', 
	"url"      :'https://github.com/pmd/pmd.git', 
	"snapshot" :'6063aaf', 
	"directory":['pmd/src/main/']
	},
	{
	"name"     :'apache-log4j1', 
	"url"      :'https://github.com/apache/log4j.git',
	"snapshot" :'7cf64b6c9692e596193a0b11e38367721cf1c938',
	"directory":['src/java/']
	},
	{
	"name"     :'apache-log4j2', 
	"url"      :'https://github.com/apache/log4j.git', 
	"snapshot" :'0663eb2a1301f7622f017496c5983789b1cbae38', 
	"directory":['src/java/']
	},
	{
	"name"     :'mongodb', 
	"url"      :'https://github.com/mongodb/mongo-java-driver.git', 
	"snapshot" :'b67c0c43', 
	"directory":['src/main']
	},
	{
	"name"     :'apache-derby', 
	"url"      :'https://github.com/apache/derby.git', 
	"snapshot" :'c30c7da', 
	"directory":['java/engine/']
	},
	{
	"name"     :'junit', 
	"url"      :'https://github.com/junit-team/junit4.git', 
	"snapshot" :'751f75986b11336ac8310d73c89003b0b09ecb92', 
	"directory":['src/main/java/']
	},
	{
	"name"     :'jgraphx', 
	"url"      :'https://github.com/jgraph/jgraphx.git', 
	"snapshot" :'25c9cfc539564de53d71a022815f3033630ba7c2', 
	"directory":['src/']
	},
	{
	"name"     :'android-frameworks-opt-telephony', 
	"url"      :'https://android.googlesource.com/platform/frameworks/opt/telephony',
	"snapshot" :'c241cad754ecf27c96b09f1e585b8be341dfcb71',
	"directory":['src/java/']
	},
	{
	"name"     :'android-platform-support',
	"url"      :'https://android.googlesource.com/platform/frameworks/support',
	"snapshot" :'38fc0cf9d7e38258009f1a053d35827e24563de6',
	"directory":['v4/java/']
	},
	{
	"name"     :'apache-ant', 
	"url"      :'https://git-wip-us.apache.org/repos/asf/ant.git', 
	"snapshot" :'e7734def8b0961af37c37eb1964a7e9ffdd052ca', 
	"directory":['src/main/']
	},
	{
	"name"     :'apache-tomcat',
	"url"      :'https://github.com/apache/tomcat.git',
	"snapshot" :'398ca7ee',
	"directory":['java/org/']
	},
	{
	"name"     :'lucene', 
	"url"      :'https://github.com/apache/lucene-solr.git', 
	"snapshot" :'39f6dc1', 
	"directory":['src/java/']
	},
	{
	"name"     :'xerces-2_7_0', 
	"url"      :'https://github.com/apache/xerces2-j.git', 
	"snapshot" :'c986230', 
	"directory":['src/']
	},
	{
	"name"     :'android-frameworks-sdk', 
	"url"      :'https://android.googlesource.com/platform/sdk', 
	"snapshot" :'04b07a76650a6ffd719c55f593b21fb1d92c84d2', 
	"directory":[
					'androidprefs/',
					'anttasks/',
					'archquery/',
					'assetstudio/src/',
					'attribute_stats/',
					'chimpchat/src/',
					'common/src/',
					'ddms/app/',
					'ddms/libs/ddmlib/src/',
					'ddms/libs/ddmuilib/src/',
					'draw9patch/',
					'dumpeventlog/',
					'eclipse/plugins/com.android.ide.eclipse.adt/',
					'eclipse/plugins/com.android.ide.eclipse.adt.ndk/',
					'eclipse/plugins/com.android.ide.eclipse.ddms/',
					'eclipse/plugins/com.android.ide.eclipse.gldebugger/',
					'eclipse/plugins/com.android.ide.eclipse.hierarchyviewer/',
					'eclipse/plugins/com.android.ide.eclipse.pdt/',
					'eclipse/plugins/com.android.ide.eclipse.traceview/',
					'eventanalyzer/',
					'hierarchyviewer/',
					'hierarchyviewer2/',
					'ide_common/src/',
					'layoutlib_api/',
					'layoutopt/',
					'monkeyrunner/src/',
					'ninepatch/src/',
					'rule_api/',
					'screenshot/',
					'sdklauncher/app/src/',
					'sdkmanager/app/src/',
					'sdkmanager/libs/sdklib/src/',
					'sdkmanager/libs/sdkuilib/src/',
					'sdkstats/',
					'swtmenubar/',
					'traceview/'
				]
	}
]


# List of the systems that uses SVN as versionning system.
# For these systems, you must first transform them into a git repository using "git svn" command.
# Put the obtained git repositories in the "./dataConstruction" directory and now you can do what you want.

#argouml version 0.15.6 : r5998 = bd70644e7afff38ba024a5db7c90e286623c2a49
#argouml version 0.19.8 : r9304 = 6edc166ff845cf9926bc7dbb70d93181471552c1
#argouml version 0.21.3 : r10701 = da60ec8e0fa5f40b5dde65226301f6ed810ebf98
systems_svn = [
	{
	"name"     :'jedit',
	"url"      :'https://svn.code.sf.net/p/jedit/svn/jEdit/trunk/',
	"snapshot" :'e343491b611efdd7a5313e7ba87d6a2d1d6f8804',
	"directory":['']
	},
	{
	"name"     :'argouml', 
	"url"      :'http://argouml.stage.tigris.org/svn/argouml/trunk', 
	"snapshot" :'6edc166ff845cf9926bc7dbb70d93181471552c1', 
	"directory":['src_new/']
	}
]


hist = [
	{
	"name"     :'jedit',
	"url"      :'https://svn.code.sf.net/p/jedit/svn/jEdit/trunk/',
	"snapshot" :'e343491b611efdd7a5313e7ba87d6a2d1d6f8804',
	"directory":['']
	},
	{
	"name"     :'argouml', 
	"url"      :'http://argouml.stage.tigris.org/svn/argouml/trunk', 
	"snapshot" :'6edc166ff845cf9926bc7dbb70d93181471552c1', 
	"directory":['src_new/']
	},
	{
	"name"     :'android-frameworks-opt-telephony', 
	"url"      :'https://android.googlesource.com/platform/frameworks/opt/telephony',
	"snapshot" :'c241cad754ecf27c96b09f1e585b8be341dfcb71',
	"directory":['src/java/']
	},
	{
	"name"     :'android-platform-support',
	"url"      :'https://android.googlesource.com/platform/frameworks/support',
	"snapshot" :'38fc0cf9d7e38258009f1a053d35827e24563de6',
	"directory":['v4/java/']
	},
	{
	"name"     :'apache-ant', 
	"url"      :'https://git-wip-us.apache.org/repos/asf/ant.git', 
	"snapshot" :'e7734def8b0961af37c37eb1964a7e9ffdd052ca', 
	"directory":['src/main/']
	},
	{
	"name"     :'apache-tomcat',
	"url"      :'https://github.com/apache/tomcat.git',
	"snapshot" :'398ca7ee',
	"directory":['java/org/']
	},
	{
	"name"     :'lucene', 
	"url"      :'https://github.com/apache/lucene-solr.git', 
	"snapshot" :'39f6dc1', 
	"directory":['src/java/']
	},
	{
	"name"     :'xerces-2_7_0', 
	"url"      :'https://github.com/apache/xerces2-j.git', 
	"snapshot" :'c986230', 
	"directory":['src/']
	},
	{
	"name"     :'android-frameworks-sdk', 
	"url"      :'https://android.googlesource.com/platform/sdk', 
	"snapshot" :'04b07a76650a6ffd719c55f593b21fb1d92c84d2', 
	"directory":[
					'androidprefs/',
					'anttasks/',
					'archquery/',
					'assetstudio/src/',
					'attribute_stats/',
					'chimpchat/src/',
					'common/src/',
					'ddms/app/',
					'ddms/libs/ddmlib/src/',
					'ddms/libs/ddmuilib/src/',
					'draw9patch/',
					'dumpeventlog/',
					'eclipse/plugins/com.android.ide.eclipse.adt/',
					'eclipse/plugins/com.android.ide.eclipse.adt.ndk/'
					'eclipse/plugins/com.android.ide.eclipse.ddms/',
					'eclipse/plugins/com.android.ide.eclipse.gldebugger/',
					'eclipse/plugins/com.android.ide.eclipse.hierarchyviewer/',
					'eclipse/plugins/com.android.ide.eclipse.pdt/',
					'eclipse/plugins/com.android.ide.eclipse.traceview/',
					'eventanalyzer/',
					'hierarchyviewer',
					'hierarchyviewer2',
					'ide_common/src/',
					'layoutlib_api/',
					'layoutopt/',
					'monkeyrunner/src/',
					'ninepatch/src/',
					'rule_api/',
					'screenshot/',
					'sdklauncher/app/src/',
					'sdkmanager/app/src/',
					'sdkmanager/libs/sdklib/src/',
					'sdkmanager/libs/sdkuilib/src/',
					'sdkstats/',
					'swtmenubar/',
					'traceview/'
				]
	}
]