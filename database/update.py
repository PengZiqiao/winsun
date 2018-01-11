import json
import os

from winsun.utils import Spider
from winsun.database.model import MonthBook, MonthSale, MonthSold, WeekBook, WeekSale, WeekSold
from winsun.database.model import Session, MianjiDuan, DanjiaDuan, ZongjiaDuan, TaoXing
from winsun.database.query import str2date
import itertools

path = 'E:/gisDataBase'


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
        url = 'http://winsun.house365.com/sys/dataout/data'
        args = {'type': type_, 't1': date, 't2': date, 't': table}
        result = self.session.get(url, params=args)
        print(f'>>> 【{type_} {table} {date}】get!')
        return result.content.replace(b'\xef\xbb\xbf', b'').decode()

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
            s.add(m)
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

    def batch_get(self, type_, date_list):
        """批量下载json"""
        # 表格
        tables = ['sale', 'book', 'sold']

        for table, date in itertools.product(tables, date_list):
            self.get_write(type_, date, table)


def init_db(self):
    """根据文件夹内json文件初始化数据库"""
    walk = list(list(os.walk(path)))[1:]
    for path_, _, files in walk:
        type_, table = path_.split('\\')[1].split('_')
        for file in files:
            date = file.replace('.json', '')
            print(type_, date, table)
            self.load_update(type_, date, table)


if __name__ == '__main__':
    ud = Updata()
    ud.login()

    # 日常更新
    type_ = input('>>> 请输入更新报表类型(week/month)...\n')
    date = input('>>> 请输入更新日期(如201802/2018-02-01)...\n')
    for table in ['sale', 'book', 'sold']:
        ud.get_write_update(type_, date, table)

    # 批量下载json文件、初始化数据库
    # ud.batch_get('week', [])
    # ud.init_db()
