﻿from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import Select, WebDriverWait
import pandas as pd
from winsun.utils import Week, Month
from bs4 import BeautifulSoup
from time import sleep

"""常量"""
ZHU_ZHAI = ['住宅']
SHANG_YE = ['商业']
BAN_GONG = ['办公']
SHANG_BAN = ['商业', '办公']
BIE_SHU = ['独立别墅', '叠加别墅', '联排别墅', '双拼别墅']
SHANG_PIN_ZHU_ZHAI = ['独立别墅', '叠加别墅', '联排别墅', '双拼别墅', '住宅']
QUANSHI_BUHAN_LIGAO = '全市(不含溧水高淳)'

class CricSpider:
    def __init__(self):
        cookies = [
            {'domain': '2015.app.cric.com',
             'httpOnly': False,
             'mjd_label': 'BIGipServerpool_10.0.7',
             'path': '/',
             'secure': False,
             'value': '34013194.20480.0000'},
            {'domain': '.2015.app.cric.com',
             'httpOnly': False,
             'mjd_label': 'Hm_lpvt_dca78b8bfff3e4d195a71fcb0524dcf3',
             'path': '/',
             'secure': False,
             'value': '1503474356'},
            {'domain': '.cric.com',
             'expiry': 1504079106.982804,
             'httpOnly': True,
             'mjd_label': 'cric2015',
             'path': '/',
             'secure': False,
             'value': 'C101A9F6D98B733C1ACDA77C8F59A308A206181EC2BA28017D5B5482980ED2E6A61F798D31E2DCE553208E8550D5AACBB0F3C3FA1CC004B4836B8DF95794A14F5AF682E978DB4847EB82FF2D'},
            {'domain': '.2015.app.cric.com',
             'expiry': 1535010356,
             'httpOnly': False,
             'mjd_label': 'Hm_lvt_dca78b8bfff3e4d195a71fcb0524dcf3',
             'path': '/',
             'secure': False,
             'value': '1503474313'},
            {'domain': '.cric.com',
             'expiry': 1506066306.982859,
             'httpOnly': False,
             'mjd_label': 'cric2015_token',
             'path': '/',
             'secure': False,
             'value': 'username=c7WgHp4zScNtsm7KKQFU/Q==&verifycode=jjKbRj1fAaWKtVZoTqJCYQ==&token=ZT+H74zJs4mnpW93dJ9ZY0FGAy1+y8rRuGTlI9bd2c/2Bj5hjjCIbciiWaiJwSFh&usermobilephone=/xjKEQnYyec5HZvPfeoEsQ==&userid=Fiw/A5cH9X34OaMfzJTZzvuhDhEURUDyXzQkeVFh/K9SzWYASZeECe8KehkOlt37'}
        ]
        self.url = 'http://2015.app.cric.com/'
        self.driver = webdriver.Chrome()
        self.driver.get(self.url)
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.get(self.url)
        self.wait = WebDriverWait(self.driver, 10)

    def loaded(self, name='数据说明'):
        self.wait.until(lambda driver: driver.find_element_by_link_text(name))

    def checkbox(self, name, value_list):
        """多选框
        :param
            mjd_label:表单控件的name
            value:表单的 value
        """
        chk = self.driver.find_elements_by_name(name)

        # 取消所有已选项目
        for each in chk:
            if each.is_selected():
                each.click()

        # 根据value选中需要的项目
        for each in chk:
            if each.get_attribute('value') in value_list:
                each.click()

    def stat_date(self, date, point):
        """选择日期
        date: '2017年' or '2017年08月' or '2017年x周/季度'
        point: 'Start' or 'End'
        """
        self.driver.find_element_by_xpath(f"//div[@id='divTimeRangeChoice_{point}']/div/a").click()
        sleep(0.2)
        self.driver.find_element_by_xpath(f"//div[@id='divTimeRangeChoice_{point}']//a[@data-value='{date}']").click()
        sleep(0.2)

    def stat_area(self):
        """区域选择"""
        self.driver.find_element_by_xpath("//div[@class='area_checked_content']/p").click()
        area_xpath = f"//div[@class= 'area_layer']//input[@value='{area}']"
        self.wait.until(lambda driver: driver.find_element_by_xpath(area_xpath).is_displayed())
        self.driver.find_element_by_xpath(area_xpath).click()
        sleep(0.2)
        self.click('确定')

    def stat_area2(self, area):
        """板块选择"""
        self.driver.find_element_by_xpath("//div[@class='area_checked_content']/p").click()
        area_xpath = f"//div[@class= 'plate_warp_layer']//label[text()='{area}']"
        self.wait.until(lambda driver: driver.find_element_by_xpath(area_xpath).is_displayed)
        self.driver.find_element_by_xpath(area_xpath).click()
        sleep(0.2)
        self.driver.find_element_by_xpath(f"//div[@class= 'plate_warp_layer']//label[text()='请选择板块']").click()
        sleep(0.2)
        self.click('确定')

    def monitor_date(self, date, point):
        """选择日期
        date: '2017年' or '2017年08月' or '2017年x周/季度'
        point: 'Begin' or 'End'
        """
        self.driver.find_element_by_xpath(f"//span[contains(@mjd_label, 'Date{point}')]/div/a").click()
        sleep(0.2)
        self.driver.find_element_by_xpath(f"//span[contains(@mjd_label, 'Date{point}')]//a[@data-value='{date}']").click()
        sleep(0.2)

    def monitor_area(self):
        self.driver.find_element_by_xpath("//div[@mjd_label='regionselecter_region_block']/div/div/p").click()
        area_xpath = f"//div[@mjd_label='regionselecter_region_block']//label[text()='{area}']"
        self.wait.until(lambda driver: driver.find_element_by_xpath(area_xpath).is_displayed())
        self.driver.find_element_by_xpath(area_xpath).click()
        sleep(0.2)
        self.click('确定')

    def monitor_area2(self, area):
        """板块选择"""
        self.driver.find_element_by_xpath("//div[@mjd_label='regionselecter_area_block']/div/div/p").click()
        area_xpath = f"//div[@mjd_label='regionselecter_area_block']//label[text()='{area}']"
        self.wait.until(lambda driver: driver.find_element_by_xpath(area_xpath).is_displayed())
        self.driver.find_element_by_xpath(area_xpath).click()
        sleep(0.2)
        self.driver.find_element_by_xpath(f"//div[@mjd_label='regionselecter_area_block']//label[text()='请选择板块']").click()
        sleep(0.2)
        self.click('确定')

    def monitor_usage(self, value_list):
        # 按两次全选，取消所有选中
        chk = self.driver.find_element_by_xpath("//input[contains(@mjd_label,'RoomUsageAll')]")
        chk.click()
        sleep(0.2)
        chk.click()
        sleep(0.2)

        # 按需要选中
        chk = self.driver.find_elements_by_xpath("//input[contains(@mjd_label,'Dims_RoomUsage')]")
        for each in chk:
            if each.get_attribute('value') in value_list:
                each.click()

    def monitor_radio(self, name):
        self.driver.find_element_by_xpath(f"//input[@data-text='{mjd_label}']").click()

    def click(self, name, pause=0.2):
        self.driver.find_element_by_link_text(name).click()
        sleep(pause)

    def stat_page(self, city):
        url = f'{self.url}Statistic/StatisticCenter/StatisticCenter?CityName={city}'
        self.driver.get(url)
        self.loaded()

    def monitor_page(self, city):
        url = f'{self.url}Statistic/MarketMonitor/MarketMonitoringIndex?CityName={city}'
        self.driver.get(url)
        self.loaded()
        
class GisSpider:
    def __init__(self):
        """初始化并登陆GIS
        """
        self.url = 'http://winsun.house365.com/'
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 60)

        # 登陆
        self.driver.get(f'{self.url}weixin/login')
        print('>>> 请使用微信扫码登陆')
        try:
            self.wait.until(lambda driver: driver.find_element_by_class_name('logo'))
            print('>>> 成功登陆')
            sleep(5)
        except TimeoutException:
            print('>>> 登陆超时')

    def gongxiao(self, by, **kwargs):
        """商品房市场-供销走势
        :param 参数均为 string 或 [string,string,...]
            by: year, month, week
            year_start:开始年份 default:最新
            year:结束年份 default:最新
            plate:板块 default:全市
            pq:片区 default:不限
            groupby:分类方式 default:板块
            usg: 功能 default:[住宅]
            item: 输出项 default:[上市面积, 销售面积, 销售套数, 销售均价]
            isSum: 0 逐期 1 累计
        """
        if by == 'year':
            self.driver.get(f'{self.url}stat/wsdbestate/year')
        else:
            self.driver.get(f'{self.url}stat/wsdbestate/{by}trend')
        self.wait.until(lambda driver: driver.find_element_by_id("btnSearch"))

        # 下拉列表的选项们
        for key in ['week_start', 'week', 'month_start', 'month', 'year_start', 'year', 'plate', 'pq', 'groupby',
                    'isSum']:
            if key in kwargs:
                self.select(key, kwargs[key])

        # 功能
        if 'usg' in kwargs:
            self.checkbox('chk_usg', kwargs['usg'])

        # 输出项
        if 'item' in kwargs:
            dic = {
                '上市面积': '0',
                '上市套数': '1',
                '认购面积': '2',
                '认购套数': '3',
                '销售面积': '4',
                '销售套数': '5',
                '销售金额': '6',
                '销售均价': '7',
            }
            value_list = list(dic[key] for key in kwargs['item'])
            self.checkbox('chk_fld[]', value_list)

        # 查询
        self.driver.find_element_by_id("btnSearch").click()
        try:
            self.wait.until_not(lambda driver: driver.find_element_by_class_name('loading'))
            print('>>> 查询成功')
        except TimeoutException:
            print('>>> 超时')
        sleep(3)
        return self.driver.page_source

    def rank(self, by, plate, usg):
        """当期排行榜
        :param 
            by: week, month
            plate: 板块
            usg: 物业类型
        :return: df的列表,如df[0]为面积排行榜
        """
        self.driver.get(f'{self.url}stat/wsdbestate/{by}rank')
        self.wait.until(lambda driver: driver.find_element_by_id("btnSearch"))

        # 板块、功能
        self.select('plate', plate)
        self.checkbox('chk_usg', usg)

        # 查询
        self.driver.find_element_by_id("btnSearch").click()
        try:
            self.wait.until_not(lambda driver: driver.find_element_by_class_name('loading'))
            print('>>> 查询成功')
        except TimeoutException:
            print('>>> 超时')
        sleep(3)
        rank_df = pd.read_html(self.driver.page_source, index_col=0, header=0)
        return rank_df

    def select(self, name, value):
        """下拉列表
        :param
            mjd_label:表单控件的name
            value:表单的 value 或visible_text
        """
        s = Select(self.driver.find_element_by_name(name))
        try:
            s.select_by_visible_text(value)
        except NoSuchElementException:
            s.select_by_value(value)

    def checkbox(self, name, value_list):
        """多选框
        :param
            mjd_label:表单控件的name
            value:表单的 value 或visible_text
        """

        chk = self.driver.find_elements_by_name(name)

        # 取消所有已选项目
        for each in chk:
            if each.is_selected():
                each.click()

        # 根据value选中需要的项目
        for each in chk:
            if each.get_attribute('value') in value_list:
                each.click()

    def current_gxj(self, by, usg, plate, rengou=False):
        """返回一个当期的，以各板块为行，以“供、销、价”为列的表格，含“合计”
        :param 
            by: year, month, week
            usg: 物业类型
            plate: 板块
            rengou: 是否包含认购面积
        :return: df
        """

        item = ['上市面积', '销售面积', '销售均价']
        if rengou:
            item.append('认购面积')

        r = self.gongxiao(by=by, usg=usg, plate=plate, item=item, isSum='1')
        df = pd.read_html(r, index_col=0, header=0)[0]
        df = df.rename(index=lambda x: x.replace('仙西', '仙林'))
        df = df_gxj(df)
        
        return df

    def trend_gxj(self, by, usg, plate, period, rengou=False):
        """返回一个按时间为行的，以“供、销、价”为列的表格
        :param 
            by: year, month, week
            usg: 物业类型
            plate: 板块
            rengou: 是否包含认购面积
            period: 期数
        :return: df
        """
        # 设置开始时间
        if by == 'week':
            w = Week()
            start = {
                'week_start': f'2017{w.N - period + 1}'
            }

        if by == 'month':
            m = Month()
            start_year, start_month = m.before(period-1)
            start = {
                'month_start': f'{start_year}-{start_month:02d}-01'
            }

        item = ['上市面积', '销售面积', '销售均价']
        if rengou:
            item.append('认购面积')

        r = self.gongxiao(by=by, plate=plate, usg=usg, item=item, isSum='0', **start)
        df = pd.read_html(r, index_col=0, header=1)[0]
        df = df_reshape(df, -1, list(range(period)), item)
        
        return df_gxj(df)


class NeiSpider:
    def __init__(self, username, password):
        """初始化并登陆
        """
        self.url= 'http://192.168.108.16/realty/admin/'
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 60)
        
        # 登陆
        try:
            self.driver.get(f'{self.url}main.php')
            self.driver.find_element_by_name('username').send_keys(username)
            self.driver.find_element_by_name('password').send_keys(password)
            self.driver.find_element_by_name('submit').click()
            self.wait.until(lambda driver: driver.title == '研究部数据管理系统')
            print('>>> 登陆成功')
        except TimeoutException:
            print('>>> 登陆失败')
            
    def gongxiao(self, by, **kwargs):
        """供销查询
        :param
            by: 'week', 'month', 'year'
            start, end: 2017年第1周 => '201701'; 2017年1月 => '2017-01-00'
            block: 板块 default:'全市'
            stat: 输出方式
            usg: 物业类型
            item：输出项
            add: 累计 => '0'; 逐周 => '1'
        """
        self.driver.get(f'{self.url}ol_new_block_{by}.php')
        self.wait.until(lambda driver: driver.find_element_by_name('block'))

        # 设置开始、结束时间
        kwargs[f'{by}1'], kwargs[f'{by}2'] = kwargs['start'], kwargs['end']

        # 下拉列表的选项们
        for key in [f'{by}1', f'{by}2', 'block', 'stat', 'add']:
            if key in kwargs:
                self.select(key, kwargs[key])

        # 物业类型
        if 'usg' in kwargs:
            self.multiselect('usage[]', kwargs['usg'])

        # 输出项
        if 'item' in kwargs:
            if by == 'month':
                self.multiselect('Litem1[]', kwargs['item'])
            else:
                self.multiselect('Litem2[]', kwargs['item'])

        # 查询
        self.submit()
        try:
            self.wait.until(lambda driver: driver.find_element_by_tag_name('caption'))
            print('>>> 查询成功')
        except TimeoutException:
            print('>>> 超时')
            
        bs = BeautifulSoup(self.driver.page_source, 'lxml')
        table = bs.table.find('table').prettify()
        df = pd.read_html(table, index_col=0, header=1)[0]
        return df


    def select(self, name, value):
        """下拉列表
        :param
            mjd_label:表单控件的name
            value:表单的 value 或visible_text
        """
        s = Select(self.driver.find_element_by_name(name))
        try:
            s.select_by_visible_text(value)
        except NoSuchElementException:
            s.select_by_value(value)

    def multiselect(self, name, value_list):
        """多选
        :param
            mjd_label:表单控件的name
            value_list:表单的 value 或visible_text 组成的列表
        """
        s = Select(self.driver.find_element_by_name(name))
        s.deselect_all()
        for value in value_list:
            try:
                s.select_by_visible_text(value)
            except NoSuchElementException:
                s.select_by_value(value)
                
    def sendkeys(self, name, value):
        self.driver.find_element_by_name(name).clear()
        self.driver.find_element_by_name(name).send_keys(value)

    def sum_gxj(self, by, start, end, usg, block, rengou=False):
        """返回一个时间段内，以各板块为行，以“供、销、价”为列的表格，含“合计”
        :param 
            by: year, month, week
            start, end：时间
            usg: 物业类型
            block: 板块
            rengou: 是否包含认购面积
        :return: df
        """

        item = ['上市面积', '已售面积', '已售均价']
        if rengou:
            item.append('认购面积')

        df = self.gongxiao(by=by, start=start, end=end, usg=usg, block=block, stat='按板块/片区', item=item, add='0')
        df.columns = item
        df = df.rename(index=lambda x: x.replace('仙西', '仙林'))
        df = df_gxj(df)
        return df

    def trend_gxj(self, by, start, end, usg, block, rengou=False):
        """返回一个按时间为行的，以“供、销、价”为列的表格
        :param 
            by: year, month, week
            start, end：时间
            usg: 物业类型
            block: 板块
            plate: 板块
            rengou: 是否包含认购面积
        :return: df
        """
        item = ['上市面积', '已售面积', '已售均价']
        if rengou:
            item.append('认购面积')

        if by == 'year':
            df = self.gongxiao(by=by, start=start, end=end, block=block, usg=usg, item=item, stat='按板块/片区')
        else:
            df = self.gongxiao(by=by, start=start, end=end, block=block, usg=usg, item=item, stat='按板块/片区', add='1')
        
        col_len = int(len(df.columns) / len(item) - 1)
        
        df = df_reshape(df, 0, list(range(col_len)), item)
        return df_gxj(df)
    
    def suiji(self):
        self.driver.get(f'{self.url}ol_filter_stat.php?check_flag=false')
        self.wait.until(lambda driver: driver.find_element_by_name('ByProject'))
        print('>>> 可以开始使用随机随机统计')
        print('>>> 使用nei.select(mjd_label, value)控制下拉菜单和单选框')
        print('>>> 使用nei.multiselect(mjd_label, value_list)控制多选框')
        print('>>> 使用nei.sendkeys(mjd_label, value)控制输入框')
        print('>>> 输入df = nei.submit()提交')
        
    def submit(self):
        self.driver.find_element_by_name("Submit").click()
        

def df_reshape(df, row, index, columns):
    """
    :param 
        df: pd.DataFrame()
        row: 保留第几行数据
        index：大概是一个日期组成的列表，转换为每行
        columns：项名称组成的列表，转换为每列
    :return df
    """
    col_len = len(columns)
    index_len = len(index)

    df = df.iloc[row,range(col_len * index_len)]
    matrix = df.as_matrix().reshape(index_len, col_len)
    return pd.DataFrame(matrix, index, columns)

def df_gxj(df):
    """表中面积单位由㎡换算为万㎡，并保留两位小数"""
    # 最后一列为均价，前面2（含认购则为3）列为面积
    for each in df.columns[:-1]:
            df[each] = df[each].astype('float')
            df[each] = df[each] / 1e4
    df = df.round(2)
    df[df.columns[-1]] = df[df.columns[-1]].astype('int')
    return df

def cut(df, break_list):
    df2 = pd.DataFrame()
    df['upper'] = list(map(lambda x:int(x.split('-')[1]), df.index))
    # first row
    row = f'{break_list[0]}以下'
    demand = df['upper'] <= break_list[0]
    df2[row] = df[demand].sum()
    
    # middle
    lower = break_list[0]
    for upper in break_list[1:]:
        row = f'{lower}-{upper}'
        demand = (df['upper']>lower) & (df['upper'] <= upper)
        df2[row] = df[demand].sum()
        lower = upper
        
    # last row
    row = f'{break_list[-1]}以上'
    demand = df['upper'] > break_list[-1]
    df2[row] = df[demand].sum()
    
    return df2.drop('upper').T