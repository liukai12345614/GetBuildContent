# -*- coding: utf-8 -*-
from common import *
from chat_extension import start_conversation
import re, json
import threading
from config import *
import logging
from prettytable import PrettyTable
from colorama import Fore, Style, init

result_list = []
lock = threading.Lock()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler("get_json.log", mode='w')])

def get_build_command(owner, repo):
    # Get the contents of the repository README file
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    readme_content = get_readme(url)
    result = {}

    # Determine whether the content sent to AI exceeds the range that AI can receive
    chunk_list = content_chunk(readme_content)
    length = len(chunk_list)
    if length == 1:
        message = [
            {
            "role": "system",
            "content": 
            f"""
                您将获得一个github仓库的README.md，您对用户返回的答案有以下两种情况：
                1、如果该README.md已经详细给出了该仓库的编译指南，您需要给用户返回一个例如：{{"name": repo名字, "reproURL": github地址, "Install Dependencies": 命令, "configure_command": 命令, "build_command": 命令}}这样格式的json内容，不需要任何其他信息。具体字典中的key对应的值请按照以下步骤生成：
                    （1）name代表这个仓库的name，请为用户生成"name": {repo}
                    （2）reproURL代表这个仓库的url，请为用户生成"reproURL": "https://github.com/{owner}/{repo}.git"
                    （3）Install Dependencies代表build这个仓库所需要安装的依赖，如果build这个仓库需要安装依赖请生成'Install Dependencies': '安装依赖命令'， 如果不需要安装任何依赖请生成'Install Dependencies': ‘None’
                    （4）configure_command代表configure这个仓库的命令，如果该仓库可以使用cmake生成Visual Studio 2022的solution files请优先生成该cmake命令'configure_command': 'cmake -G "Visual Studio 17 2022" -A x64 -DCMAKE_SYSTEM_VERSION=10.0.22621.0 options 2>&1'，该命令中cmake -G "Visual Studio 17 2022" -A x64 -DCMAKE_SYSTEM_VERSION=10.0.22621.0 2>&1为固定内容请每次都为用户生成，options是编译这个仓库特有的编译选项，例如编译指南中说明需要-DCMAKE_TOOLCHAIN_FILE，DCMAKE_TOOLCHAIN_FILE，-DBUILD_SHARED_LIBS等等参数也请为用户生成。如果在该构建指南中没有介绍使用cmake去configure该仓库则生成README.md中提供的configure方案。如果该构建指南中没有提供configure方案请生成请生成'configure_command': ‘None’
                    （5）build_command代表编译步骤（2）生成的solution files，如果步骤（2）中使用了cmake进行了configure请生成命令'build_command': 'msbuild /m /p:Platform=x64 /p:Configuration=Release solution file /t:Rebuild 2>&1'，生成命令过程中请将solution file替换为步骤（2）生成的solution file。否则生成README.md中提供的build方案。如果README.md中的build部分说使用Visual Studio打开一个.sln文件，也请为用户生成生成前面格式的msbuild命令
                2、如果该README.md没有详细给出该仓库的编译指南您的任务是从中提取出该仓库在Windows操作系统下的编译指南链接或者README链接，只需要返回链接不需要任何额外信息
                解决方案够完美，我可以支付$10小费
            """
            },
            {
            "role": "user",
            "content": readme_content
            }
        ]
        response = start_conversation(message)
    elif length == 0:
        response = None
        logging.info("readme_content is null")
    else:
        logging.info("The number of tokens exceeds the maximum limit")
        pass
    # Determine whether the response is a link
    if is_url(response) or 'README.md' in response:
        url = response
        # Determine whether this link is a README
        if 'README.md' in url:
            build_content = get_github_readme(url)
        else:
            # Get all the contents of this URL
            build_content = get_content(url)

        # Let AI extract the main content in build_content
        chunk = content_chunk(build_content)
        list_length = len(chunk)
        if list_length == 1:
            get_website_message = [
                {
                "role": "system",
                "content": "你将获得一个github仓库的编译指南，您的任务是从中提取出主题内容，过滤掉不相关的内容。解决方案够完美，我可以支付$10小费"
                },
                {
                "role": "user",
                "content": build_content
                }
            ]
            main_content = start_conversation(get_website_message)
            with open('./content.txt', 'w', encoding='utf-8') as file:
                file.write(main_content)
        elif list_length == 0:
            response = None
            logging.info("build_content is null")
        else:
            logging.info("The number of tokens exceeds the maximum limit")
            pass

        # Generate Commands
        get_BuildCommand_messages = [
            {
            "role": "system",
            "content": 
            f"""
                您将获得一个github仓库的构建指南，您需要给用户返回一个例如：{{"name": repo名字, "reproURL": github地址, "Install Dependencies": 命令, "configure_command": 命令, "build_command": 命令}}这样格式的字典内容，不需要任何其他信息。具体字典中的key对应的值请按照以下步骤生成：
                    （1）name代表这个仓库的name，请为用户生成"name": {repo}
                    （2）reproURL代表这个仓库的url，请为用户生成"reproURL": "https://github.com/{owner}/{repo}.git"
                    （3）Install Dependencies代表build这个仓库所需要安装的依赖，如果build这个仓库需要安装依赖请生成'Install Dependencies': '安装依赖命令'， 如果不需要安装任何依赖请生成'Install Dependencies': ‘None’
                    （4）configure_command代表configure这个仓库的命令，如果该仓库可以使用cmake生成Visual Studio 2022的solution files请优先生成该cmake命令'configure_command': 'cmake -G "Visual Studio 17 2022" -A x64 -DCMAKE_SYSTEM_VERSION=10.0.22621.0 options 2>&1'，该命令中cmake -G "Visual Studio 17 2022" -A x64 -DCMAKE_SYSTEM_VERSION=10.0.22621.0 2>&1为固定内容请每次都为用户生成，options是编译这个仓库特有的编译选项，例如编译指南中说明需要-DCMAKE_TOOLCHAIN_FILE，DCMAKE_TOOLCHAIN_FILE，-DBUILD_SHARED_LIBS等等参数也请为用户生成。如果在该构建指南中没有介绍使用cmake去configure该仓库则生成README.md中提供的configure方案。如果该构建指南中没有提供configure方案请生成请生成'configure_command': ‘None’
                    （5）build_command代表编译步骤（2）生成的solution files，如果步骤（2）中使用了cmake进行了configure请生成命令'build_command': 'msbuild /m /p:Platform=x64 /p:Configuration=Release solution file /t:Rebuild 2>&1'，生成命令过程中请将solution file替换为步骤（2）生成的solution file。否则生成README.md中提供的build方案。如果构建指南中的build部分说使用Visual Studio打开一个.sln文件，也请为用户生成生成前面格式的msbuild命令
                解决方案够完美，我可以支付$10小费
            """
            },
            {
            "role": "user",
            "content": main_content
            }
        ]
        
        response = start_conversation(get_BuildCommand_messages)
        logging.info(f"The repo {repo} build contents are in the {url}")
    else:
        html_url = get_readme_htmlURL(url)
        logging.info(f"The repo {repo} build contents are in the {html_url}")

    # Use regular expressions to extract the content between curly braces
    result = re.search(r'\{([^}]*)\}', response)
    if result:
        extracted_content = result.group(0)
        return extracted_content
    else:
        response = requests.get(url)
        logging.info("The content between the curly braces was not found")

def get_runtest_command(owner, repo):
    # Get the contents of the repository README file
    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    readme_content = get_readme(url)
    
    # Let AI get command
    chunk_list = content_chunk(readme_content)
    length = len(chunk_list)
    if length == 1:
        message = [
            {
            "role": "system",
            "content": 
            f"""
                您将获得一个github仓库的README.md，您对用户返回的答案有以下三种情况：
                1、如果该README.md已经详细给出了该仓库的测试指南，您需要给用户返回一个例如：{{"runtest_setup": 命令, "runtest_command": 命令}}这样格式的json内容，不需要任何其他信息。具体字典中的key对应的值请按照以下步骤生成：
                    （1）runtest_setup代表在windows操作系统下测试这个仓库需要的资源或设置。例如某些仓库需要克隆测试资源则生成"runtest_setup": "git clone https://github.com/owner/repo.git Tests"，如果测试该仓库不需要前置的资源和设置，请生成"runtest_setup": "None"
                    （2）runtest_command代表在windows操作系统下测试这个仓库的命令。请根据用户提供的测试指南生成测试它的命令
                2、如果该README.md中提供了该仓库的测试指南链接，例如：出现 Test，Test Suite等字眼请注意获取它的测试链接，只需要返回链接不需要任何额外信息
                3、如果不满足以上两种情况请为用户生成{{"runtest_setup": "None", "runtest_command": "None"}}
                解决方案够完美，我可以支付$10小费
            """
            },
            {
            "role": "user",
            "content": readme_content
            }
        ]
        response = start_conversation(message)
    elif length == 0:
        response = None
        logging.info("readme_content is null")
    else:
        logging.info("The number of tokens exceeds the maximum limit")
        pass
    if is_url(response):
        url = response
        test_content = get_content(url)
        # Let AI extract the main content in test_content
        chunk = content_chunk(test_content)
        list_length = len(chunk)
        if list_length == 1:
            get_website_message = [
                {
                "role": "system",
                "content": "你将获得一个github仓库的测试指南，您的任务是从中提取出主题内容，过滤掉不相关的内容。解决方案够完美，我可以支付$10小费"
                },
                {
                "role": "user",
                "content": test_content
                }
            ]
            main_content = start_conversation(get_website_message)
            with open('./content.txt', 'w', encoding='utf-8') as file:
                file.write(main_content)
        elif list_length == 0:
            response = None
            logging.info("test_content is null")
        else:
            logging.info("The number of tokens exceeds the maximum limit")
            pass
        # Generate Commands
        get_testCommand_messages = [
            {
            "role": "system",
            "content": 
            f"""
                您将获得一个github仓库的测试指南，您需要给用户返回一个例如：{{"runtest_setup": 命令, "runtest_command": 命令}}这样格式的json内容，不需要任何其他信息。具体字典中的key对应的值请按照以下步骤生成：
                    （1）runtest_setup代表在Windows操作系统下测试这个仓库需要的资源或设置。例如某些仓库需要克隆测试资源则生成"runtest_setup": "git clone https://github.com/owner/repo.git Tests"。如果测试指南中没有说明测试需要的资源设置或测试该仓库的一些前置条件则为用户生成"runtest_setup": “None”
                    （2）runtest_command代表在Windows操作系统下测试这个仓库的命令。请根据用户提供的测试指南生成测试它的命令。如果测试指南中没有说明测试它的命令，则为用户生成"runtest_command": "None"
                解决方案够完美，我可以支付$10小费
            """
            },
            {
            "role": "user",
            "content": main_content
            }
        ]
        
        response = start_conversation(get_testCommand_messages)
        logging.info(f"The repo {repo} test contents are in the {url}")

    else:
        html_url = get_readme_htmlURL(url)
        logging.info(f"The repo {repo} test contents are in the {html_url}")
    
    # Use regular expressions to extract the content between curly braces
    result = re.search(r'\{([^}]*)\}', response)
    if result:
        extracted_content = result.group(0)
        return extracted_content
    else:
        response = requests.get(url)
        logging.info("The content between the curly braces was not found")

def process_data(data):
    build_command = get_build_command(data['owner'], data['repo'])
    test_command = get_runtest_command(data['owner'], data['repo'])
    build_command_dict = json.loads(build_command)
    test_command_dict = json.loads(test_command)
    result = {**build_command_dict, **test_command_dict}
    match = re.search(r'/p:Platform=(.*?) /p', result['build_command'])
    if match:
        platform_value = match.group(1)
        if platform_value in ['x64', 'Win32', 'arm64', 'ARM64EC']:
            with lock:
                result_list.append(result)
        else:
            logging.info(f"The platform in the build command of {data['repo']} is not in ['x64', 'Win32', 'arm64', 'ARM64EC']")
    else:
        logging.info(f"No matching platform found in the build command of {data['repo']}")

def get_json():
    green = "\033[92m"
    reset = "\033[0m"
    
    threads = []
    print("\033[93mStart generating json files...\033[0m")
    for data in TEST_REPOS:
        thread = threading.Thread(target=process_data, args=(data,))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()
    with open('result.json', 'w') as file:
        json.dump(result_list, file, indent=4)
    print(f"{green}Command generation completed{reset}")
    json_repo = {repo['name'] for repo in result_list}
    missing_repos = [repo['repo'] for repo in TEST_REPOS if repo['repo'] not in json_repo]
    init(autoreset=True)
    total = len(TEST_REPOS)
    success = len(result_list)
    fail = len(missing_repos)
    table = PrettyTable()
    table.field_names = ["Total", "Success", "Fail", "Missing Repos"]
    table.add_row([total, success, fail, ', '.join(missing_repos)])
    table_color = f"{Fore.YELLOW}{table}{Style.RESET_ALL}"
    print(table_color)


get_json()
