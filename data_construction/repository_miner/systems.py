

# List of the systems that use Git as versionning system
systems_git = [
	{
	"name"     :'pmd', 
	"url"      :'https://github.com/pmd/pmd.git', 
	"snapshot" :'6063aaf', 
	"directory":['pmd/src/main/java/'],
	"sources"  :['pmd/src/main/java/']
	},
	{
	"name"     :'apache-log4j1', 
	"url"      :'https://github.com/apache/log4j.git',
	"snapshot" :'7cf64b6c9692e596193a0b11e38367721cf1c938',
	"directory":['src/java/'],
	"sources"  :['src/java/']
	},
	{
	"name"     :'apache-log4j2', 
	"url"      :'https://github.com/apache/log4j.git', 
	"snapshot" :'0663eb2a1301f7622f017496c5983789b1cbae38', 
	"directory":['src/java/'],
	"sources"  :['src/java/']
	},
	{
	"name"     :'mongodb', 
	"url"      :'https://github.com/mongodb/mongo-java-driver.git', 
	"snapshot" :'b67c0c43', 
	"directory":['src/main/'],
	"sources"  :['src/main/']
	},
	{
	"name"     :'apache-derby', 
	"url"      :'https://github.com/apache/derby.git', 
	"snapshot" :'c30c7da', 
	"directory":['java/engine/'],
	"sources"  :['java/engine/']
	},
	{
	"name"     :'junit', 
	"url"      :'https://github.com/junit-team/junit4.git', 
	"snapshot" :'751f75986b11336ac8310d73c89003b0b09ecb92', 
	"directory":['src/main/java/'],
	"sources"  :['src/main/java/']
	},
	{
	"name"     :'jgraphx', 
	"url"      :'https://github.com/jgraph/jgraphx.git', 
	"snapshot" :'25c9cfc539564de53d71a022815f3033630ba7c2', 
	"directory":['src/'],
	"sources"  :['src/']

	},
	{
	"name"     :'android-frameworks-opt-telephony', 
	"url"      :'https://android.googlesource.com/platform/frameworks/opt/telephony',
	"snapshot" :'c241cad754ecf27c96b09f1e585b8be341dfcb71',
	"directory":['src/java/'],
	"sources"  :['src/java/']
	},
	{
	"name"     :'android-platform-support',
	"url"      :'https://android.googlesource.com/platform/frameworks/support',
	"snapshot" :'38fc0cf9d7e38258009f1a053d35827e24563de6',
	"directory":['v4'],
	"sources"  :[
					'v4/eclair/',
					'v4/froyo/',
					'v4/gingerbread/',
					'v4/honeycomb/',
					'v4/honeycomb_mr2/',
					'v4/ics/',
					'v4/ics-mr1/',
					'v4/java/',
					'v4/jellybean/'
				]
	},
	{
	"name"     :'apache-ant', 
	"url"      :'https://git-wip-us.apache.org/repos/asf/ant.git', 
	"snapshot" :'e7734def8b0961af37c37eb1964a7e9ffdd052ca', 
	"directory":['src/main/'],
	"sources"  :['src/main/']
	},
	{
	"name"     :'apache-tomcat',
	"url"      :'https://github.com/apache/tomcat.git',
	"snapshot" :'398ca7ee',
	"directory":['java/org/'],
	"sources"  :['java/']

	},
	{
	"name"     :'lucene', 
	"url"      :'https://github.com/apache/lucene-solr.git', 
	"snapshot" :'39f6dc1', 
	"directory":['src/java/'],
	"sources"  :['src/java/']
	},
	{
	"name"     :'xerces-2_7_0', 
	"url"      :'https://github.com/apache/xerces2-j.git', 
	"snapshot" :'c986230', 
	"directory":['src/'],
	"sources"  :['src/']
	},
	{
	"name"     :'jspwiki', 
	"url"      :'https://github.com/apache/jspwiki.git', 
	"snapshot" :'a3b1041393db03d72d32e4d51554941be55e07e3', 
	"directory":['src/'],
	"sources"  :['src/']
	},
	{
	"name"     :'jgroups',
	"url"      :'https://github.com/belaban/JGroups.git',
	"snapshot" :'2d2ee7db9763c527a0228ba95dba433a2ea11972',
	"directory":['src/'],
	"sources"  :['src/']
	},
	{
	"name"     :'javacc',
	"url"      :'https://github.com/javacc/javacc.git',
	"snapshot" :'1b23b61777df9ccfe627682c848a07b3bf73387b',
	"directory":['src/main/java/'],
	"sources"  :['src/main/java/']
	},
	{
	"name"     :'apache-jena',
	"url"      :'https://github.com/apache/jena.git',
	"snapshot" :'dc0bfe6f0d32de82f711bc241e8f96e2be0a539d',
	"directory":['jena-core/src/main/java/'],
	"sources"  :['jena-core/src/main/java/']
	},
	{
	"name"     :'apache-velocity',
	"url"      :'https://github.com/apache/velocity-engine.git',
	"snapshot" :'23c979d3b185ace79c06fc7bedfcc1b9c232eb06',
	"directory":['src/java/'],
	"sources"  :['src/java/']
	}
]


# List of the systems that use SVN as versionning system.
# For these systems, you must first transform them into a git repository using "git svn" command.

#argouml version 0.15.6 : r5998 = bd70644e7afff38ba024a5db7c90e286623c2a49
#argouml version 0.19.8 : r9304 = 6edc166ff845cf9926bc7dbb70d93181471552c1
#argouml version 0.21.3 : r10701 = da60ec8e0fa5f40b5dde65226301f6ed810ebf98
#jHotDraw version 7.5.1 : r679 = 58d8df336c3c48a1943427754f6bbb6e991c2e41
systems_svn = [
	{
	"name"     :'jedit',
	"url"      :'https://svn.code.sf.net/p/jedit/svn/jEdit/trunk/',
	"snapshot" :'e343491b611efdd7a5313e7ba87d6a2d1d6f8804',
	"directory":[''],
	"sources"  :['']
	},
	{
	"name"     :'argouml', 
	"url"      :'http://argouml.stage.tigris.org/svn/argouml/trunk', 
	"snapshot" :'6edc166ff845cf9926bc7dbb70d93181471552c1', 
	"directory":['src_new/org/'],
	"sources"  :['src_new/']
	},
	{
	"name"     :'jhotdraw', 
	"url"      :'https://svn.code.sf.net/p/jhotdraw/svn/trunk', 
	"snapshot" :'58d8df336c3c48a1943427754f6bbb6e991c2e41', 
	"directory":['jhotdraw7/src/main/java/'],
	"sources"  :['jhotdraw7/src/main/java/']
	}
]