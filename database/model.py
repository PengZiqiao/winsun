from sqlalchemy import create_engine, Column, Integer, Float, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base, declared_attr, AbstractConcreteBase
from sqlalchemy.orm import sessionmaker, relationship

engine = create_engine('sqlite:///e:/gisDataBase/winsun')
Session = sessionmaker(engine)
Base = declarative_base()


class MianjiDuan(Base):
    """面积段"""
    __tablename__ = 'acreage'

    id = Column(Integer, primary_key=True)
    mjd_label = Column(String, name='面积段')
    mjd_low = Column(Float, name='acreage_low')
    mjd_high = Column(Float, name='acreage_high')
    month_book = relationship('MonthBook', backref='mianjiduan')
    month_sale = relationship('MonthSale', backref='mianjiduan')
    month_sold = relationship('MonthSold', backref='mianjiduan')
    week_book = relationship('WeekBook', backref='mianjiduan')
    week_sale = relationship('WeekSale', backref='mianjiduan')
    week_sold = relationship('WeekSold', backref='mianjiduan')

    def __repr__(self):
        return f'<MianjiDuan {self.mjd_label}>'


class DanjiaDuan(Base):
    """单价段"""
    __tablename__ = 'aveprice'

    id = Column(Integer, primary_key=True)
    djd_label = Column(String, name='单价段')
    djd_low = Column(Float, name='aveprice_low')
    djd_high = Column(Float, name='aveprice_high')
    month_book = relationship('MonthBook', backref='danjiaduan')
    month_sale = relationship('MonthSale', backref='danjiaduan')
    month_sold = relationship('MonthSold', backref='danjiaduan')
    week_book = relationship('WeekBook', backref='danjiaduan')
    week_sale = relationship('WeekSale', backref='danjiaduan')
    week_sold = relationship('WeekSold', backref='danjiaduan')

    def __repr__(self):
        return f'<DanjiaDuan {self.djd_label}>'


class ZongjiaDuan(Base):
    """单价段"""
    __tablename__ = 'tprice'

    id = Column(Integer, primary_key=True)
    zjd_label = Column(String, name='总价段')
    zjd_low = Column(Float, name='tprice_low')
    zjd_high = Column(Float, name='tprice_high')
    month_book = relationship('MonthBook', backref='zongjiaduan')
    month_sale = relationship('MonthSale', backref='zongjiaduan')
    month_sold = relationship('MonthSold', backref='zongjiaduan')
    week_book = relationship('WeekBook', backref='zongjiaduan')
    week_sale = relationship('WeekSale', backref='zongjiaduan')
    week_sold = relationship('WeekSold', backref='zongjiaduan')

    def __repr__(self):
        return f'<ZongjiaDuan {self.zjd_label}>'


class TaoXing(Base):
    """套型"""
    __tablename__ = 'type'

    id = Column(Integer, primary_key=True)
    tx_name = Column(String, name='套型')
    month_book = relationship('MonthBook', backref='taoxing')
    month_sale = relationship('MonthSale', backref='taoxing')
    month_sold = relationship('MonthSold', backref='taoxing')
    week_book = relationship('WeekBook', backref='taoxing')
    week_sale = relationship('WeekSale', backref='taoxing')
    week_sold = relationship('WeekSold', backref='taoxing')

    def __repr__(self):
        return f'<TaoXing {self.tx_name}>'


class MarketBase(AbstractConcreteBase, Base):
    """月度、周度表基于此表"""
    id = Column(Integer, primary_key=True)
    # 地区
    dist = Column(String, name='区属')
    plate = Column(String, name='板块')
    zone = Column(String, name='片区')
    # 功能
    usage = Column(String, name='功能')
    # 量价
    set = Column(Integer, name='件数')
    space = Column(Float, name='面积')
    price = Column(Integer, name='均价')
    money = Column(Float, name='金额')
    # 项目基本信息
    proj_id = Column(Integer, name='prjid')
    proj_name = Column(String, name='projectname')
    pop_name = Column(String, name='popularizename')
    # 许可证
    permit_id = Column(Integer, name='permitid')
    permit_no = Column(String, name='permitno')
    permit_date = Column(Date, name='perdate')
    # 暂时用不到
    update_time = Column(String)
    presaleid = Column(String)

    # 结构、套型
    @declared_attr
    def mjd_id(self):
        return Column(Integer, ForeignKey('acreage.id'), name='面积段')

    @declared_attr
    def djd_id(self):
        return Column(Integer, ForeignKey('aveprice.id'), name='单价段')

    @declared_attr
    def zjd_id(self):
        return Column(Integer, ForeignKey('tprice.id'), name='总价段')

    @declared_attr
    def taoxing_id(self):
        return Column(Integer, ForeignKey('type.id'), name='套型')

    @declared_attr
    def __mapper_args__(cls):
        return {'concrete': True} if cls.__name__ != "MarketBase" else {}


class MonthBook(MarketBase):
    """月度认购"""
    __tablename__ = 'month_book'
    date = Column(Date, name='年月')


class MonthSale(MarketBase):
    """月度上市"""
    __tablename__ = 'month_sale'
    date = Column(Date, name='年月')


class MonthSold(MarketBase):
    """月度成交"""
    __tablename__ = 'month_sold'
    date = Column(Date, name='年月')


class WeekBook(MarketBase):
    """周度认购"""
    __tablename__ = 'week_book'
    week = Column(Integer, name='星期')
    start = Column(Date, name='start_date')
    end = Column(Date, name='end_date')


class WeekSale(MarketBase):
    """周度上市"""
    __tablename__ = 'week_sale'
    week = Column(Integer, name='星期')
    start = Column(Date, name='start_date')
    end = Column(Date, name='end_date')


class WeekSold(MarketBase):
    """周度成交"""
    __tablename__ = 'week_sold'
    week = Column(Integer, name='星期')
    start = Column(Date, name='start_date')
    end = Column(Date, name='end_date')
