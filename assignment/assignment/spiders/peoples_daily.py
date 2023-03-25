import scrapy
import datetime
import pandas as pd

begin_date = datetime.datetime(2023, 1, 1)
end_date = datetime.datetime(2023, 2, 28, 23, 59)
base_url = 'http://en.people.cn/'
stored_articles = []

class PeoplesDaily(scrapy.Spider):
    """
    iterate through and scrape people's daily
    """
    name = "peoples_daily"

    start_urls = [
        "http://en.people.cn/90777/index.html"
    ]

    def parse(self, response):
        # print(len(stored_articles))
        articles = response.css('ul.foreign_list8.cf')[0]
        titles = articles.css('li a::text').getall()
        dates_times = articles.css('li span::text').getall()
        next_pages = articles.css('li a::attr(href)').getall()

        for title, date_time, page in zip(titles, dates_times, next_pages):
            if begin_date <= datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M') <= end_date:
                url = base_url + page
                data = [title, date_time]
                yield scrapy.Request(url=url, callback=self.get_article_text, meta={'data' : data})
        
            
        if datetime.datetime.strptime(dates_times[-1], '%Y-%m-%d %H:%M') < begin_date:
                print(len(stored_articles))
        
        else:
            new_page = response.css('div.page_n.clearfix a::attr(href)').getall()[-1]
            if new_page is not None:
                new_url = response.urljoin(new_page)
                yield scrapy.Request(url=new_url, callback=self.parse)
    
    def get_article_text(self, response):
        title = response.meta['data'][0]
        date_time = response.meta['data'][1]

        article = response.css('div.w860.d2txtCon.cf')[0]
        text = article.css('p::text').getall()
        text = [paragraph.strip() for paragraph in text]

        content = " ".join(text)
        author = article.css('div.origin.cf a::text').get()
        if author is None:
            author = article.css('div.origin.cf::text').get()

        entry = {
            'Title' : title,
            'Content' : content,
            'Author' : author,
            'Date and Time' : date_time,
        }
        
        stored_articles.append(entry)

    def closed(self, reason):
        df = pd.DataFrame(stored_articles)
        df.sort_values(by='Date and Time', inplace=True)
        df.to_csv('assignment/peoples_daily.csv')