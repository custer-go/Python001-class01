# -*- coding:utf-8 -*-
from sqlalchemy import Column, Integer, String, Table, MetaData, DateTime, Sequence
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

engine = create_engine('mysql://spider:mydb999@localhost:3306/spider?charset=utf8', echo=False)
DBSession = sessionmaker(bind=engine, autoflush=True)


class Job(Base):
    # 表的名字:
    __tablename__ = 't_jobs'

    # 表的结构:
    id = Column(Integer, Sequence("job_id_seq"), primary_key=True)
    positionId = Column(String(20))
    positionName = Column(String(512))  # "Python 后台研发工程师",
    companyId = Column(String(20))  # 327797,
    companyFullName = Column(String(512))  # "广州影子科技有限公司",
    companyShortName = Column(String(128))  # "影子科技",
    companyLogo = Column(String(256))  # "i/image/M00/89/F0/CgpFT1rhb6SADouVAAAkwtEBuhY828.png",
    companySize = Column(String(64))  # "150-500人",
    industryField = Column(String(128))  # "企业服务,数据服务",
    companyLabelList = Column(String(256))  # "年底双薪", "交通补助", "通讯津贴",  "带薪年假"
    firstType = Column(String(256))  # "开发|测试|运维类",
    secondType = Column(String(256))  # "后端开发",
    thirdType = Column(String(256))  # "Python",
    skillLables = Column(String(256))  # ["Python",   "docker" ],
    positionLables = Column(String(256))  # "Python",  "docker"
    createTime = Column(DateTime)  # "2020-07-08 11:57:58",
    city = Column(String(32))  # "深圳",
    district = Column(String(32))  # "南山区",
    salary = Column(String(32))  # "20k-35k",
    salaryMonth = Column(String(32))  # "16",
    workYear = Column(String(32))  # "5-10年",
    jobNature = Column(String(32))  # "全职",
    education = Column(String(32))  # "本科",
    positionAdvantage = Column(String(128))  # "16薪、产业互联网、团队福利好、加班少",


def check_exsit(positionId):
    dbsession = DBSession()
    result = dbsession.query(Job).filter(Job.positionId == positionId).first()
    dbsession.close()
    if result is None:
        return False
    else:
        return True


def add_job(jobinfo):
    obj = Job()
    obj.positionId = jobinfo['positionId']
    obj.positionName = jobinfo['positionName']
    obj.companyId = jobinfo['companyId']
    obj.companyFullName = jobinfo['companyFullName']
    obj.companyShortName = jobinfo['companyShortName']
    obj.companyLogo = jobinfo['companyLogo']
    obj.companySize = jobinfo['companySize']
    obj.industryField = jobinfo['industryField']
    obj.companyLabelList = str(jobinfo['companyLabelList'])
    obj.firstType = jobinfo['firstType']
    obj.secondType = jobinfo['secondType']
    obj.thirdType = jobinfo['thirdType']
    obj.skillLables = str(jobinfo['skillLables'])
    obj.positionLables = str(jobinfo['positionLables'])
    obj.createTime = jobinfo['createTime']
    obj.city = jobinfo['city']
    obj.district = jobinfo['district']
    obj.salary = jobinfo['salary']
    obj.salaryMonth = jobinfo['salaryMonth']
    obj.workYear = jobinfo['workYear']
    obj.jobNature = jobinfo['jobNature']
    obj.education = jobinfo['education']
    obj.positionAdvantage = jobinfo['positionAdvantage']
    dbsession = DBSession()
    dbsession.add(obj)
    dbsession.commit()
    dbsession.close()


def query_by_city(city):
    dbsession = DBSession()
    result = dbsession.query(Job).filter(Job.jobNature.notin_(("实习","兼职"))). \
        filter(Job.city == city).all()
    dbsession.close()
    return result


if __name__ == "__main__":
    engine = create_engine('mysql://spider:mydb999@localhost:3306/spider?charset=utf8', echo=True)
    Base.metadata.create_all(engine)
    dbsession = DBSession()
    positionId = '7407606'
    print(check_exsit(positionId))
