from winsun.map import BaiduMap
import pandas as pd
from functools import partial

# 设置一个起点
origin = [32.079143, 118.633997]

# 终点
df = pd.read_excel('e:/南京渔网质点_1km.xls')
df[['POINT_X', 'POINT_Y']] = df[['POINT_X', 'POINT_Y']].round(6)

# 查询函数
bd = BaiduMap('BsFEbr8Tz50vFRHE1dSXfnYO3MuFgrVM')
duration = partial(bd.duration, origin=origin, coord_type='wgs84')

# main
for idx, row in df.iterrows():
    print(idx)
    df.at[idx, 'duration'] = duration(destination=row[['POINT_Y', 'POINT_X']].tolist())
df[['POINT_X', 'POINT_Y', 'duration']].to_excel('e:/duration_circle.xlsx', index=False)
