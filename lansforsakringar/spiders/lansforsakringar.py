import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from lansforsakringar.items import Article


class LansforsakringarSpider(scrapy.Spider):
    name = 'lansforsakringar'
    start_urls = ['https://www.lansforsakringar.se/bergslagen/privat/om-oss/press-media/nyheter/']

    def parse(self, response):
        links = response.xpath('//article/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//nav//a[@class="arrow-right"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()
        else:
            return

        date = response.xpath('//time/@datetime').get()
        if date:
            date = date.strip()

        content = response.xpath('//article//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[3:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
