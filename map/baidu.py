import requests
import json


class API:
    def __init__(self, ak):
        self.ak = ak

    def fetch(self, url, **kwargs):
        kwargs['ak'] = self.ak
        return requests.get(url, kwargs).json()


class Direction(API):
    """路线规划服务
    又名Direction API，是一套REST风格的Web服务API，以HTTP/HTTPS形式提供了路线规划功能，是Direction API v1.0的升级版本。
    目前，Direction API v2.0率先对外开放了公交线路规划功能：
    全面支持跨城公交路线规划
    支持 公交、地铁、火车、飞机、城际大巴多种公共出行方式。
    """

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

    def transit_cost(self, origin, destination, **kwargs):
        """所需时间、均价
        """
        res = self.transit(origin, destination, **kwargs)
        if res['status'] == 0:
            res = res['result']
            (public_duration, public_price) = (res['routes'][0]['duration'], res['routes'][0]['price']) if res['routes'] \
                else (None, None)
            (taxi_duration, taxi_price) = (res['taxi']['duration'], res['taxi']['detail'][0]['total_price']) if res[
                'taxi'] \
                else (None, None)
            return public_duration, public_price, taxi_duration, taxi_price
        else:
            return None, None, None, None