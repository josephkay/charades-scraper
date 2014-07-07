import unicodecsv as csv
from scrapy import signals
from scrapy import log

class CSVPipeline(object):
    
    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
        crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
        return pipeline
    
    def spider_opened(self, spider):
        self.output_file = open("output.csv", "wb")
        self.writer = csv.writer(self.output_file)
        
    def process_item(self, item, spider):
        row = [item['title'], item['person'], item['rating'], item['votes'], item['language'], item['genres'], item['description']]
        self.writer.writerow(row)
        return item
    
    def spider_closed(self, spider):
        self.output_file.close()