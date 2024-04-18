import scrapy
from scrapy import Request
import scrapy.http

class AnimeScraper(scrapy.Spider):
    name = 'anime'
    start_urls = ['https://myanimelist.net/topanime.php']
    page = 0
    
    def parse(self, response: scrapy.http.Response):
        for animes in response.css ('tr.ranking-list'):
            link = animes.css('a.hoverinfo_trigger::attr(href)').get()
            yield response.follow(link, callback=self.parse_anime_page)
            
        next_page = response.css('a.link-blue-box.next::attr(href)').get()
        if next_page is not None and self.page < 2:
            next_page_url = response.urljoin(next_page)
            self.page += 1
            yield response.follow(next_page_url, callback=self.parse)
            
    def parse_anime_page(self, response: scrapy.http.Response):
        rank = response.css('span.numbers.ranked > strong::text').get()
        title = response.css('h1.title-name.h1_bold_none > strong::text').get()
        image_url = response.css('div.leftside > div:first-child > a > img::attr(data-src)').get()
        rating = response.css('div.score-label::text').get()
        genre = response.css('span[itemprop="genre"]::text').getall()
        rilis = response.xpath('//div[contains(span[@class="dark_text"], "Aired:")]/text()').getall()
        available = response.css('div.broadcast > a > div.caption::text').getall()
        character = response.css('td.borderClass > h3.h3_characters_voice_actors > a::text').getall()
        
        yield {
            'rank': rank[1:],
            'title': title,
            'url': response.url,
            'image_url': image_url,
            'rating': rating,
            'genre': genre,
            'rilis': rilis[1].strip()[:12] if len(rilis) > 1 else None,
            'available': available,
            'character':character,
        }