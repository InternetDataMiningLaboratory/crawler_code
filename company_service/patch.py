# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年04月25日 星期六 13时55分06秒
# 

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy import log
import MySQLdb, json


class PatchGenerator(object):
    def __init__(self, db_settings):
        self.db_settings = db_settings

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.get("DB_CONNECT")
        if not db_settings:
            raise NotConfigured

        patch_generator = cls(db_settings)

        crawler.signals.connect(
            patch_generator.spider_closed,
            signal=signals.spider_closed
        )

        return patch_generator

    def spider_closed(self, spider):
        patch_set = []
        db_connection = MySQLdb.connect(**self.db_settings)
        cursor = db_connection.cursor()
        
        sql =\
            (
                'SELECT data_validate '
                'FROM data '
                'WHERE data_patch = {patch_id}'
            ).format(patch_id=spider.patch_id)
        cursor.execute(sql)
        results = cursor.fetchall()
        if results:
            for result in results:
                patch_set.append(result[0])
        
        patch_set = json.dumps(patch_set)
        log.msg(patch_set, level=log.INFO) 

        sql =\
            (
                'UPDATE patch '
                'SET patch_set = %s '
                'WHERE patch_id = {patch_id}'
            ).format(patch_id=spider.patch_id)
        
        log.msg('start', level=log.INFO) 
        cursor.execute(sql, patch_set) 
        log.msg('end', level=log.INFO) 
        db_connection.commit()
        cursor.close()
        db_connection.close()
