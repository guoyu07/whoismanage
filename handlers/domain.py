# encoding:utf-8
"""
功能：域名数量统计所需数据
"""

import decimal
import tornado
import json
from models.domain_db import DomainDb

PATH = './domain/'  # 模板地址


class DomainIndexHandler(tornado.web.RequestHandler):
    """各个顶级后缀域名数量统计"""

    def get(self):
        domains, total = DomainDb().fetch_domain(11)
        self.render(
            PATH + 'domain_overall.html',
            domains=json.dumps(domains),
            total=total
        )


class DomainTldIndexHandler(tornado.web.RequestHandler):
    """
    获取指定顶级域名后缀首页
    """
    def get(self):
        self.render(PATH+'domain_tld.html')


class DomainTldNumHandler(tornado.web.RequestHandler):
    """
    获取指定顶级域名后缀的域名数量
    """
    def get(self):
        tld = self.get_argument('tld','None')
        # total,tld_num,whois_tld,whois_total = DomainDb().get_tld_num(tld)
        results = DomainDb().get_tld_num(tld)
        self.write(json.dumps(results, cls=DecimalEncoder))


class DecimalEncoder(json.JSONEncoder):
    """
    解决json.dumps不能格式化Decimal问题
    """
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)