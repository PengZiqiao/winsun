import pandas as pd
from openpyxl import Workbook
from winsun.map.__init__ import BaiduMap


def search_poi(query, **kwargs):
    """搜索渔网中所有符合条件的poi
    """
    fishnet = pd.read_excel('e:/nj_net.xlsx', index_col='id')
    total = len(fishnet)
    b = BaiduMap('BsFEbr8Tz50vFRHE1dSXfnYO3MuFgrVM')

    wb = Workbook()
    ws = wb.active
    ws.append(['address', 'lat', 'lng', 'name', 'tag', 'uid'])

    for idx, row in fishnet.iterrows():
        df = b.search_bounds(query, row.tolist())
        print(f'>>> {idx} / {total}: {len(df)}')
        for _, row in df.iterrows():
            ws.append(row.tolist())

    print('>>> saving file...')
    wb.save('e:/nanjing_poi.xlsx')
    wb.close()
    print('>>> ok!')


if __name__ == '__main__':
    search_poi(['银行', '酒店'], coord_type='wgs84ll')
