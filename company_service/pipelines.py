# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from twisted.enterprise import adbapi
from scrapy.utils.project import get_project_settings 
import json, md5, MySQLdb, logging
 
settings = get_project_settings()
 
class CompanyServicePipeline(object):
    
    def __init__(self):
        dbargs = settings.get('DB_CONNECT')
        db_server = settings.get('DB_SERVER')
        dbpool = adbapi.ConnectionPool(db_server, **dbargs)
        self.dbpool = dbpool 
    
    def __del__(self):
        self.dbpool.close() 
    
    def process_item(self, item, spider):
        url = item.get('url')
        sql = (
            'SELECT data_validate '
            'FROM data '
            'WHERE data_url = %s LIMIT 1'
        )
        def get_data(rows, item=item):
            site_id = item.get('site_id')
            item_type = item.get('item_type')
            title = item.get('title')
            patch_id = item.get('patch_id')
            item_str = json.dumps(dict(item)) 
            url = item.get('url')
            item_md5 = md5.new(str(item_str)).hexdigest()
            item['validate'] = item_md5
            if rows is not None:
                validate = rows['data_validate']
                if validate == item_md5:
                    return 
            sql = (
                'INSERT INTO data '
                'VALUES('
                'null, '
                '%s, %s, '
                '{site_id}, '
                '%s, %s, ' 
                '{patch_id}, %s) '
                'ON DUPLICATE KEY '
                'UPDATE data_id = LAST_INSERT_ID(data_id), '
                'data_content = values(data_content), '
                'data_validate = values(data_validate), '
                'data_type = values(data_type), '
                'data_title = values(data_title)'
            ).format(
                site_id=site_id,
                patch_id=patch_id,
            )
            self.dbpool.runOperation(
                sql, 
                (item_str, item_md5, item_type, url, title),
            )

        defer = self.dbpool.runOperation(sql, url)
        defer.addCallbacks(get_data)

        return item
