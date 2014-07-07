# Scrapy settings for charades_scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'charades_scraper'

SPIDER_MODULES = ['charades_scraper.spiders']
NEWSPIDER_MODULE = 'charades_scraper.spiders'

ITEM_PIPELINES = [
	'charades_scraper.pipelines.CSVPipeline'
]

DEPTH_LIMIT = 1

#DOWNLOADER_MIDDLEWARES = {
#    'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware' : None,
#    'charades_scraper.comm.rotate_useragent.RotateUserAgentMiddleware' : 400
#}