# -*- coding:utf-8 -*-
from model import Job, query_by_city
from pyecharts import options as opts
from pyecharts.charts import Bar


# 数据统计类
class Summary():
    def __init__(self, city):
        self.city = city
        self.total_count = 0
        self.min_salary = 1000
        self.max_salary = 0
        self.avg = None
        self.avg_sum = 0
        self.min_avg = None
        self.min_sum = 0
        self.max_avg = None
        self.max_sum = 0
        self.datalist = []


# 数据统计函数
def get_summary_info(sum_obj):
    """
    @type sum_obj:Summary
    """
    joblist = query_by_city(sum_obj.city)
    """
    @type joblist:list[Job]
    """
    for job_obj in joblist:
        salary_str = job_obj.salary
        min_salary = int(salary_str.split("-")[0].replace("k", ""))
        max_salary = int(salary_str.split("-")[1].replace("k", ""))

        if  min_salary < sum_obj.min_salary:
            sum_obj.min_salary = min_salary
        if  max_salary > sum_obj.max_salary:
            sum_obj.max_salary = max_salary

        avg_salary = (min_salary + max_salary) / 2
        sum_obj.avg_sum += avg_salary
        sum_obj.min_sum += min_salary
        sum_obj.max_sum += max_salary

    sum_obj.total_count = len(joblist)
    sum_obj.avg = int(sum_obj.avg_sum / sum_obj.total_count)
    sum_obj.min_avg = int(sum_obj.min_sum / sum_obj.total_count)
    sum_obj.max_avg = int(sum_obj.max_sum / sum_obj.total_count)


if __name__ == '__main__':
    summary_list = []
    for city in ['北京', '上海', '广州', '深圳']:
        summary_list.append(Summary(city))

    # 用于绘图的数据字典
    data_dict_a = {}
    data_dict_b = {
        "最低工资": [],
        "地位数平均工资": [],
        "平均工资": [],
        "高位数平均工资": [],
        "最高工资": []
    }

    # 根据不同城市进行数据统计
    for sum_obj in summary_list:
        get_summary_info(sum_obj)
        print(f'{sum_obj.city} 最低工资：{sum_obj.min_salary}k，最高工资：{sum_obj.max_salary}k，'
              f'平均工资：{sum_obj.avg}k，样本数量：{sum_obj.total_count}')
        data_dict_a[sum_obj.city] = [sum_obj.min_salary, sum_obj.min_avg, sum_obj.avg, sum_obj.max_avg,
                                     sum_obj.max_salary]
        data_dict_b['最低工资'].append(sum_obj.min_salary)
        data_dict_b['地位数平均工资'].append(sum_obj.min_avg)
        data_dict_b['平均工资'].append(sum_obj.avg)
        data_dict_b['高位数平均工资'].append(sum_obj.max_avg)
        data_dict_b['最高工资'].append(sum_obj.max_salary)

    # 以工资指标横坐标 绘图
    a = (
        Bar().add_xaxis(["最低工资", "低位数平均工资", "平均工资", "高位数平均工资", "最高工资"])
            .add_yaxis('北京', data_dict_a['北京'])
            .add_yaxis('上海', data_dict_a['上海'])
            .add_yaxis('广州', data_dict_a['广州'])
            .add_yaxis('深圳', data_dict_a['深圳'])
            .set_global_opts(title_opts=opts.TitleOpts(title='工资水平统计', subtitle='职位：Python工程师，单位：k'))

    )
    a.render("./a.html")

    # 以城市作为横坐标 绘图
    b = (
        Bar().add_xaxis(["北京", "上海", "广州", "深圳"])
            .add_yaxis('最低工资', data_dict_b['最低工资'])
            .add_yaxis('地位数平均工资', data_dict_b['地位数平均工资'])
            .add_yaxis('平均工资', data_dict_b['平均工资'])
            .add_yaxis('高位数平均工资', data_dict_b['高位数平均工资'])
            .add_yaxis('最高工资', data_dict_b['最高工资'])
            .set_global_opts(title_opts=opts.TitleOpts(title='工资水平统计', subtitle='职位：Python工程师，单位：k'))

    )
    b.render("./b.html")
