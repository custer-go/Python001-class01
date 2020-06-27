# 使用 BeautifulSoup 解析网页


import requests
from bs4 import BeautifulSoup as bs
# bs4是第三方库需要使用pip命令安装
import pandas as pd

headers = {
    'Cookie': '__mta=251551033.1593240787318.1593241664647.1593242261454.3; uuid_n_v=v1; uuid=DB006550B84211EA974289B279A7041DF9A17B5DE9994A698A932AABDAE3B0D9; _lxsdk_cuid=172f48d17aac8-0df6b09750e74f-4353760-240000-172f48d17aac8; _lxsdk=DB006550B84211EA974289B279A7041DF9A17B5DE9994A698A932AABDAE3B0D9; mojo-uuid=11f6ebaa1c8548dd8b7a8a1922dad2e9; mojo-session-id={"id":"4129f6b9bbd65deab8a8352b7559854b","time":1593244871299}; _csrf=53c3b4745a99c0c8308a35214795513e1d5aa60b41a4cdd519ddbe5f7aa9d499; lt=uUMpqdis4aVqsAZpJa5KDEVd1U8AAAAA5woAAKhMDVSliegR0vxjNISpsniW_UJVKIWHobzubonhVActYV13RNmtdl-U0etZqcBX3A; lt.sig=XH827rWZav4l7HmpB0rseLOUzfs; mojo-trace-id=7; __mta=251551033.1593240787318.1593242261454.1593245116594.4; _lxsdk_s=172f4cb6b34-623-fd8-90%7C%7C13',
    # 加入cookie解决猫眼反爬
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
}
# 定义要爬取的网址
myurl = 'https://maoyan.com/films?showType=3'

response = requests.get(myurl, headers=headers)

bs_info = bs(response.text, 'html.parser')

movies = []

count = 10

# Python 中使用 for in 形式的循环，Python 使用缩进来做语句块分隔
for tags in bs_info.find_all('div', attrs={'class': 'movie-hover-info'}):
    if count > 0:
        movie_name = tags.find('span', attrs={'class': 'name'}).text
        hover_tags = tags.find_all('span', attrs={'class': 'hover-tag'})
        movie_type = hover_tags[0].next_sibling.strip()
        plan_date = hover_tags[2].next_sibling.strip()
        movies.append([movie_name, movie_type, plan_date])
        # for atag in tags.find_all('div'):
        # print(atag.find('span').text)
        # print(atag.find('span').next_sibling.strip())
        count -= 1

pd.DataFrame(data=movies).to_csv('./movie.csv', encoding='utf8', index=False, header=False)
