# coding=UTF-8
"""
 Copyright (c) 2024 Alexander-Porter & fwilliamhe

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program. If not, see <https://www.gnu.org/licenses/>.
 """

import os
import sys
import ctypes
import atexit
import signal
import requests
import requests.packages

from certmgr import certmgr
from hostmgr import hostmgr
from proxymgr import proxymgr
from envmgr import genv


m_certmgr = None
m_hostmgr = None
m_proxy = None

def handle_exit():
    print("[main] 再见!")
    if m_hostmgr != None:
        m_hostmgr.remove(genv.get("URI_TARGET"))
    os.system("pause")

def initialize() :
    # if we don't have enough privileges, relaunch as administrator
    if ctypes.windll.shell32.IsUserAnAdmin() == 0:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

    # initialize the global vars at first
    genv.set("URI_TARGET", "service.mkey.163.com")
    genv.set("FP_WORKDIR", os.path.join(os.environ['PROGRAMDATA'], 'idv-login'))    
    genv.set("FP_WEBCERT", os.path.join(genv.get("FP_WORKDIR"),"domain_cert.pem"))
    genv.set("FP_WEBKEY",  os.path.join(genv.get("FP_WORKDIR"),"domain_key.pem"))
    genv.set("FP_CACERT",  os.path.join(genv.get("FP_WORKDIR"),"root_ca.pem"))

    # handle exit
    atexit.register(handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    signal.signal(signal.SIGINT, handle_exit)

    # initialize object
    global m_certmgr, m_hostmgr, m_proxy
    m_certmgr = certmgr()
    m_hostmgr = hostmgr()
    m_proxy = proxymgr()
    
    # initialize workpath
    if not os.path.exists(genv.get("FP_WORKDIR")):
        os.mkdir(genv.get("FP_WORKDIR"))
    os.chdir(os.path.join(genv.get("FP_WORKDIR")))
    print(f"[main] 已将工作目录设置为 -> {genv.get("FP_WORKDIR")}")

    # disable warnings for requests
    requests.packages.urllib3.disable_warnings()

def welcome() :
    print("[+] 欢迎使用第五人格登陆助手 version 5.0.0-stable")
    print(" - 官方项目地址 : https://github.com/Alexander-Porter/idv-login/")
    print(" - 如果你的这个工具不能用了，请前往仓库检查是否有新版本发布或加群询问！")
    print(" - 本程序使用GNU GPLv3协议开源， 严禁将本程序用于任何商业行为！")
    print(" - This program is free software: you can redistribute it and/or modify")
    print(" - it under the terms of the GNU General Public License as published by")
    print(" - the Free Software Foundation, either version 3 of the License, or")
    print(" - (at your option) any later version.")

if __name__ == '__main__':

    welcome()
    initialize()

    if (os.path.exists(genv.get("FP_WEBCERT")) == False) or (os.path.exists(genv.get("FP_WEBKEY")) == False):
        print("[main] 正在生成必要的证书文件...")
        
        ca_key  = m_certmgr.generate_private_key(bits=2048)
        ca_cert = m_certmgr.generate_ca(ca_key)
        m_certmgr.export_cert(genv.get("FP_CACERT"), ca_cert)

        srv_key = m_certmgr.generate_private_key(bits=2048)
        srv_cert = m_certmgr.generate_cert(genv.get("URI_TARGET"), srv_key, ca_cert, ca_key)

        if (m_certmgr.import_to_root(genv.get("FP_CACERT")) == False) : 
            print("[main] 导入CA证书失败!")
            os.system("pause")
            sys.exit(-1)
        
        m_certmgr.export_cert(genv.get("FP_WEBCERT"), srv_cert)
        m_certmgr.export_key(genv.get("FP_WEBKEY"), srv_key)
        print("[main] 初始化成功!")

    print("[main] 正在重定向目标地址到本机...")

    m_hostmgr.add(genv.get("URI_TARGET"), "127.0.0.1")

    print("[main] 正在启动代理服务器...")

    if (m_proxy.run() == False) :
        print("[main] 启动代理服务器失败!")
        sys.exit()