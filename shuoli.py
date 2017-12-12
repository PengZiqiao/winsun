from winsun.utils import chg_desc
import pandas as pd
from numpy import isnan


class Zoushi:
    """
    sale, sold, price 分别代表上市、成交、均价
    xx_h, xx_t 对应环比、同比
    """

    def __init__(self, df, volumn='space', degree=2, tongbi=None, book=False):
        """
        :param df: 传入一个供销走势的DataFrame
        :param volumn: 'space'面积，'set'套数
        :param degree: 同环比保留几位小数
        :param tongbi: int，往前几期计算同比
        """

        def chg(df, period, degree):
            return df.pct_change(period).applymap(lambda x: chg_desc(x, degree))

        # 环比
        df_h = chg(df, 1, degree)

        # 调整用参数
        objs = [df.iloc[-1:], df_h.iloc[-1:]]
        index = ['v', 'h']

        # 同比
        if tongbi:
            df_t = chg(df, tongbi, degree)
            objs.append(df_t.iloc[-1:])
            index.append('t')

        self.df = pd.concat(objs)
        self.df.index = index

        self.tongbi = tongbi
        self.volumn = volumn
        self.book = book

    def thb_txt(self, item):
        """
        :param item: 'sale','sold','book','price'
        :return:
        """
        series = self.df[item]
        hb = f'，环比{series.h}' if series.h else ''
        if self.tongbi:
            tb = f'，同比{series.t}' if series.t else ''
            return f'{hb}{tb}'
        else:
            return hb

    def value_txt(self, item):
        value = self.df[item].v
        # 上市、成交、认购
        if item in ['sale', 'sold', 'book']:
            if isnan(value) or value == 0:
                return f'无'
            else:
                return f'{value:.2f}万㎡' if self.volumn == 'space' else f'{value:.0f}套'

        #  均价
        else:
            if isnan(value) or value == 0:
                return '无'
            else:
                return f'{value:.0f}元/㎡'

    def text(self, item):
        value = self.value_txt(item)
        # 上市、成交、认购
        if item in ['sale', 'sold', 'book']:
            item_ = {'sale': '上市', 'sold': '成交', 'book': '认购'}[item]
            if value == '无':
                return f'无{item_}。'
            else:
                thb = self.thb_txt(item)
                return f'{item_}{value}{thb}。'
        # 均价
        else:
            if value == '无':
                return ''
            else:
                thb = self.thb_txt(item)
                return f'成交均价{value}{thb}。'

    @property
    def shuoli(self):
        items = ['sale', 'sold', 'price']
        if self.book:
            items.insert(1, 'book')

        text = ''
        for each in items:
            text += f'{self.text(each)}'

        return text
