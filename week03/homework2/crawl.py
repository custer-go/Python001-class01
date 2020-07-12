# -*- coding:utf-8 -*-
import requests
import random
import threading
import time
from requests.cookies import RequestsCookieJar
from queue import Queue
from model import Job, add_job, check_exsit
from selenium import webdriver


class CrawlThread(threading.Thread):
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
        print(f'启动线程：{self.thread_id}')
        self.scheduler()
        print(f'结束线程：{self.thread_id}')

    # 模拟任务调度
    def scheduler(self):
        while True:
            time.sleep(random.randint(1, 5))
            if self.queue.empty():  # 队列为空不处理
                break
            else:
                city, page, web_obj = self.queue.get()
                # 设置城市标志
                city_flag = "0"
                if city == "北京":
                    city_flag = "2"
                elif city == "上海":
                    city_flag = "3"
                elif city == "广州":
                    city_flag = "213"
                elif city == "深圳":
                    city_flag = "215"
                print(f'下载线程为：{self.thread_id}, 城市：{city}，下载页面： {page}')
                # downloader 下载器
                try:
                    # 先访问一下城市职位页面，这样才能访问一次接口，不然会被拒绝
                    web_obj.format_params(page, city_flag, city)
                    web_obj.browser.get(web_obj.homepage)
                    time.sleep(0.5)
                    web_obj.browser.get(web_obj.prepost_url)
                    time.sleep(0.2)
                    # 访问接口获取详细信息
                    data = web_obj.http_session.post(web_obj.job_url, params=web_obj.params, cookies=web_obj.cookies)
                    print(data.text)
                    time.sleep(0.2)
                    dataQueue.put(data.json())
                except Exception as e:
                    print('下载出现异常', e)
            # 限制访问速度，不然会被拒绝
            time.sleep(random.randint(1, 5))


class ParserThread(threading.Thread):
    '''
    页面内容分析
    '''

    def __init__(self, thread_id, queue):
        threading.Thread.__init__(self)
        self.thread_id = thread_id
        self.queue = queue

    def run(self):
        print(f'启动线程：{self.thread_id}')
        while not flag:
            try:
                item = self.queue.get(False)  # 参数为false时队列为空，抛出异常
                if not item:
                    pass
                self.parse_data(item)
                self.queue.task_done()  # get之后检测是否会阻塞
            except Exception as e:
                pass
        print(f'结束线程：{self.thread_id}')

    def parse_data(self, item):
        '''
        解析网页内容的函数
        :param item:
        :return:
        '''
        # 检测格式是否在正常
        if not isinstance(item, dict):
            return
        jsondata = item
        try:
            # 组个对象保存到数据库
            for jobinfo in jsondata['content']['positionResult']['result']:
                if check_exsit(jobinfo['positionId']):
                    continue
                else:
                    print(f'新增记录：{jobinfo}')
                add_job(jobinfo)
        except Exception as e:
            print('job error', e)


# 自定义web类，内含浏览器和requests session
class MyWeb():
    def __init__(self, username, password):
        self.browser = webdriver.Chrome()
        self.http_session = requests.session()
        self.username = username
        self.password = password
        self.prepost_url = ""
        self.job_url = ""
        self.cookies = None
        self.homepage = 'https://www.lagou.com/jobs/list_Python/p-city_0?px=default#filterBox'

    def format_params(self, page, city_flag, city):
        self.http_session.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            "Referer": f"https://www.lagou.com/jobs/list_Python?city={city_flag}&gm=&jd=&px=default",
            "origin": "https://www.lagou.com",
            "accept": "application/json, text/javascript, */*; q=0.01"
        }
        self.prepost_url = f"https://www.lagou.com/jobs/list_Python/p-city_{city_flag}?px=default#filterBox"
        self.job_url = f'https://www.lagou.com/jobs/positionAjax.json?px=default&city={city}&needAddtionalResult=false'
        self.params = {
            'pn': str(page),
            'kd': 'Python'
        }

    # 开启浏览器，登录并获取token
    def web_login(self):
        # 开启浏览器
        self.browser.get('https://lagou.com')
        time.sleep(5)

        # 登录
        loginbutton = self.browser.find_element_by_xpath('//*[@id="lg_tbar"]/div/div[2]/ul/li[3]/a')
        loginbutton.click()

        self.browser.find_element_by_xpath(
            '/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[1]/div/div[1]/form/div[1]/div/input').send_keys(
            self.username)
        self.browser.find_element_by_xpath(
            '/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[1]/div/div[1]/form/div[2]/div/input').send_keys(
            self.password)
        # time.sleep(3)
        # self.browser.find_element_by_xpath('/html/body/div[2]/div[1]/div/div/div[2]/div[3]/div[2]/div[2]/div[2]').click()

        # time.sleep(20)
        # 等待手动图形验证
        input("确认验证完毕")
        seleuium_cookies = self.browser.get_cookies()

        # 转换cookies格式
        cookies = RequestsCookieJar()
        for cookie in seleuium_cookies:
            cookies.set(cookie['name'], cookie['value'])
        self.cookies = cookies

    def close(self):
        self.browser.close()


dataQueue = Queue()  # 存放解析数据的queue
flag = False

if __name__ == '__main__':
    # 线程锁
    # 获取cookies
    web_obj1 = MyWeb("user1", "passwd1")
    web_obj2 = MyWeb("user2", "passwd2")

    # 实例化web对象, 进行登录操作
    web_obj1.web_login()
    web_obj2.web_login()

    print("开始爬虫")

    # 任务队列，存放网页的队列
    pageQueue = Queue(100)
    for page in range(1, 16):
        pageQueue.put(("北京", page, web_obj1))
        pageQueue.put(("上海", page, web_obj2))
        pageQueue.put(("广州", page, web_obj1))
        pageQueue.put(("深圳", page, web_obj2))

    # 爬虫线程
    crawl_threads = []
    crawl_name_list = ['crawl_1', 'crawl_2']
    for thread_id in crawl_name_list:
        thread = CrawlThread(thread_id, pageQueue)
        thread.start()
        crawl_threads.append(thread)

    # 解析线程
    parse_thread = []
    parser_name_list = ['parse_1', 'parse_2', 'parse_3']
    for thread_id in parser_name_list:
        thread = ParserThread(thread_id, dataQueue)
        thread.start()
        parse_thread.append(thread)

    # 结束crawl线程
    for t in crawl_threads:
        t.join()

    # 结束parse线程
    flag = True
    for t in parse_thread:
        t.join()

    web_obj1.close()
    web_obj2.close()
    print('退出主线程')
