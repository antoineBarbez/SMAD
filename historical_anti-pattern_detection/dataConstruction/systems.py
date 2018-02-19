
'''
	List of the systems used for training and validation
'''


systems = [
	{
	"name"     :'apache-commons-logging',
	"url"      :'https://github.com/apache/commons-logging.git',
	"snapshot" :'d821ed3e',
	"directory":''
	},
	{
	"name"     :'apache-commons-lang', 
	"url"      :'https://github.com/apache/commons-lang.git', 
	"snapshot" :'f957d81625a3aa70385f50d87f036ebe2c54613f', 
	"directory":''
	},
	{
	"name"     :'apache-commons-io', 
	"url"      :'https://github.com/apache/commons-io.git',
	"snapshot" :'99c5008d71b61f84a114038b064d58c837ee7ed6',
	"directory":''
	},
	{
	"name"     :'apache-commons-codec', 
	"url"      :'https://github.com/apache/commons-codec.git', 
	"snapshot" :'c6c8ae7a', 
	"directory":''
	},
	{
	"name"     :'google-guava1',
	"url"      :'https://github.com/google/guava.git',
	"snapshot" :'e8959ed0',
	"directory":''
	},
	{
	"name"     :'google-guava2', 
	"url"      :'https://github.com/google/guava.git', 
	"snapshot" :'e7c525b3310b07221b263ff48b3978d4ed54f811', 
	"directory":''
	},
	{
	"name"     :'android-frameworks-opt-telephony', 
	"url"      :'https://android.googlesource.com/platform/frameworks/opt/telephony',
	"snapshot" :'c241cad754ecf27c96b09f1e585b8be341dfcb71',
	"directory":''
	},
	{
	"name"     :'android-frameworks-sdk', 
	"url"      :'https://android.googlesource.com/platform/sdk', 
	"snapshot" :'04b07a76650a6ffd719c55f593b21fb1d92c84d2', 
	"directory":''
	},
	{
	"name"     :'android-platform-support',
	"url"      :'https://android.googlesource.com/platform/frameworks/support',
	"snapshot" :'38fc0cf9d7e38258009f1a053d35827e24563de6',
	"directory":''
	},
	{
	"name"     :'apache-ant', 
	"url"      :'https://git-wip-us.apache.org/repos/asf/ant.git', 
	"snapshot" :'e7734def8b0961af37c37eb1964a7e9ffdd052ca', 
	"directory":'src/main/'
	},
	{
	"name"     :'apache-log4j1', 
	"url"      :'https://github.com/apache/log4j.git',
	"snapshot" :'7cf64b6c9692e596193a0b11e38367721cf1c938',
	"directory":''
	},
	{
	"name"     :'apache-log4j2', 
	"url"      :'https://github.com/apache/log4j.git', 
	"snapshot" :'0663eb2a1301f7622f017496c5983789b1cbae38', 
	"directory":''
	},
	{
	"name"     :'apache-tomcat',
	"url"      :'https://github.com/apache/tomcat.git',
	"snapshot" :'398ca7ee',
	"directory":''
	},
	{
	"name"     :'mongodb', 
	"url"      :'https://github.com/mongodb/mongo-java-driver.git', 
	"snapshot" :'b67c0c43', 
	"directory":''
	},
	{
	"name"     :'apache-struts1', 
	"url"      :'https://github.com/apache/struts.git',
	"snapshot" :'9ad9404bfac2b936e1b5f0f5e828335bc5a51b48',
	"directory":'core/src/main/'
	},
	{
	"name"     :'apache-struts2', 
	"url"      :'https://github.com/apache/struts.git', 
	"snapshot" :'b9964b9e867c3d2512d087c87450601145a651c7', 
	"directory":'core/src/main/'
	},
	{
	"name"     :'apache-derby1', 
	"url"      :'https://github.com/apache/derby.git', 
	"snapshot" :'7a5b1d07853497727812cc9ada20209eea7b6a77', 
	"directory":''
	},
	{
	"name"     :'apache-derby2', 
	"url"      :'https://github.com/apache/derby.git', 
	"snapshot" :'fe8446d216a95529b9c165099b0d4d04c2c77be4', 
	"directory":''
	},
	{
	"name"     :'apache-cayenne1', 
	"url"      :'https://github.com/apache/cayenne.git', 
	"snapshot" :'fc5de25f422e7a8a9494a593638073215a752eae', 
	"directory":''
	},
	{
	"name"     :'apache-cayenne2', 
	"url"      :'https://github.com/apache/cayenne.git', 
	"snapshot" :'f820acff650eaa0325862efb89d316353501096f', 
	"directory":''
	},
	{
	"name"     :'junit1', 
	"url"      :'https://github.com/junit-team/junit4.git', 
	"snapshot" :'30f2b16525dabb477373be9ed3e76bb98b200806', 
	"directory":''
	},
	{
	"name"     :'junit2', 
	"url"      :'https://github.com/junit-team/junit4.git', 
	"snapshot" :'d9c908b9aab5f610e2f42aba1863ce25e36423f2', 
	"directory":''
	},
	{
	"name"     :'apache-tapestry1', 
	"url"      :'https://github.com/apache/tapestry4.git', 
	"snapshot" :'2f9be52a0001202f850a47e98a9f796759358ec8', 
	"directory":''
	},
	{
	"name"     :'apache-tapestry2', 
	"url"      :'https://github.com/apache/tapestry4.git', 
	"snapshot" :'fa9d5b3a416e60a70637a7f9c411070c517d26ca', 
	"directory":''
	},
	{
	"name"     :'cobertura1', 
	"url"      :'https://github.com/cobertura/cobertura.git', 
	"snapshot" :'0e90a9877baa84d9c9d3f4d025446eaac17fe3ad', 
	"directory":''
	},
	{
	"name"     :'cobertura2', 
	"url"      :'https://github.com/cobertura/cobertura.git', 
	"snapshot" :'7aa8877f03181e170ad638af2a3ad5e4fa68afa5', 
	"directory":''
	},
	{
	"name"     :'heritrix1', 
	"url"      :'https://github.com/internetarchive/heritrix3.git', 
	"snapshot" :'b2a0495a081c93b7f7dc5ad7f28e602134e5bf6e', 
	"directory":''
	},
	{
	"name"     :'heritrix2', 
	"url"      :'https://github.com/internetarchive/heritrix3.git', 
	"snapshot" :'18d459f6b9ebb732cda2c1d1f2ef9336e5a274dc', 
	"directory":''
	}
]