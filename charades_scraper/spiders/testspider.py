import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from pprint import pprint
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.conf import settings
from urlparse import urlparse
from charades_scraper.items import CharadesItem
from scrapy import log
from scrapy.log import ScrapyFileLogObserver
import logging
from bs4 import BeautifulSoup as bs
from bs4 import NavigableString, Tag

seed_urls = [
    "http://www.metacritic.com/browse/movies/score/userscore/all"
]
allowed_domains = [
    'www.metacritic.com'
]
exclude_domains = []


class TestSpider(CrawlSpider):
    name = "test"
    allowed_domains = allowed_domains
    # LEAVE OFF THE TRAILING SLASH!!!!
    start_urls = seed_urls

    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=('//li[contains(concat(" ", normalize-space(@class), " "), " movie_product ")]'), allow=(), deny=(), allow_domains=allowed_domains, deny_domains=exclude_domains), callback='parse_item', follow=False),
    )
    
    def __init__(self, **kwargs):
        ScrapyFileLogObserver(open("debug.log", 'w'), level=logging.DEBUG).start()
        ScrapyFileLogObserver(open("error.log", 'w'), level=logging.ERROR).start()
        ScrapyFileLogObserver(open("info.log", 'w'), level=logging.INFO).start()
        CrawlSpider.__init__(self, **kwargs)
    
    def parse_item(self, response):

        log.msg("WORKING")
        return

spider = TestSpider()