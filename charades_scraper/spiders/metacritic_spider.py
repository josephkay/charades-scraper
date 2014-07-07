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
import urllib2

seed_urls = [
    "http://www.metacritic.com/browse/movies/score/userscore/all"
]
allowed_domains = [
    'www.metacritic.com'
]
exclude_domains = []


class MetacriticSpider(CrawlSpider):
    name = "metacritic"
    allowed_domains = allowed_domains
    # LEAVE OFF THE TRAILING SLASH!!!!
    start_urls = seed_urls

    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=('//span[contains(concat(" ", normalize-space(@class), " "), " next ")]'), allow=(), deny=(), allow_domains=allowed_domains, deny_domains=exclude_domains), follow=True),
        Rule(SgmlLinkExtractor(restrict_xpaths=('//li[contains(concat(" ", normalize-space(@class), " "), " movie_product ")]'), allow=(), deny=(), allow_domains=allowed_domains, deny_domains=exclude_domains), callback='parse_item', follow=False),
    )
    
    def __init__(self, **kwargs):
        ScrapyFileLogObserver(open("debug.log", 'w'), level=logging.DEBUG).start()
        ScrapyFileLogObserver(open("error.log", 'w'), level=logging.ERROR).start()
        ScrapyFileLogObserver(open("info.log", 'w'), level=logging.INFO).start()
        CrawlSpider.__init__(self, **kwargs)
    
    def get_text(self, html, ignores=[]):
        if not html:
            return ""
        if isinstance(html, NavigableString):
            return html
        if type(html) is Tag:
            if "class" in html.attrs:
                for class_item in ignores:
                    if class_item in html['class']:
                        #log.msg("more/less found")
                        return ""
        try:
            contents = html.contents
        except Exception, e:
            log.msg("Could not retrieve contents: {0}".format(e))
            return ""
        texts = []
        for x in contents:
            texts.append(self.get_text(x, ignores))
        return "".join([text for text in texts])
    
    def parse_item(self, response):

        urlp = urlparse(response.url)
    
        soup = bs(response.body_as_unicode())
            
        try:
            title = soup.find("div", class_="product_title").find("span", itemprop="name").contents[0].strip()
            director = soup.find("li", itemprop="director").find("span", itemprop="name").contents[0].strip()
            genres = soup.find("li", class_="product_genre").find_all("span", itemprop="genre")
            genres_text = ", ".join([genre.contents[0].strip() for genre in genres])
            userscore_wrap = soup.find("div", class_="product_scores").find("div", class_="side_details").find("div", class_="userscore_wrap")
            rating = userscore_wrap.find("div", class_="user").contents[0].strip()
            votes = userscore_wrap.find("span", class_="count").find("a").contents[0].strip().split()[0]
            
            description_obj = soup.find("span", itemprop="description")
            description_list = description_obj.contents
            span_list = [x for x in description_list if x.name == "span"]
            description = self.get_text(description_obj, ignores=["toggle_expand_collapse", "blurb_etc"]).strip()

            details_req = urllib2.Request("{0}/details".format(response.url), headers={'User-Agent': 'Mozilla/5.0'})
            details = urllib2.urlopen(details_req).read()
            details_soup = bs(details)
            details_rows = details_soup.find_all("div", class_="product_details")[1].find("table").find_all("tr")
            
            main_language = "unknown"
            for row in details_rows:
                row_name = row.find("th").contents[0]
                if "Lang" in row_name:
                    try:
                        languages = row.find("td").contents[0].strip().split(", ")
                        main_language = languages[0]
                    except Exception, e:
                        log.msg("Couldn't find a language: {0}".format(e), level=logging.ERROR)
                    break
            
            log.msg("title: {0}".format(title.encode("utf-8", errors="ignore")))
            log.msg("director: {0}".format(director.encode("utf-8", errors="ignore")))
            log.msg("rating: {0}".format(rating.encode("utf-8", errors="ignore")))
            log.msg("votes: {0}".format(votes.encode("utf-8", errors="ignore")))
            log.msg("genres: {0}".format(genres_text.encode("utf-8", errors="ignore")))
            log.msg("main language: {0}".format(main_language.encode("utf-8", errors="ignore")))
            log.msg("description: {0}".format(description.encode("utf-8", errors="ignore")))
            
        except Exception, e:
            log.msg("Problem with URL: {0}".format(response.url), level=logging.ERROR)
            log.msg("Couldn't find something: {0}".format(e), level=logging.ERROR)
            return
            
        item = CharadesItem()
        item['type'] = u"film"
        item['title'] = title
        item['person'] = director
        item['genres'] = genres_text
        item['rating'] = int(float(rating)*50)
        item['votes'] = int(votes)
        item['description'] = description
        item['language'] = main_language
        
        print "processed " + response.url
        return item

spider = MetacriticSpider()