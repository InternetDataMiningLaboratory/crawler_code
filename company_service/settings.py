# -*- coding: utf-8 -*-

# Scrapy settings for company_service project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#
import os

BOT_NAME = 'company_service'

SPIDER_MODULES = ['company_service.spiders']
NEWSPIDER_MODULE = 'company_service.spiders'

ITEM_PIPELINES = {
    'company_service.pipelines.CompanyServicePipeline': 300
}

DB_SERVER = 'MySQLdb'
DB_CONNECT = {
    'db' : 'contribute_crawler',
    'host' : 'mysql',
    'user' : os.getenv("DATABASE_USER"),
    'passwd' : os.getenv("DATABASE_PASSWD")
    'charset' : 'utf8',
}
EXTENSIONS = {
    'company_service.patch.PatchGenerator' : 300,
    'company_service.close_sender.CloseSender' : 500,
}

STATSMAILER_RCPTS = [
    'windworship2@163.com',
    '258831720@qq.com'
]
MAIL_FROM = os.getenv("MAIL_USER")
MAIL_HOST = 'smtp-mail.outlook.com'
MAIL_USER = os.getenv("MAIL_USER")
MAIL_PASS = os.getenv("MAIL_PASSWD")

WEBSERVICE_HOST = '0.0.0.0'
WEBSERVICE_LOGFILE = 'web.log'
# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'company_service (+http://www.yourdomain.com)'
