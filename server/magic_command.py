# -*- coding: utf-8 -*-
# @Time    : 2020/2/15 17:57
# @Author  : wangH
# @Email   :
# @File    : magic_command.py

import sys


def ask_yes_no(question):
    """Ask a yes/no question via input() and return their answer.
    """
    valid = {"yes": True, "y": True, "no": False, "n": False}
    prompt = " [y/n] "

    while True:
        print(question + prompt)
        choice = input().lower()
        if choice in valid:
            answer = valid[choice]
            print(answer)
            return answer
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' ('y' or 'n').\n")


def read_requirements():
    with open('requirements.txt') as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    return [element for element in content if len(element) > 1]


def zip_dir():
    print('这是打包用户模型的代码')


def push_to_git():
    print('这是推送到 git 的代码')


def k8s_apply():
    print('这是调用 k8s client 运行 yaml 的代码')


def query_pod_status():
    print('这是调用 k8s client 查询运行状态的代码')
    return 'running'
    # return 'successful'
    # return 'failed'


def query_log_all_step():
    print('这是返回所有步骤的运行日志的代码')


def query_log_only_model():
    print('这是返回用户模型运行日志的代码')


if __name__ == '__main__':
    STEP1   = "STEP1: <<=== 您是否已经检查确定您的输入输出路径 ===>>"
    STEP2_1 = "STEP2: <<======== 您是否需要安装 %s ======>>"
    STEP2_2 = "STEP2: <<========== 无需要安装的第三方包 ==========>>"
    STEP3   = "STEP3: <<============ 正在打包您的模型 ============>>"
    # STEP4 = "STEP4: <<============= 推送到git仓库 ==============>>"
    # STEP5 = "STEP5: <<============= 从git仓库拉取 ==============>>"  # Tekton step（source fed）
    STEP4   = "STEP4: <<=============== 模型运行中 ===============>>"  # Tekton step（python run）
    STEP5   = "STEP5: <<====== 当前运行状态（间隔10秒查询）： =====>>"  # 查询大POD的状态即可
    STEP6_1 = "STEP6: <<===== 模型运行出错，是否查看运行日志 =====>>"  # 给所有步骤的日志(pod namespace list)
    STEP6_2 = "STEP6: <<===== 模型运行结束，是否查看运行日志 =====>>"  # 给模型运行步骤的日志
    STEP7   = "STEP7: <<=== 如有需要，验证您的模型的文件写结果 ===>>"
    NEED_PIP_INSTALL = False

    # STEP1
    if ask_yes_no(STEP1):
        want_to_install = read_requirements()
        # STEP2
        if len(want_to_install) > 0:
            NEED_PIP_INSTALL = ask_yes_no(STEP2_1.replace('%s', ','.join(want_to_install)))
        else:
            print(STEP2_2)
        # STEP3
        print(STEP3)
        zip_dir()
        push_to_git()
        # STEP4
        print(STEP4)
        k8s_apply()
        # STEP5 TODO:
        #  https://stackoverflow.com/questions/474528/what-is-the-best-way-to-repeatedly-execute-a-function-every-x-seconds-in-python
        print(STEP5)
        pod_status = query_pod_status()
        print(pod_status)
        # STEP6
        if pod_status == 'failed':
            if ask_yes_no(STEP6_1):
                query_log_all_step()
        else:
            if ask_yes_no(STEP6_2):
                query_log_only_model()
        # STEP7
        print(STEP7)
        print('GOODBYE!')
    else:
        exit()
