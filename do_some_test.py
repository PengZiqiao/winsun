from winsun.datebase.query import Query, str2date
from winsun.datebase.model import MonthSold, MianjiDuan, DanjiaDuan
from winsun.utils import Month

m = Month()
q = Query()

# 日期
end = m.date
start = m.before(2).date

# 查询
df = q.gxj('week')
print(df)
