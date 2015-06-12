# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年01月31日 星期六 10时36分11秒
# 
import scrapy,re
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.http import Request, FormRequest
from scrapy.utils.project import get_project_settings
from scrapy import log


class BasicSpider(CrawlSpider):
    
    def parse_rule(self, rule):
        #start url
        self.start_urls = rule['start_url']

        #next url
        self.parse_start_url = self.hand_out(rule['next']) 

        #item
        self.hand_out(rule['item'])
    
    def hand_out(self, rule):
        def _Rule(rule):
            self.rules += (
                Rule(
                    LinkExtractor(
                        allow=(rule['allow'], )
                    ),
                    callback = self.hand_out(rule['callback'])
                ),
            )       
        
        def _Request(rule, form=False):
            def _response(response, rule=rule):
                url = rule['url']
                real_parameters = dict()
                rule_parameters = rule['parameter'] if not form else rule['formdata']
                for parameter, value in rule_parameters.iteritems():
                    if isinstance(value, dict):
                        value = self.hand_out(value)(response)
                        if isinstance(value, list):
                            value = value.pop()
                    real_parameters[parameter] = str(value)
                if form:
                    return FormRequest(
                        url=url,
                        formdata=real_parameters,
                        callback=self.hand_out(rule['callback']) if 'callback' in rule else None,
                    ) 
                if rule['dynamic']:
                    parameter = '&'.join(map('='.join, real_parameters.iteritems()))
                    url = ''.join((url, '?', parameter))
                return Request(url=url)
            return _response
        
        def _FormRequest(rule):
            return _Request(rule, form=True)
        
        def _callback(rule):
            def _call(response, rule=rule):
                item = None
                if rule['item'] == 'meta':
                    item = response.meta['item']
                else:
                    name = 'company_service.items'
                    module = None
                    try:
                        module = __import__(name, fromlist=[rule['item']])
                    except ImportError:
                        print 'import error'
                    item_class = getattr(module, rule['item'])
                    item = item_class()
                    item['item_type'] = rule['item']
                    item['url'] = response.url
                    item['site_url'] = self.site_url
                    item['site_name'] = self.site_name
                    item['site_id'] = self.site_id
                    item['patch_id'] = self.patch_id

                for add_value in rule['add']:
                    item[add_value] = self.hand_out(rule[add_value])(response)
                
                if 'last' in rule:
                    last = self.hand_out(rule['last'])(response)
                    last.meta['item'] = item
                    return last
                log.msg(item['title'].encode('utf8'), level=log.INFO) 
                return item 
            return _call                
        
        def _css(rule):
            def _response(response):
                result = response.css(rule['css'])
                if 're' in rule:
                    result = result.re(rule['re'])
                else:
                    result = result.extract()[0]
                return result
            return _response
        
        def _url(rule):
            def _source(source):
                pattern = re.compile(rule['re'])
                return pattern.search(source.url).group(1)
            return _source

        return locals()['_' + rule['type']](rule)

    name = 'BasicCrawler'
        
    def __init__(self, rule_id=None, patch_id=None, *a, **kw):
        self.patch_id = patch_id
        self.rule_id = rule_id

        import MySQLdb
        conn = MySQLdb.connect(**get_project_settings().get('DB_CONNECT'))
        cursor = conn.cursor()
        sql =\
        (
            'SELECT rule_content, site_url, site_name, site_id FROM '
            'rule NATURAL JOIN website '
            'WHERE rule_id = {rule_id} '
        ).format(rule_id=rule_id)
        cursor.execute(sql)
        crawler = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if not crawler:
            return
        import json
        rules = json.loads('\\\\'.join(crawler[0].split('\\')))
        self.site_url = crawler[1]
        self.site_name = crawler[2]
        self.site_id = crawler[3]

        self.parse_rule(rules)
        super(BasicSpider, self).__init__(*a, **kw)
