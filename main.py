#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Create Time  : 2021/12/30 5:16 PM
# @Update Time  : 
# @Version      : V 0.1
# @File         : main.py
import time
from telnetlib import Telnet


def write_and_read(telnet_sess, write, read="error id=0 msg=ok"):
    write = write.encode('utf-8') + b"\n"
    read = read.encode('utf-8')
    telnet_sess.write(write)
    resp = telnet_sess.read_until(read, timeout=5).decode('utf-8')
    resp = [r for r in resp.split('\n\r') if r != '']
    return resp


def res_to_list_object(res):
    line_list = []
    for line in res:
        line_info = {}
        for r in line.split(' '):
            if r.find('=') != -1:
                line_info[r[:r.find('=')]] = r[r.find('=') + 1:].replace('\\s', ' ').replace('\\', '')
        line_list.append(line_info)
    return line_list


def res_to_dict(res):
    line_info = {}
    for r in res.split(' '):
        if r.find('=') != -1:
            line_info[r[:r.find('=')]] = r[r.find('=') + 1:].replace('\\s', ' ').replace('\\', '')
    return line_info


class TeamSpeak:
    """远程访问teamspeak"""

    def __init__(self, host, user, pwd, port=10011):
        # 配置选项
        self.host = host  # Telnet服务器IP
        self.port = port  # 通讯端口
        self.username = user  # 登录用户名
        self.password = pwd  # 登录密码
        self.telnet = None
        self.request_times = 0

    def check_telnet(self):
        if not self.telnet:
            self.connect()
        self.request_times += 1
        if self.request_times > 600:
            print('重连telnet')
            self.request_times = 0
            self.disconnect()
            time.sleep(3)
            self.connect()

    def connect(self):
        self.telnet = Telnet(self.host, self.port)
        if self.telnet:
            write_and_read(self.telnet, 'login %s %s' % (self.username, self.password))
            write_and_read(self.telnet, 'use 1')
            return True
        return False

    def disconnect(self):
        if self.telnet:
            write_and_read(self.telnet, 'quit')
            self.telnet.close()
        else:
            pass
    
    def restart(self):
        print('重连telnet')
        self.request_times = 0
        self.disconnect()
        time.sleep(3)
        self.connect()
    
    def create_token(self):
        self.check_telnet()
        res = write_and_read(self.telnet, 'tokenadd tokentype=0 tokenid1=6 tokenid2=0')[0]
        return res[res.find('=') + 1:]

    # 服务器信息
    def get_server(self):
        self.check_telnet()
        try:
            res = write_and_read(self.telnet, 'serverlist')[0]
        except Exception:
            self.restart()
            res = write_and_read(self.telnet, 'serverlist')[0]
        return res_to_dict(res)

    def read_server(self):
        self.check_telnet()
        res = write_and_read(self.telnet, 'serverinfo')[0]
        result = res_to_dict(res)
        if result.get('virtualserver_welcomemessage'):
            return result
        else:
            return None

    # 频道信息
    def get_channel(self):
        self.check_telnet()
        res = write_and_read(self.telnet, 'channellist')[0].split('|')
        return res_to_list_object(res)

    # 获取令牌
    def get_token(self):
        self.check_telnet()
        res = write_and_read(self.telnet, 'tokenlist')[0].split('|')
        return res_to_list_object(res)

    # 客户端信息
    def get_all_client(self):
        self.check_telnet()
        res = write_and_read(self.telnet, 'clientlist -info')[0].split('|')
        return res_to_list_object(res)

    def read_client(self, clid):
        self.check_telnet()
        res = write_and_read(self.telnet, 'clientinfo clid=%s' % clid)[0]
        return res_to_dict(res)

    def poke_client(self, clid, msg='戳一下'):
        self.check_telnet()
        res = write_and_read(self.telnet, 'clientpoke clid=%s msg=%s' % (clid, msg))[0]
        return res_to_dict(res)

    def kick_client(self, clid):
        self.check_telnet()
        res = write_and_read(self.telnet, 'clientkick clid=%s reasonid=5' % (clid))[0]
        return res_to_dict(res)

    def query(self, msg):
        self.check_telnet()
        res = write_and_read(self.telnet, msg)[0]
        res = res_to_dict(res)
        print(res)
        for k, v in res.items():
            print(k, v)

    def query_list(self, msg):
        self.check_telnet()
        res = write_and_read(self.telnet, msg)[0].split('|')
        res = res_to_list_object(res)
        print(res)
        for k, v in enumerate(res):
            print(k, v)
