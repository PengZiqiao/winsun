import json
import os
from argparse import ArgumentParser

from lxml import etree
from winsun.utils import Spider
from winsun.database.model import MonthBook, MonthSale, MonthSold, WeekBook, WeekSale, WeekSold
from winsun.database.model import Session, MianjiDuan, DanjiaDuan, ZongjiaDuan, TaoXing
from winsun.database.query import str2date
from winsun.tools import GisSpider

path = 'E:/gisDataBase'


# def load(filename):
#     """打开json文件"""
#     with open(f'{path}/{filename}.json', 'r') as f:
#         # return json.load(f)
#         obj = f.read().encode('utf-8').decode('unicode-escape')
#         obj = obj.replace('é\x94\x98ç¸\x96', '[')
#         return json.loads(obj)


def jiegou(by):
    """用于生成“面积段”、“单价段”、“总价段”的表"""
    arg = {
        '面积段': (MianjiDuan, 'acreage', 'mjd'),
        '单价段': (DanjiaDuan, 'aveprice', 'djd'),
        '总价段': (ZongjiaDuan, 'tprice', 'zjd')
    }[by]

    if by == '面积段':
        name, name_, m = 'acreage', 'mjd', MianjiDuan()
    elif by == '单价段':
        name, name_, m = 'aveprice', 'djd', DanjiaDuan()
    elif by == '总价段':
        name, name_, m = 'tprice', 'zjd', ZongjiaDuan()

    low, high = f'{name}_low', f'{name}_high'
    label_, low_, high_ = f'{name_}_label', f'{name_}_low', f'{name_}_high'

    s = Session()
    obj = load(name)

    for rec in obj:
        m.id = rec['id']
        exec(f'm.{label_} = rec[by]')
        exec(f'm.{low_} = rec[low]')
        exec(f'm.{high_} = rec[high]')
        print(m)
        s.add(m)

    s.commit()


def type():
    """用于生成套型表"""

    s = Session()
    obj = load('type')

    for rec in obj:
        m = TaoXing()
        m.id = rec['id']
        m.tx_name = rec['套型']
        print(m)
        s.add(m)

    s.commit()


def market(obj, by):
    """用于生成周月报表"""
    obj.reverse()

    model = {
        'month_book': MonthBook,
        'month_sale': MonthSale,
        'month_sold': MonthSold,
        'week_book': WeekBook,
        'week_sale': WeekSale,
        'week_sold': WeekSold
    }[by]
    s = Session()

    for rec in obj:
        m = model()
        m.id = int(rec['id'])
        m.dist = rec['区属']
        m.plate = rec['板块']
        m.zone = rec['片区']
        m.usage = rec['功能']
        m.set = rec['件数']
        m.space = rec['面积']
        m.price = rec['均价']
        m.money = rec['金额']
        m.mjd_id = rec['面积段']
        m.djd_id = rec['单价段']
        m.zjd_id = rec['总价段']
        m.taoxing_id = rec['套型']
        m.proj_id = rec['prjid']
        m.proj_name = rec['projectname']
        m.pop_name = rec['popularizename']
        m.permit_id = rec['permitid']
        m.permit_no = rec['permitno']
        m.permit_date = str2date(rec['perdate'])
        m.update_time = rec['update_time']
        m.presaleid = rec['presaleid']
        if 'month' in by:
            m.date = str2date(rec['年月'])
        else:
            m.week = rec['星期']
            m.start = str2date(rec['start_date'])
            m.end = str2date(rec['end_date'])
        s.merge(m)
    s.commit()


def init_db():
    """根据文件夹内json文件初始化数据库"""

    # 生成三张结构
    for by in ['面积段', '单价段', '总价段']:
        jiegou(by)

    # 套型
    type()

    # 将周月报表json文件遍历打开后填入数据库。
    walk = list(list(os.walk(path)))[1:]
    for path_, _, files in walk:
        by = path_.split('\\')[1]
        for file in files:
            print(by, file)
            obj = load(f"{by}/{file.replace('.json','')}")
            market(obj, by)


# TODO:有空改写GIS爬虫，尽量用requests代替selenium
class GisAPI:
    def __init__(self):
        self.path = 'E:/gisDataBase'

        # 通过selenium登陆gis
        g = GisSpider()
        self.driver = g.driver
        self.wait = g.wait

        self.wait.until(lambda driver: driver.find_element_by_link_text("更改密码"))

        # 获得日期选项
        self.driver.get('http://winsun.house365.com/sys/dataout')
        self.wait.until(lambda driver: driver.find_element_by_name("m2"))
        tree = etree.HTML(self.driver.page_source)
        self.week_option = tree.xpath("//select[@name='w2']/option/@value")
        self.month_option = tree.xpath("//select[@name='m2']/option/@value")

    def get(self, **kwargs):
        # 取得json
        url = 'http://winsun.house365.com/sys/dataout/data'
        for i, each in enumerate(kwargs):
            arg = f'{each}={kwargs[each]}'
            if i == 0:
                url += f'?{arg}'
            else:
                url += f'&{arg}'
        self.driver.get(url)
        self.wait.until(lambda driver: driver.find_element_by_xpath("//pre"))
        tree = etree.HTML(self.driver.page_source)
        return tree.xpath("//pre/text()")[0]

    def write(self, file, text):
        # 将json写入文件
        with open(file, 'w') as f:
            f.write(text)
        return None

    def get_write(self, type_, opt, t):
        text = self.get(type=type_, t1=opt, t2=opt, t=t)
        file = f'{self.path}/{type_}_{t}/{opt}.json'
        print(file)
        self.write(file, text)
        return text

    def get_all(self):
        for type_ in ['week', 'month']:
            for t in ['sale', 'book', 'sold']:
                for opt in eval(f'self.{type_}_option'):
                    self.get_write(type_, opt, t)
        return None

    def update(self, type_):
        for t in ['sale', 'book', 'sold']:
            opt = eval(f'self.{type_}_option[0]')
            text = self.get_write(type_, opt, t)
            market(json.loads(text), f'{type_}_{t}')
        return None

# TODO: 还没有测试
class Updata(Spider):
    def load(self, filename):
        """打开一个json文件,返回object"""
        with open(f'{path}/{filename}.json', 'r') as f:
            return json.load(f)

    def write(self, text, type_, date, table):
        """将获得的json文本写入文件"""
        with open(f'{path}/{type_}_{table}/{date}.json', 'w') as f:
            f.write(text)
        print(f'>>> 【{type_} {table} {date}】is written into file.')

    def login(self):
        """登录gis,设置cookies和headers"""
        url = 'winsun.house365.com'
        self.set_cookies(f'http://{url}')
        self.session.headers.update({'Host': url, 'Referer': f'http://{url}/'})

    def get(self, type_, date, table):
        """获得市场数据
        :param type_: 'month' or 'week'
        :param date: '2018-01-01' for month or '201801' for week
        :param table: 'sale', 'book', 'sold'
        :return: result: json 形式的 string
        """
        url = 'http://winsun.house365.com/sys/dataout/date'
        args = {'type': type_, 't1': date, 't2': date, 't': table}
        result = self.session.get(url, params=args).content
        print(f'>>> 【{type_} {table} {date}】get!')
        return result.replace(b'\xef\xbb\xbf', b'').decode()

    def market(self, obj, type_, table):
        """更新周月报表
        :param obj: json对象
        :param type_: 'month' or 'week'
        :param table: 'sale', 'book', 'sold'
        """
        obj.reverse()
        model = eval(f'{type_.capitalize()}{table.capitalize()}')
        s = Session()

        for rec in obj:
            m = model()
            m.id = int(rec['id'])
            m.dist = rec['区属']
            m.plate = rec['板块']
            m.zone = rec['片区']
            m.usage = rec['功能']
            m.set = rec['件数']
            m.space = rec['面积']
            m.price = rec['均价']
            m.money = rec['金额']
            m.mjd_id = rec['面积段']
            m.djd_id = rec['单价段']
            m.zjd_id = rec['总价段']
            m.taoxing_id = rec['套型']
            m.proj_id = rec['prjid']
            m.proj_name = rec['projectname']
            m.pop_name = rec['popularizename']
            m.permit_id = rec['permitid']
            m.permit_no = rec['permitno']
            m.permit_date = str2date(rec['perdate'])
            m.update_time = rec['update_time']
            m.presaleid = rec['presaleid']
            if type_ == 'month':
                m.date = str2date(rec['年月'])
            else:
                m.week = rec['星期']
                m.start = str2date(rec['start_date'])
                m.end = str2date(rec['end_date'])
            s.update(m)
        s.commit()

    def get_write_update(self, type_, date, table):
        """get、写入文件、 更新数据库"""
        text = self.get_write(type_, date, table)
        obj = json.loads(text)
        self.market(obj, type_, table)

    def get_write(self, type_, date, table):
        """get并写入文件"""
        text = self.get(type_, date, table)
        self.write(text, type_, date, table)
        return text

    def load_update(self, type_, date, table):
        """Load文件、更新数据库"""
        obj = self.load(f'{type_}_{table}/{date}')
        self.market(obj, type_, table)


def update_once(type_):
    # def build_args():
    #     parser = ArgumentParser()
    #     parser.add_argument("type", choices=['week', 'month'])
    #     return parser

    gis = GisAPI()
    # type_ = build_args().type
    gis.update(type_)
    gis.driver.close()


if __name__ == '__main__':
    def build_args():
        parser = ArgumentParser()
        parser.add_argument("type", choices=['week', 'month'])
        return parser.parse_args()


    gis = GisAPI()
    type_ = build_args().type
    gis.update(type_)
    gis.driver.close()
