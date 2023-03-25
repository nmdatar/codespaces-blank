import pandas as pd
import scrapy
import datetime

begin_date = datetime.datetime(2023, 1, 1)
end_date = datetime.datetime(2023, 2, 28, 23, 59)
base_url = 'https://www.japantimes.co.jp'
stored_articles = []

class JapanTimes(scrapy.Spider):
    """
    iterate through and scrape Japan Times
    """
    name = "japan_times"

    start_urls = [
        "https://www.japantimes.co.jp/news/world/"
    ]

    def parse(self, response):
        # print(len(stored_articles))
        articles = response.css('div.main_content article.story.archive_story.single_block')
        titles = []
        dates_times = []
        next_pages = []
        for article in articles:
            titles.append(article.css('p a::text').get())
            dates_times.append(article.css('h3 span.right.date::text').get())
            next_pages.append(article.css('p a::attr(href)').get())

        for title, date_time, page in zip(titles, dates_times, next_pages):
            if begin_date <= datetime.datetime.strptime(date_time, '%b %d, %Y') <= end_date:
                data = [title, date_time]
                yield scrapy.Request(url=page, callback=self.get_article_text, meta={'data' : data})
        
            
        if datetime.datetime.strptime(dates_times[-1], '%b %d, %Y') < begin_date:
                print(len(stored_articles))
        
        else:
            new_page = response.css('span.pages a::attr(href)').getall()[-1]
            if new_page is not None:
                if not new_page.startswith('https'):
                    new_page = base_url + new_page
                yield scrapy.Request(url=new_page, callback=self.parse)
                
    def get_article_text(self, response):
        title = response.meta['data'][0]
        date_time = response.meta['data'][1]

        text = response.css('div#jtarticle.entry > p:nth-of-type(-n+3)::text').getall()
        text = [paragraph.strip() for paragraph in text]

        content = " ".join(text)
        author = response.css('div.single-upper-meta h5.writer a::text').getall()
        author_agency = response.css('div.single-upper-meta p.credit::text').get()
        # print(author_agency)
        if author is not None and author != []:
            print(author)
            author = ", ".join(author)
            print(author)
            author_agency = author + ", " + author_agency
            print(author_agency)
        entry = {
            'Title' : title,
            'Content' : content,
            'Author' : author_agency,
            'Date and Time' : date_time,
        }
        
        stored_articles.append(entry)

    def closed(self, reason):
        df = pd.DataFrame(stored_articles)
        df['Date and Time'] = pd.to_datetime(df['Date and Time'], format='%b %d, %Y')
        df.sort_values(by='Date and Time', inplace=True)
        df.to_csv('assignment/japan_times.csv')