
from bs4 import BeautifulSoup
import requests
from BDWM import BDWM
import os
import sys
import subprocess 

#编写bat脚本，删除旧程序，运行新程序
def WriteRestartCmd(zip_name):
    base_path = ""
    if getattr(sys, 'frozen', False):  # 判断sys中是否存在frozen变量,
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(__file__)

    b = open("upgrade.bat",'w')
    TempList = "@echo off\n";                             # 关闭bat脚本的输出
    TempList += "timeout /t 3\n"                          # 等待3秒 方便覆盖旧程序（3秒后程序已运行结束，不延时的话，会提示被占用，无法覆盖）
    TempList += "copy /B "+ zip_name +" QJZPoster.zip\n"  # 合并所有分卷压缩文件
    TempList += "unzip -o QJZPoster.zip -x unzip.exe\n"   # 解压缩文件并覆盖
    TempList += "start QJZPoster.exe"                     # 启动新程序
    b.write(TempList)
    b.close()

    # 这里使用 start, windows下杀进程 subprocess 不能用 难过
    os.popen("start upgrade.bat")
    sys.exit()                                         # 进行升级，退出此程序

def main(bdwm,version):
    # url 为程序更新的精华区文件链接  权限控制靠BBS自带
    url = "https://bbs.pku.edu.cn/v2/collection-read.php?path=groups%2FGROUP_0%2FWMQJZ%2FDA7F65EA8%2FAA66D0FAC"
    response = bdwm._session.get(url)
    soup = BeautifulSoup(response.text, features="lxml")
    new_version = soup.select('.file-read p')[0].text
    if(new_version != version ):
        #下载所有附件
        attachment = soup.select('ul li a[target]')
        zip_all = ""
        for attach_url in attachment:
            #download 
            url = attach_url['href']
            r = bdwm._session.get(url)
            zip_all += "+"+attach_url.text
            with open(attach_url.text,'wb+') as f:
                f.write(r.content)
        zip_all = zip_all.lstrip("+") 
        
        version = new_version

        # 新程序启动时，删除旧程序制造的脚本
        if os.path.isfile("upgrade.bat"):
            os.remove("upgrade.bat")
        WriteRestartCmd(zip_all)