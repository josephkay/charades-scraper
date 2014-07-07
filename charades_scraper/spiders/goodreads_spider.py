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
        Rule(SgmlLinkExtractor(restrict_xpaths=('//table[@class="tableList"]'), allow=(), deny=('.*/list/comments/*', '.*/topic/*', '.*/author/*'), allow_domains=allowed_domains, deny_domains=exclude_domains), callback='parse_item', follow=False),
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
    
    def normalise_whitespace(self, text):
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)
        return text
    
    def parse_item(self, response):
    
        soup = bs(response.body_as_unicode())
            
        try:
            title = soup.find("h1", class_="bookTitle").contents[0].strip()
            authors = soup.find("div", id="bookAuthors").find("span", itemprop="author").find_all("a", class_="authorName")
            authors_text = ", ".join([author.find("span", itemprop="name").contents[0].strip() for author in authors])
            rating = soup.find("span", itemprop="ratingValue").contents[0].strip()
            votes = soup.find("span", itemprop="ratingCount")['title']
            description_obj = soup.find("div", id="description")
            description_list = description_obj.contents
            span_list = [x for x in description_list if x.name == "span"]
            description = self.get_text(span_list[-1], ignores=["actionLinkLite"]).strip()
            details_rows = soup.find("div", id="bookDataBox").find_all("div", class_="clearFloats")
            language = "unknown"
            for row in details_rows:
                row_name = row.find("div", class_="infoBoxRowTitle").contents[0]
                if "lang" in row_name:
                    try:
                        language = row.find("div", class_="infoBoxRowItem").contents[0].strip()
                    except Exception, e:
                        log.msg("Couldn't find a language: {0}".format(e), level=logging.ERROR)
                    break
            
            boxes = soup.find_all("div", class_="bigBox")
            genres = "unknown"
            for box in boxes:
                header_container = box.find("div", class_="h2Container")
                if header_container:
                    header = self.get_text(header_container)
                else:
                    continue
                    
                if header == "Genres":
                    genres_list = box.find("div", class_="bigBoxContent").find_all("div", class_="elementList")
                    if len(genres_list) > 3:
                        genres_list = genres_list[:3]
                    
                    genres_list = [self.normalise_whitespace(self.get_text(g.find("div", class_="left"))).replace(">", "-") for g in genres_list]
                    
                    if genres_list:
                        genres = ", ".join(genres_list)
                    break
            
            log.msg("title: {0}".format(title.encode("utf-8", errors="ignore")))
            log.msg("authors: {0}".format(authors_text.encode("utf-8", errors="ignore")))
            log.msg("rating: {0}".format(rating.encode("utf-8", errors="ignore")))
            log.msg("votes: {0}".format(votes))
            log.msg("genres: {0}".format(genres.encode("utf-8", errors="ignore")))
            log.msg("language: {0}".format(language.encode("utf-8", errors="ignore")))
            log.msg("description: {0}".format(description.encode("utf-8", errors="ignore")))
            
        except Exception, e :
            log.msg("Problem with URL: {0}".format(response.url), level=logging.ERROR)
            log.msg("Couldn't find something: {0}".format(e), level=logging.ERROR)
            return
            
        item = CharadesItem()
        item['type'] = u"book"
        item['title'] = title
        item['person'] = authors_text
        item['rating'] = int(float(rating)*100)
        item['votes'] = int(votes)
        item['description'] = description
        item['language'] = language
        item['genres'] = genres
        
        print "processed " + response.url
        return item

spider = GoodreadsSpider()