# -*- coding:utf-8 -*-
import random
import threading
import time
import json
import sys
import re
import os
import getopt
import socket
from queue import Queue
from netaddr import IPNetwork, IPRange

port_start = 1
port_end = 8000
lock = threading.Lock()
portQueue = Queue()  # 存放解析数据的queue
ping_result = {
    "ping_pass": [],
    "ping_fail": []
}
tcp_result = {}
flag = False


# 自定义输入错误
class InputError(BaseException):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        print(self.message)
        return ("输入参数有误，使用方法示例：pmap.py -n 4 -f ping -ip 192.168.0.1-192.168.0.100")


class PingThread(threading.Thread):
    '''
    爬虫类
    '''

    def __init__(self, thread_id, queue):
        super().__init__()
        self.thread_id = thread_id
        self.queue = queue

    def run(self):
        '''
        重写run方法
        '''
        # print(f'启动ping线程：{self.thread_id}')
        self.ping_check()
        # print(f'结束ping线程：{self.thread_id}')

    # ping 检测
    def ping_check(self):
        while True:
            if self.queue.empty():  # 队列为空不处理
                break
            else:
                ipaddr = self.queue.get()
                backinfo = os.system('ping -w 2 -n 1 %s >nul' % ipaddr)
                lock.acquire()
                if backinfo == 0:
                    ping_result['ping_pass'].append(ipaddr)
                    print(f"ping {ipaddr} pass")
                else:
                    ping_result['ping_fail'].append(ipaddr)
                    # print(f"ping {ipaddr} fail")
                lock.release()
                if backinfo == 0:
                    for port in range(port_start, port_end + 1):
                        portQueue.put((ipaddr, port))


# socket 检测端口
class TcpThread(threading.Thread):
    '''
    端口检测任务
    '''

    def __init__(self, thread_id, queue):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.queue = queue

    def run(self):
        # print(f'启动tcp线程：{self.thread_id}')
        while True:
            try:
                item = self.queue.get(False)  # 参数为false（非阻塞）时队列为空，抛出异常
                if item is None:
                    # print(f'结束tcp线程：{self.thread_id}')
                    break
                ipaddr = item[0]
                ipport = item[1]

                self.scan_port(ipaddr, ipport)
                self.queue.task_done()  # get之后检测是否会阻塞
            except Exception as e:
                pass
            time.sleep(0.5)

    def scan_port(self, ipaddr, port):
        try:
            res = socket.create_connection((ipaddr, port), timeout=3)
            res.close()
            print("%s - %d port is open" % (ipaddr, port))
            status = True
        except socket.error as e:
            status = False
        lock.acquire()
        if status:
            if ipaddr not in tcp_result:
                tcp_result[ipaddr] = {"open_port": []}
            tcp_result[ipaddr]["open_port"].append(port)
        lock.release()


# Getopt参数类
class Getopt_pmap:
    def __init__(self, argv):
        try:
            # 参数注册
            opts, args = getopt.getopt(argv, "hn:f:i:w:v", ["help", "ip="])
            print(f"parsed argv: opts----{opts} args----{args}")
        except getopt.GetoptError:
            # 参数不符合注册格式要求报错
            print("parameter format error")
            raise InputError("-h，--help查看使用说明")

        self.thread_number = None
        self.scan_mode = None
        self.display_spend = False
        self.ipaddr_str = None
        self.output_file = None
        self.ipaddr_list = []

        for opt, arg in opts:
            # -h与--help等价
            if opt in ("-h", "--help"):
                raise InputError("-h，--help查看使用说明")
            # -n 并发参数
            elif opt in ("-n"):
                self.thread_number = arg
            # -f 检测模式
            elif opt in ("-f"):
                self.scan_mode = arg
            # ip地址参数
            elif opt in ("-i", "--ip"):
                self.ipaddr_str = arg
            # 时间显示参数
            elif opt in ("-v"):
                self.display_spend = True
            # 输出json
            elif opt in ("-w"):
                self.output_file = arg
        print(f"thread number is {self.thread_number}, scan mode is {self.scan_mode}"
              f" ，ip address is {self.ipaddr_str}, display spend is {self.display_spend}, output is {self.output_file}!")


# IP地址合法性检查
def check_ip(ipAddr):
    compile_ip = re.compile(
        '^(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|[1-9])\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)\.(1\d{2}|2[0-4]\d|25[0-5]|[1-9]\d|\d)$')
    if compile_ip.match(ipAddr):
        return True
    else:
        return False


# 参数合理性检查
def check_param(getopt_obj):
    """
    @type getopt_obj:Getopt_pmap
    """
    try:
        int(getopt_obj.thread_number)
    except:
        raise InputError("并发参数错误")
    if getopt_obj.scan_mode != "ping" and getopt_obj.scan_mode != "tcp":
        raise InputError("检测参数错误")
    ip_list = []
    ip_str = getopt_obj.ipaddr_str
    if ip_str.find("-") != -1:
        startip = ip_str.split("-")[0]
        endip = ip_str.split("-")[1]
        if not (check_ip(startip) and check_ip(endip)):
            raise InputError("ip地址参数错误")
        iprange_cidrs = IPRange(startip, endip)
        for net_cidr in iprange_cidrs.cidrs():
            for ip in net_cidr.iter_hosts():
                ip_list.append(str(ip))
    elif ip_str.find("/") != -1:
        try:
            for ip in IPNetwork(ip_str):
                ip_list.append(str(ip))
        except:
            raise InputError("ip地址参数错误")
    else:
        if not check_ip(ip_str):
            raise InputError("ip地址参数错误")
        ip_list.append(ip_str)
    getopt_obj.ipaddr_list = ip_list


if __name__ == '__main__':
    # 参数检查
    argv = sys.argv[1:]
    param_obj = Getopt_pmap(argv)
    check_param(param_obj)

    # 参数读取
    start_time = time.time()
    ip_list = param_obj.ipaddr_list
    thread_num = int(param_obj.thread_number)

    # 将IP地址放入ping队列
    thread_list = []
    print(f'共要检测{len(ip_list)}个ip地址')
    pingQueue = Queue()
    for ipaddr in ip_list:
        pingQueue.put(ipaddr)
    print("---------------检测开始------------------")

    # ping线程
    ping_threads = []
    for thread_id in range(thread_num):
        thread = PingThread(thread_id, pingQueue)
        thread.start()
        ping_threads.append(thread)

    # tcp线程
    tcp_threads = []
    if param_obj.scan_mode == 'tcp':
        for thread_id in range(thread_num):
            thread = TcpThread(thread_id, portQueue)
            thread.start()
            tcp_threads.append(thread)

    # 结束ping线程，ping检查结束后在TCP队列最后加上结束标志
    for t in ping_threads:
        t.join()
    for i in range(thread_num):
        portQueue.put(None)

    # 结束tcp线程
    if param_obj.scan_mode == 'tcp':
        for t in tcp_threads:
            t.join()

    # 列表重新排序
    ping_result['ping_pass'] = sorted(ping_result['ping_pass'])
    ping_result['ping_fail'] = sorted(ping_result['ping_fail'])
    for ipaddr, port_dict in tcp_result.items():
        port_dict["open_port"] = sorted(port_dict["open_port"])

    # 输出结果
    end_time = time.time()
    print("---------------检测结果------------------")
    if param_obj.display_spend:
        print(f'检测共耗时：{round(end_time - start_time, 2)} 秒')
    print(f"ping 通过的地址列表：{ping_result['ping_pass']}")
    if param_obj.scan_mode == "tcp":
        print(tcp_result)
    if param_obj.output_file is not None:
        with open(param_obj.output_file, 'w') as f:
            json.dump(ping_result, f)
            json.dump(tcp_result, f)
