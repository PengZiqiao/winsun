from numpy import isnan
from pandas.tseries.offsets import DateOffset, MonthBegin
import datetime
import calendar
from selenium import webdriver
import requests


def growth_rate(a, b):
    """growth rate
    a相对于b的增长率
    """
    return (a - b) / b


def cagr(current_value, start_value, years):
    """
    复合增长率
    """
    return (current_value / start_value) ** (1 / years) - 1


def chg_desc(value, degree=2):
    """
    将带正负号的比值(1代表100%)转成“增长/下降xx%”的形式
    """
    if isnan(value):
        # 传入nan时直接返回None
        return None
    else:
        # 方向
        change = '下降' if value < 0 else '增长'
        # 数值
        value = abs(value) * 100
        value = f'{value:.0f}' if degree == 0 else round(value, degree)
        # 组合
        return f'{change}{value}%'


def gr(a, b, degree=2):
    return chg_desc(growth_rate(a, b), degree)


class Week:
    """
    monday, sunday 为上周一、日
    N 为上周周数
    """
    # 从今天开始往前找第一个星期日
    sunday = datetime.date.today()
    while sunday.weekday() != 6:
        sunday -= datetime.timedelta(days=1)
    sunday_str = sunday.strftime('%Y%m%d')

    # 从上周星期日往前推6天即为星期一
    monday = sunday - datetime.timedelta(days=6)
    monday_str = monday.strftime('%Y%m%d')

    # 周数
    N = int(sunday.strftime('%U')) if monday.year == 2018 else int(monday.strftime('%U'))

    def before(self, i):
        """从上周起往前的第i周"""
        w = Week()
        w.monday = self.monday - datetime.timedelta(weeks=i)
        w.sunday = self.sunday - datetime.timedelta(weeks=i)
        w.N = int(w.sunday.strftime('%U')) if w.monday.year == 2018 else int(w.monday.strftime('%U'))
        return w

    def str_format(self, format):
        """变更日期文字样式"""
        self.monday_str = self.monday.strftime(format)
        self.sunday_str = self.sunday.strftime(format)

    def __repr__(self):
        return f'<class Week: {self.monday_str}-{self.sunday_str} {self.N}>'


class Month:
    def __init__(self):
        last_month = datetime.date.today() - DateOffset(months=1)
        # 25号（不含）之后运行，月份为当月，1号至25号（含）运行，月份为上个月
        self.date = MonthBegin().rollforward(last_month) if last_month.day > 25 else MonthBegin().rollback(last_month)
        self.month = self.date.month
        self.year = self.date.year
        self.str = self.date.strftime("%Y%m%d")

    def before(self, i):
        """i个月之前"""
        m = Month()
        m.date = self.date - DateOffset(months=i)
        m.month = m.date.month
        m.year = m.date.year
        m.str = m.date.strftime("%Y%m%d")
        return m

    def str_format(self, format):
        """变更日期文字样式"""
        self.str = self.date.strftime(format)

    def __repr__(self):
        return f'<class Month: {self.str}>'


class Spider:
    def __init__(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko)',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Connection': 'keep-alive'
        }

        # selenium
        options = webdriver.ChromeOptions()
        for key, value in headers.items():
            options.add_argument(f'{key}={value}')
        self.driver = webdriver.Chrome(chrome_options=options)

        # session
        self.session = requests.Session()
        self.session.headers = headers

    def set_cookies(self, url):
        """通过selenium登陆后获得cookies，并设定至requests.Session()"""
        self.driver.get(url)
        input('>>> 登陆完成后请按回车...')
        cookies = self.driver.get_cookies()
        cookies = dict((each['name'], each['value']) for each in cookies)
        self.session.cookies = requests.utils.cookiejar_from_dict(cookies)
