from math import ceil

import pandas as pd
import requests


class BaiduMap:
    def __init__(self, ak):
        self.ak = ak

    def fetch(self, url, **kwargs):
        kwargs['ak'] = self.ak
        return requests.get(url, kwargs).json()

    def transit(self, origin, destination, **kwargs):
        """公交路线规划
        根据起点和终点检索符合条件的公共交通方案，
        融入出行策略（少换乘、地铁优先等），
        支持大陆区域的同城及跨城路线规划，
        交通方式支持公交、地铁、火车、飞机、大巴。
        :param origin: 纬度,经度组成的tuple或list，小数点后不超过6位，如：(40.056878,116.30815)
        :param destination: 同上
        :param coord_type: string 起终点的坐标类型 "bd09ll"(默认) / "gcj02" / "wgs84"
        :param tactics_incity: int(0-5) 市内公交换乘策略 0(默认) 推荐；1 少换乘；2 少步行；3 不坐地铁；4 时间短；5 地铁优先
        :param tactics_intercity: int(0-2) 跨城公交换乘策略 0(默认):时间短；1 出发早；2 价格低
        :param trans_type_intercity: int(0-2) 跨城交通方式策略 0(默认):火车优先；1:飞机优先；2:大巴优先
        :param ret_coordtype: string 返回值的坐标类型 "bd09ll"(默认) / "gcj02"
        """
        url = 'http://api.map.baidu.com/direction/v2/transit'
        origin = ','.join(map(str, origin))
        destination = ','.join(map(str, destination))
        return self.fetch(url, origin=origin, destination=destination,
                          **kwargs)

    def driving(self, origin, destination, **kwargs):
        """驾车路线规划
        根据起点和终点检索符合条件的公共交通方案，
        融入出行策略（少换乘、地铁优先等），
        支持大陆区域的同城及跨城路线规划，
        交通方式支持公交、地铁、火车、飞机、大巴。
        :param origin: 纬度,经度组成的tuple或list，小数点后不超过6位，如：(40.056878,116.30815)
        :param destination: 同上
        :param origin_uid: 可选。POI 的 uid（在已知起点POI 的 uid 情况下，请尽量填写uid，将提升路线规划的准确性）
        :param destination_uid: 同上
        :param coord_type: string 起终点的坐标类型 "bd09ll"(默认) / "gcj02" / "wgs84"
        :param tactics: int(0-11) 策略 0(默认) 推荐；详情请查阅百度地图web API文档
        :param alternative: int(0-1) 是否返回备选路线 0(默认):返回一条推荐路线；1 返回1-3条路线供选择
        :param plate_number: 车牌号，如"京A00022", 用于规避车牌号限行路段。
        """
        url = 'http://api.map.baidu.com/direction/v2/driving'
        origin = ','.join(map(str, origin))
        destination = ','.join(map(str, destination))
        return self.fetch(url, origin=origin, destination=destination,
                          **kwargs)

    def duration(self, origin, destination, by=0, **kwargs):
        """通勤所需时间
        :param by: 0(默认) 驾车; 1 公交
        """
        func = [self.driving, self.transit][by]
        res = func(origin, destination, **kwargs)
        if res['status'] == 0:
            res = res['result']
            try:
                duration = res['routes'][0]['duration']
            except Exception:
                print('>>> No info.')
                duration = None

        print(f'>>>{origin} TO {destination}: {duration}')
        return duration

    def search(self, query, **kwargs):
        """地点检索服务
        详见http://lbsyun.baidu.com/index.php?title=webapi/guide/webservice-placeapi
        """
        url = 'http://api.map.baidu.com/place/v2/search'
        return self.fetch(url, query=query, output='json', scope=2, page_size=20, **kwargs)

    def search_bounds(self, query, bounds, **kwargs):
        """矩形区域检索
        :param query: string, tuple, list 检索关键字。多个关键字用tuple或list传入
        :param bounds: tuple or list [lat, lng(左下角坐标), lat, lng(右上角坐标)]
        """
        query = query if isinstance(query, str) else '$'.join(query)
        bounds = ','.join(map(str, bounds))
        df = pd.DataFrame()

        total = self.search(query, bounds=bounds, **kwargs)['total']
        try:
            if total > 0:
                # 遍历每一页
                for page in range(ceil(total / 20)):
                    item = {}
                    # 遍历一页中每条记录
                    for each in self.search(query, bounds=bounds, page_num=page, **kwargs)['results']:
                        item['uid'] = each['uid']
                        item['name'] = each['name']
                        item['lat'] = each['location']['lat']
                        item['lng'] = each['location']['lng']
                        item['address'] = each['address']
                        item['tag'] = each['detail_info']['tag']
                        df = df.append(item, True)
        except:
            print(self.search(query, bounds=bounds, page_num=page, **kwargs))
            df = input('>>>')

        return df
