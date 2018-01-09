from datetime import date

import numpy as np
import pandas as pd
from sqlalchemy.sql import func
from winsun.database.model import Session, MonthSale, MonthSold, MonthBook, WeekSale, WeekSold, WeekBook, \
    MianjiDuan, DanjiaDuan, ZongjiaDuan

from winsun.utils import Week, Month

ZHUZHAI = ('多层住宅', '高层住宅', '小高层住宅')
BIESHU = ('叠加别墅', '独立别墅', '双拼别墅', '联排别墅')
SPZZ = ZHUZHAI + BIESHU

GONGYU = ('挑高公寓办公', '平层公寓办公')
XIEZILOU = ('乙级办公', '甲级办公')
BANGONG = GONGYU + XIEZILOU + ('其他办公',)

SHANGYE = ('底商商业', '专业市场商业', '集中商业', '街区商业', '其它商业')

QUANSHI = ('城中', '城东', '城南', '河西', '城北', '仙西', '江宁', '浦口', '六合', '溧水', '高淳')
BUHANLIGAO = QUANSHI[:-2]

MJD_BINDS = []
DJD_BINDS = list(range(4000, 51000, 1000))
ZJD_BINDS = []

def str2date(text: str):
    """将“xxxx-xx-xx”格式的字符串转换为date"""
    return date(*[int(x) for x in text.split('-')])


class Query:
    s = Session()
    query = s.query

    def filter(self, table, date_range, usage=ZHUZHAI, plate=QUANSHI):
        """筛选
        只封装一些常用条件，更复杂的使用Query().query或者在返回结果res上再次使用filter()完成.

        :param table: 数据库表对象，用于确定在哪张表里查询
        :param date_range: 包含首尾两个date的tuple或list
        :param usage: 包含物业类型str的tuple或者list，可调用常量。默认ZHUZHAI，即('多层住宅', '高层住宅', '小高层住宅')
        :param plate: 包含板块str的tuple或者list,可调用常量。默认为QUANSHI
        :param join: 联合查询表组成的tuple或list
        :return: Query对象，可进一步使用from_self()选择显示列, query.filter()或者group_by()或者读入pandas
        """
        # 月报周报采用不同的字段来筛选日期，TODO:加入日报后改写
        date_field = getattr(table, 'week' if 'Week' in table.__name__ else 'date')

        return self.query(table).filter(
            date_field.between(*date_range),
            table.usage.in_(usage),
            table.plate.in_(plate)
        )

    def group(self, query, by, outputs):
        """分组
        :param query: Query对象
        :param by: 分组依据字段对象组成的tuple或list
        :param outputs: 包含输出项字段的tuple或list，结果按sum()聚合
        :return:Query对象，可进一步使用from_self()选择显示列, query.filter()或者group_by()或者读入pandas
        """
        # 输出项用func.sum()聚合，label为model中字段
        output_fields = [each.label(each.key) for each in by]
        output_fields.extend([func.sum(each).label(each.key) for each in outputs])

        return query.from_self(*output_fields).group_by(*by)

    def to_df(self, query, index=None, column=None):
        """转为df

        :param query:
        :param index: df的index
        :param column: 如果存在，则按index、column透视
        :return: DataFrame对象
        """
        df = pd.read_sql(query.statement, self.s.bind)
        df = df.replace('仙西', '仙林')

        if column:
            return df.pivot(index, column)
        elif index:
            return df.set_index(index)
        else:
            return df

    def render_date(self, date_type, period):
        if date_type == 'week':
            d = Week()

            # index
            index = [d.before(i) for i in range(period)]
            index.reverse()
            for each in index:
                each.str_format('%m.%d')
            index_label = [f'{x.monday_str}-{x.sunday_str}' for x in index]

            # date range
            index_sql = [int(f'{x.monday.year}{x.N:02d}') for x in index]
            date_range = [index_sql[0], index_sql[-1]]
        else:
            d = Month()

            # index
            index = [d.before(i) for i in range(period)]
            index.reverse()
            for each in index:
                each.str_format('%y.%m')
            index_label = [x.str for x in index]

            # date range
            index_sql = [x.date for x in index]
            date_range = [index_sql[0], index_sql[-1]]

        return date_range, index_sql, index_label

    def query2df(self, table, date_range, usage, plate, group_by, outputs):
        res = self.filter(table, date_range, usage, plate)
        res = self.group(res, group_by, outputs)
        return self.to_df(res)

    def gxj(self, date_type='week', period=10, usage=ZHUZHAI, plate=QUANSHI, volumn='space', by='trend', book=False):
        """供销价

        :param date_type: 'week','month','day'分别代表周度、月度、日度，日度逻辑暂未加入
        :param period: int,包含的期数
        :param usage: 包含物业类型str的tuple或者list，可调用常量。默认ZHUZHAI，即('多层住宅', '高层住宅', '小高层住宅')
        :param plate: 包含板块str的tuple或者list,可调用常量。默认为QUANSHI
        :param volumn: 'space','set' 量用面积或套数表示
        :param by: 'trend','plate'按时间、板块
        :param book: 是否包含认购列
        :return: DateFrame对象
        """

        def group_args(by, table, date_field, volumn):
            """

            :param by: 'trend' or 'plate' or maybe others
            :param table: 数据库表对象
            :param date_field: 用于筛选日期的字段
            :param volumn: 'space' or 'set'
            :return:
            """
            group_by = [getattr(table, date_field) if by == 'trend' else getattr(table, by)]
            volumn_field = [getattr(table, volumn)]
            return group_by, volumn_field

        date_range, index_sql, index_label = self.render_date(date_type, period)

        # TODO：待加入日报逻辑
        if date_type == 'week':
            tb_sale, tb_sold, tb_book, date_field = WeekSale, WeekSold, WeekBook, 'week'
        elif date_type == 'month':
            tb_sale, tb_sold, tb_book, date_field = MonthSale, MonthSold, MonthBook, 'date'

        # 上市
        group_by, outputs = group_args(by, tb_sale, date_field, volumn)
        df_sale = self.query2df(tb_sale, date_range, usage, plate, group_by, outputs)
        df_sale.columns = [by, 'sale']

        # 成交
        group_by, outputs = group_args(by, tb_sold, date_field, volumn)
        outputs.extend([tb_sold.space, tb_sold.money] if volumn == 'set' else [tb_sold.money])
        df_sold = self.query2df(tb_sold, date_range, usage, plate, group_by, outputs)
        df_sold['price'] = df_sold['money'] / df_sold['space']
        df_sold.columns = [by, 'sold', 'space', 'money', 'price'] if volumn == 'set' else [by, 'sold', 'money', 'price']

        # 合并
        df = pd.merge(df_sale, df_sold, 'outer')

        # 认购
        if book:
            group_by, outputs = group_args(by, tb_book, date_field, volumn)
            df_book = self.query2df(tb_book, date_range, usage, plate, group_by, outputs)
            df_book.columns = [by, 'book']
            df = pd.merge(df, df_book, 'outer')

        # index
        df = df.set_index(by)
        if by == 'trend':
            df = df.reindex(index_sql)
            df.index = index_label
        else:
            plate = [x.replace('仙西', '仙林') for x in plate]
            df = df.reindex(plate)

        # 调整
        columns = ['sale', 'sold']
        if book:
            columns.insert(1, 'book')
        df[columns] = df[columns] if volumn == 'set' else (df[columns] / 1e4).round(2)
        df[columns] = df[columns].fillna(0)
        try:
            df['price'] = df['price'].round(0)
        except:
            pass
        columns.append('price')

        return df[columns]

    def rank(self, table=WeekSold, period=1, usage=ZHUZHAI, plate=QUANSHI,
             group_by=['pop_name', 'plate'], outputs=['space', 'set', 'money', 'price'],
             by='space', num=None):
        """排行

        :param table:
        :param period:
        :param usage:
        :param plate:
        :param group_by:
        :param outputs:
        :param by:
        :param num:
        :return: DateFrame
        """
        # 月报周报采用不同的字段来筛选日期，TODO:加入日报后改写
        date_field = getattr(table, 'week' if 'Week' in table.__name__ else 'date')
        if 'Week' in table.__name__:
            d = Week()
            date_range = [d.before(period - 1), d]
            date_range = [f'{x.monday.year}{x.N:02d}' for x in date_range]
        else:
            d = Month()
            date_range = [d.before(period - 1), d]
            date_range = [x.date for x in date_range]

        # 调整outputs, group_by
        if 'price' in outputs:
            if 'space' not in outputs:
                outputs.append('space')
            if 'money' not in outputs:
                outputs.append('money')
        outputs_ = [getattr(table, each) for each in outputs]
        group_by = [getattr(table, each) for each in group_by]

        # 筛选、分组
        res = self.filter(table, date_range, usage, plate)
        res = self.group(res, group_by, outputs_)

        # df
        df = self.to_df(res).sort_values(by, ascending=False)[:num]

        if 'price' in outputs:
            df['price'] = (df['money'] / df['space']).round(0)

        # 加入名次列
        df.reset_index(drop=True, inplace=True)
        df['rank'] = df.index + 1
        columns = df.columns.tolist()
        columns.insert(0, columns.pop())

        return df[columns]

    def cut(self, binds, date_type='week', period=12, usage=ZHUZHAI, plate=QUANSHI, by='mjd'):
        binds.insert(0, 0)
        binds.append(9e8)

        date_range, index_sql, index_label = self.render_date(date_type, period)
        if date_type == 'week':
            table = WeekSold
            date = WeekSold.week
            date_key = 'week'
        else:
            table = MonthSold
            date = MonthSold.date
            date_key = 'date'

        df = self.query2df(table, date_range, usage, plate, group_by=[date, getattr(table, f'{by}_id')],
                           outputs=[table.set])

        table_ = {'mjd': MianjiDuan, 'djd': DanjiaDuan, 'zjd': ZongjiaDuan}
        df_ = self.to_df(self.query(table_[by]))
        df_.columns = [f'{by}', 'low', 'high', f'{by}_id']

        df = df.merge(df_)
        df['bind'] = pd.cut(df.low, binds, right=False)

        return df.pivot_table('set', date_key, 'bind', 'sum', 0)
