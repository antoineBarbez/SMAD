
# List of the systems that use Git as versionning system
systems_git = [
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
	}
]