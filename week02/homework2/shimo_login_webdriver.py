# -*- coding: utf-8 -*-
from selenium import webdriver
import time

try:
    browser = webdriver.Chrome()

    browser.get('https://shimo.im/welcome')
    time.sleep(1)

    # 浏览器复制的 XPATH 参考 //*[@id="homepage-header"]/nav/div[3]/a[2]/button
    btm1 = browser.find_element_by_xpath('//*[@class="login-button btn_hover_style_8"]')  # 登陆的 class 属性 login-button btn_hover_style_8
    btm1.click()

    # 浏览器复制的 XPATH 参考 //*[@id="root"]/div/div[2]/div/div/div/div[2]/div/div/div[1]/div[1]/div/input
    browser.find_element_by_xpath('//*[@name="mobileOrEmail"]').send_keys('13666666666')
    # 浏览器复制的 XPATH 参考 //*[@id="root"]/div/div[2]/div/div/div/div[2]/div/div/div[1]/div[2]/div/input
    browser.find_element_by_xpath('//*[@name="password"]').send_keys('password')
    # 账号和密码替换成不真实的数据
    time.sleep(1)

    browser.find_element_by_xpath('//*[@class="sm-button submit sc-1n784rm-0 bcuuIb"]').click() # 登陆的 class 属性 sm-button submit sc-1n784rm-0 bcuuIb  type=black
    time.sleep(3)

except Exception as e:
    print(e)
finally:
    browser.close()
