#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
from BDWM import BDWM
import getpass
import os
import base64
import sys

#admin0-9 ABCG https://bbs.pku.edu.cn/v2/board.php?bid={xxx}
boards_bid=[
    "621",  #0区目录
    "664",  #1区目录
    "671",  #2区目录
    "673",  #3区目录
    "674",  #4区目录
    "675",  #5区目录
    "678",  #6区目录
    "679",  #7区目录
    "680",  #8区目录
    "681",  #9区目录
    "682",  #A区目录
    "683",  #B区目录
    "685",  #C区目录
    "686",  #D区目录
    "687",  #F区目录
    "688"   #G区目录
    ]

def get_decoded_password(file):
    """read password and decode it"""
    if not os.path.exists(file):
        return None
    with open(file, 'r') as f:
        encoded_password = f.read()
    return base64.b64decode(encoded_password.encode()).decode()

def write_encoded_password(password, file):
    """encode password and write it"""
    encoded_password = base64.b64encode(password.encode()).decode()
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, 'w') as f:
        f.write(encoded_password)


boardlists_dic = {"BBShelp":"0 0"}

#pyinstaller 打包时获取正确路径 支持py+exe
base_path = ""
if getattr(sys, 'frozen', False):  # 判断sys中是否存在frozen变量,
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(__file__)

#支持读取token
password_file = os.path.join(base_path, '.token', 'token')
password = get_decoded_password(password_file)
if not password:
    password = getpass.getpass("请输入WMWZ的密码(不会显示)：")
    # Store encoded password in a file, to avoid inputting password every time.
    write_encoded_password(password, password_file)

#登录WMWZ并建立session
try:
    bdwm = BDWM('WMWZ',password)
except BDWM.RequestError as e:
    # If failing to login, remove wrong password file.
    os.remove(password_file)
    raise e
        

## 使用高权限帐号获取所有版面目录
for i in range(0,len(boards_bid)):
    url = "https://bbs.pku.edu.cn/v2/board.php?bid="+boards_bid[i]
    response = bdwm._session.get(url)
    soup = BeautifulSoup(response.text, features="lxml")
    
    partition = ''
    if(i < 10):
        partition = chr(48+i)
    elif(i < 14):
        partition = chr(55+i)
    else:
        partition = chr(56+i)

    # class = left左边添加收藏夹/ class = upper 列表
    boardlists_engname = soup.select('.set .upper .eng-name') 
    for j in range(0,len(boardlists_engname)):
        boardlists_dic[boardlists_engname[j].text] = "{} 1".format(partition)

    print("正在添加{}区目录".format(partition))

## 使用游客帐号获取所有不登陆可见版面目录,并更新字典
for i in range(0,len(boards_bid)):
    url = "https://bbs.pku.edu.cn/v2/board.php?bid="+boards_bid[i]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="lxml")
    
    partition = ''
    if(i < 10):
        partition = chr(48+i)
    elif(i < 14):
        partition = chr(55+i)
    else:
        partition = chr(56+i)

    # class = left左边添加收藏夹/ class = upper 列表
    boardlists_engname = soup.select('.set .upper .eng-name') 
    for j in range(0,len(boardlists_engname)):
        boardlists_dic[boardlists_engname[j].text] ="{} 0".format(partition)
        
    print("{}区已更新完毕".format(partition))

# 格式 版名 分区 是否登录可见（0-游客可见 1-仅登录可见）
with open('boardlist.ans', 'w+', encoding='utf8') as f:
    for board in boardlists_dic:
        f.write(("{} {}\n").format(board,boardlists_dic[board]))
