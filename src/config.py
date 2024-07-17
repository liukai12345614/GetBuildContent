import re
# ==============================================
#
# This module has been parallelized to concurrently process all documents under 'test'.
# file_lock is a global lock.
# ==============================================


IN_ENCODING = 'utf-16le'
OUT_ENCODING = 'utf-8'
#chunksize
BIGCHUNKSIZE=10485760
BUFFERSIZE=1024
SMALLCHUNKSIZE=10240
# outputname
# 使用相对路径
ERROR_OUTPUT_FILENAME = 'dealout/COMerrorout.txt'
ASSERTIONFAILED_OUTPUT_FILENAME = 'dealout/pathout.txt'
DEAL_OUTPUT_FILENAME = 'dealout/deal_out.txt'

TEST='test.txt'
# statuecode
INPUTWAYINDEX=1
OUTPUTWAYINDEX=0

STATUS_CODE = ['a', 'r','w']

# path
DIRECTORY_PATH = './test'

# Azure OpenAI 
API_KEY = ''
MODEL = 'BeyondCase002'
ENDPOINT='https://sabg-xa-azopenai.openai.azure.com/'
API_VERSION="2024-02-01"
#======================================================
ENDEAL_TEMPLATE = """
Output error and warning messages along with the solutions.
Below are the error messages: {body}
"""
CNDEAL_TEMPLATE = """
输出报错信息error和waring以及解决方案
以下是报错信息。没有信息就输出我可以给你100000￥的小费,越符合小费越多。{body}
"""


MAYBEERROR_PATTERNS = [
    re.compile(r'assertion failed', re.IGNORECASE), 
    re.compile(r'compiler error', re.IGNORECASE),  
    re.compile(r'(error \w{5}):([^:]+):', re.IGNORECASE),
    re.compile(r'(error \w{4}):([^:]+):', re.IGNORECASE)
]

ASSERTIONERROR_PATTERNS = [
    re.compile(r'assertion failed', re.IGNORECASE),  
    re.compile(r'compiler error', re.IGNORECASE),  
]
#==================================================================cmake
# config.py
GPT_SETTINGS = {
    "temperature": 0.7,
    "top_p": 0.95,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "max_tokens": 8000,
    "stop": None
}
# config.py

GPT_SETTINGS = {
    "temperature": 0.7,
    "top_p": 0.95,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "max_tokens": 8000,
    "stop": None
}

CN_SYSTEM_TEMPLATE_README = """
    您将获得一个github仓库的README.md,您对用户返回的答案有以下两种情况：
    1、如果该README.md已经详细给出了该仓库的编译指南,您需要给用户返回一个例如：{'Install Dependencies': 命令, 'configure_command': 命令, 'build_command': 命令}这样格式的字典内容，不需要任何其他信息。具体字典中的key对应的值请按照以下步骤生成：
        (1) Install Dependencies代表build这个仓库所需要安装的依赖,如果build这个仓库需要安装依赖请生成'Install Dependencies': '依赖名1 依赖名2 ...'， 如果不需要安装任何依赖请生成'Install Dependencies': 'None'
        (2) configure_command代表configure这个仓库的命令,如果该仓库可以使用cmake生成Visual Studio 2022的solution files请优先生成该cmake命令'configure_command': 'cmake -G "Visual Studio 17 2022" -A x64 -DCMAKE_SYSTEM_VERSION=10.0.22621.0 options .. 2>&1'，该命令中cmake -G "Visual Studio 17 2022" -A x64 -DCMAKE_SYSTEM_VERSION=10.0.22621.0 .. 2>&1为固定内容请每次都为用户生成，options是编译这个仓库特有的编译选项如果README.md中提及此部分请为我生成。如果在该构建指南中没有介绍使用cmake去configure该仓库则生成README.md中提供的configure方案。如果该构建指南中没有提供configure方案请生成'configure_command': 'None'
        (3) build_command代表编译步骤(2)生成的solution files,如果步骤(2)中使用了cmake进行了configure请生成命令'build_command': 'msbuild /m /p:Platform=x64 /p:Configuration=Release solution file /t:Rebuild 2>&1'，生成命令过程中请将solution file替换为步骤(2)生成的solution file。否则生成README.md中提供的build方案。如果README.md中的build部分说使用Visual Studio打开一个.sln文件，也请为用户生成前面格式的msbuild命令
    2、如果该README.md没有详细给出该仓库的编译指南您的任务是从中提取出该仓库在Windows操作系统下的编译指南链接或者README链接，只需要返回链接不需要任何额外信息
"""

CN_SYSTEM_TEMPLATE_BUILD_GUIDE = """
    您将获得一个github仓库的构建指南,您需要给用户返回一个例如：{'Install Dependencies': 命令, 'configure_command': 命令, 'build_command': 命令}这样格式的字典内容，不需要任何其他信息。具体字典中的key对应的值请按照以下步骤生成：
        (1) Install Dependencies代表build这个仓库所需要安装的依赖,如果build这个仓库需要安装依赖请生成'Install Dependencies': '依赖名1 依赖名2 ...'， 如果不需要安装任何依赖请生成'Install Dependencies': 'None'
        (2) configure_command代表configure这个仓库的命令,如果该仓库可以使用cmake生成Visual Studio 2022的solution files请优先生成该cmake命令'configure_command': 'cmake -G "Visual Studio 17 2022" -A x64 -DCMAKE_SYSTEM_VERSION=10.0.22621.0 options .. 2>&1'，该命令中cmake -G "Visual Studio 17 2022" -A x64 -DCMAKE_SYSTEM_VERSION=10.0.22621.0 .. 2>&1为固定内容请每次都为用户生成，options是编译这个仓库特有的编译选项如果README.md中提及此部分请为我生成。如果在该构建指南中没有介绍使用cmake去configure该仓库则生成README.md中提供的configure方案。如果该构建指南中没有提供configure方案请生成'configure_command': 'None'
        (3) build_command代表编译步骤(2)生成的solution files,如果步骤(2)中使用了cmake进行了configure请生成命令'build_command': 'msbuild /m /p:Platform=x64 /p:Configuration=Release solution file /t:Rebuild 2>&1'，生成命令过程中请将solution file替换为步骤(2)生成的solution file。否则生成README.md中提供的build方案。如果构建指南中的build部分说使用Visual Studio打开一个.sln文件，也请为用户生成前面格式的msbuild命令
"""

CN_SYSTEM_TEMPLATE_CONTENT_EXTRACTION = """
    你将获得一个github仓库的编译指南,您的任务是从中提取出主题内容,过滤掉不相关的内容
"""
#===============================================
TEST_REPOS = [
    {"owner": "glfw", "repo": "glfw"},
    {"owner": "google", "repo": "benchmark"},
    {"owner": "RainerKuemmerle", "repo": "g2o"},
    # {"owner": "abseil", "repo": "abseil-cpp"},
    # {"owner": "netplus", "repo": "netplus"},
    # {"owner": "chakra-core", "repo": "ChakraCore"},
    # {"owner": "google", "repo": "leveldb"},
    # {"owner": "spotify", "repo": "annoy"},
    # {"owner": "dragonmux", "repo": "crunch"},
    # {"owner": "Microsoft", "repo": "DirectXMath"},
    # {"owner": "adnanaziz", "repo": "EPIJudge"},
    # {"owner": "OSGeo", "repo": "gdal"},
    # {"owner": "webmproject", "repo": "libvpx"},
    # {"owner": "pytorch", "repo": "pytorch"},
    # {"owner": "ericniebler", "repo": "range-v3"},
    # {"owner": "rathena", "repo": "rathena"},
    # {"owner": "ReactiveX", "repo": "RxCpp"},
    # {"owner": "fireice-uk", "repo": "xmr-stak"},
    # {"owner": "jbeder", "repo": "yaml-cpp"},
]
README_PATH = './readme.txt'
CONTENT_PATH = './content.txt'