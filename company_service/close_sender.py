# -*- coding: utf-8 -*-
# 
# Author: jimin.huang
# 
# Created Time: 2015年02月07日 星期六 17时01分29秒
# 

from scrapy import signals
from scrapy.mail import MailSender
from scrapy.exceptions import NotConfigured


class CloseSender(object):
    def __init__(self, stats, recipients, mail):
        self.stats = stats
        self.recipients = recipients
        self.mail = mail

    @classmethod
    def from_crawler(cls, crawler):
        recipients = crawler.settings.getlist("STATSMAILER_RCPTS")
        if not recipients:
            raise NotConfigured
        mail = MailSender.from_settings(crawler.settings)
        o = cls(crawler.stats, recipients, mail)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        return o
    
    def spider_closed(self, spider):
        spider_stats = self.stats.get_stats(spider)
        body = "Global stats\n\n"
        body += "\n".join("%-50s : %s" % i for i in self.stats.get_stats().items())
        body += "\n\n%s stats\n\n" % spider.name
        body += "\n".join("%-50s : %s" % i for i in spider_stats.items())
        body += ''.join((
            "\n",
            '爬取网站 : {name}'.format(name=spider.site_name.encode('utf8')),
            "\n",
            '爬取地址 : {url}'.format(url=spider.site_url)
        ))
        return self.mail.send(self.recipients, "Scrapy stats for: %s" % spider.name, body)
