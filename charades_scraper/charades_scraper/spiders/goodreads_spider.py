import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from pprint import pprint
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.conf import settings
from urlparse import urlparse
from charades_spider.items import CharadesItem
from scrapy import log
from scrapy.log import ScrapyFileLogObserver
import logging
from bs4 import BeautifulSoup as bs
from bs4 import NavigableString, Tag

seed_urls = [
    "https://www.goodreads.com/list/show/7",
    "https://www.goodreads.com/list/show/6",
    "https://www.goodreads.com/list/show/16",
    "https://www.goodreads.com/list/show/30",
    "https://www.goodreads.com/list/show/53",
    "https://www.goodreads.com/list/show/52"
]
allowed_domains = [
    'www.goodreads.com'
]
exclude_domains = []


class GoodreadsSpider(CrawlSpider):
    name = "goodreads"
    allowed_domains = allowed_domains
    # LEAVE OFF THE TRAILING SLASH!!!!
    start_urls = seed_urls

    rules = (
        Rule(SgmlLinkExtractor(restrict_xpaths=('//div[@class="pagination"]'), allow=(), deny=('.*/list/comments/*'), allow_domains=allowed_domains, deny_domains=exclude_domains), follow=True),
        Rule(SgmlLinkExtractor(restrict_xpaths=('//table[@class="tableList"]'), allow=(), deny=('.*/list/comments/*', '.*/topic/*'), allow_domains=allowed_domains, deny_domains=exclude_domains), callback='parse_item', follow=False),
    )
    
    def __init__(self, **kwargs):
        ScrapyFileLogObserver(open("debug.log", 'w'), level=logging.DEBUG).start()
        ScrapyFileLogObserver(open("error.log", 'w'), level=logging.ERROR).start()
        ScrapyFileLogObserver(open("info.log", 'w'), level=logging.INFO).start()
        CrawlSpider.__init__(self, **kwargs)
    
    def get_text(self, html):
        if not html:
            return ""
        if isinstance(html, NavigableString):
            return html
        if type(html) is Tag:
            if "class" in html.attrs:
                if "actionLinkLite" in html['class']:
                    #log.msg("more/less found")
                    return ""
        try:
            contents = html.contents
        except Exception, e:
            log.msg("Could not retrieve contents: {0}".format(e))
            return ""
        texts = []
        for x in contents:
            texts.append(self.get_text(x))
        return "".join([text for text in texts])
    
    def parse_item(self, response):
        items = []

        urlp = urlparse(response.url)
        #domain = urlp.netloc
        #d = domain.strip()

        #ist2 = re.search('<a href="category/type-2-diabetes\.25/">Type 2 Diabetes</a>', response.body)
        #if not ist2 :
        #    return items

        #hxs = HtmlXPathSelector(response)
        #try :
        #    threads = hxs.select('//*[contains(concat(" ", normalize-space(@class), " "), " messageInfo ")]').extract()
        #except AttributeError :
        #    log.msg("Couldn't find threads")
        #    return items
    
        soup = bs(response.body_as_unicode())
            
        try:
            title = soup.find("h1", class_="bookTitle").contents
            authors = soup.find("div", id="bookAuthors").find("span", itemprop="author").find_all("a", class_="authorName")
            authors_text = ", ".join([author.find("span", itemprop="name").contents for author in authors])
            rating = soup.find("span", itemprop="ratingValue").contents
            votes = soup.find("span", itemprop="ratingCount").title
            description_obj = soup.find("div", id="description")
            #description_list = description_obj.contents
            description = self.get_text(description_obj)
            
            log.msg("title: {0}".format(title.encode("utf-8", errors="ignore")))
            log.msg("authors: {0}".format(authors_text.encode("utf-8", errors="ignore")))
            log.msg("rating: {0}".format(rating.encode("utf-8", errors="ignore")))
            log.msg("votes: {0}".format(votes.encode("utf-8", errors="ignore")))
            log.msg("description: {0}".format(description.encode("utf-8", errors="ignore")))
            
        except Exception, e :
            log.msg("Problem with URL: {0}".format(response.url), level=logging.ERROR)
            log.msg("Couldn't find something: {0}".format(e), level=logging.ERROR)
            continue
            
        item = DiabetescoukItem()
        item['title'] = title
        item['authors'] = authors_text
        item['rating'] = rating
        item['votes'] = votes
        item['description'] = description
        
        print "processed " + response.url
        return items

spider = GoodreadsSpider()