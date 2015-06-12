# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CompanyServiceItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    item_type = scrapy.Field()
    url = scrapy.Field()
    site_url = scrapy.Field()
    site_name = scrapy.Field()
    site_id = scrapy.Field()
    patch_id = scrapy.Field()
    validate = scrapy.Field()

class BiddingItem(CompanyServiceItem):
    body = scrapy.Field()
    webtype = scrapy.Field()
    title = scrapy.Field()
