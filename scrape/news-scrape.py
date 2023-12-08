from bs4 import BeautifulSoup
import requests
import csv
import sys
import chardet

if len(sys.argv) != 2:
    print('Usage: python3 news-srape.py <annapurna|gorkhapatra>')
    sys.exit(1)
    
choosen = sys.argv[1]
if choosen == "annapurna":
    # annapurna post section
    total_pages = 100
    scraped_link=[]
    count = 1
    for i in range(total_pages):
        try:
            response = requests.get(f'https://annapurnapost.com/category/politics/?page={i+1}').text
            soup = BeautifulSoup(response,'lxml')
            highlight = soup.find('div',class_='category__banner').a['href']
            scraped_link.append(highlight)
            news_grid = soup.find('div',class_='category__news-grid')
            news_collection = news_grid.find_all('div',class_='grid__card')
            print('Link: ',count)
            count+=1
            for news in news_collection:
                a_tag = news.find('div',class_='card__details').h3.a
                # a_tag_text = a_tag.text
                a_tag_link = a_tag['href']
                scraped_link.append(a_tag_link)
        except Exception as e:
            continue


    print(len(scraped_link))
    count = 1
    scraped_news = []
    for link in scraped_link:
        try:
            response = requests.get(f'https://annapurnapost.com{link}').text
            soup = BeautifulSoup(response,'lxml')
            news_content = soup.find('div',class_='ap__news-content')
            topic = news_content.a.text
            title = news_content.h1.text
            date = news_content.find('p',class_='date').text
            body = news_content.find('div',class_='news__details').text
            scraped_news.append((topic,date,title,body))
            print('Count: ',count)
            count+=1
        except Exception as e:
            continue

    with open('news.csv','a',encoding='UTF8') as f:
        writer = csv.writer(f)
        try:
            writer.writerow(('topic','date','title','body'))
            for news in scraped_news:
                writer.writerow(news)
        except Exception as e:
            print('Exception occurred while writing from annapurna post') 
        print('Success!!!')
elif choosen == "gorkhapatra":
    total_pages = 150
    scraped_link= []
    count = 1
    for i in range(total_pages):
        try:
            response = requests.get(f'https://gorkhapatraonline.com/categories/politics?page={i+1}').text
            soup = BeautifulSoup(response,'lxml')
            news_in_a_page = soup.find_all('h2',class_='item-title')
            for news in news_in_a_page:
                link = news.a['href']
                scraped_link.append(link)
            print('Done for Page: ',count)
            count+=1
        except Exception as e:
            continue
    
    # print(len(scraped_link))
    # print(scraped_link)
    scraped_news = []
    count = 1
    for link in scraped_link:
        try:
            response = requests.get(link).text
            soup = BeautifulSoup(response,'lxml')
            headline = soup.find('h1',class_='single-top-title').text
            content = soup.select_one(".single-blog-content")
            date = content.find('div').select_one('div > div:nth-of-type(2)').text
            body = content.select_one("div.blog-details:nth-of-type(4)").text
            topic = 'politics'
            information = (topic,date,headline,body)
            scraped_news.append(information)
            # print(scraped_news)
            print('Collected news: ',count)
            count+=1
        except Exception as e:
            print('in except block where link is:',link)
            continue

    with open('news-gorkhapatra.csv','a',encoding='UTF8') as f:
        writer = csv.writer(f)
        try:
            writer.writerow(('topic','date','title','body'))
            for news in scraped_news:
                writer.writerow(news)
            print('Success!!!')
        except Exception as e:
            print('Exception occurred while writing in gorkhapatra')
            sys.exit(1)
elif choosen == "setopati":
    # IMP/TODO: the \xao character is a lot inside the text of this setopati, that 
    # means the space character as said but if it impacts,need to take care of that 
    # thing.
    initial_page = 201
    final_page = 500
    scraped_link = []
    count = initial_page
    for i in range(initial_page,final_page+1):
        try:
            response = requests.get(f'https://www.setopati.com/politics?page={i}').text
            soup = BeautifulSoup(response,'lxml')
            if count == initial_page:
                # since the big item news is repeated 
                # in setopati across pages.
                big_item_link = soup.find('div',class_='big-feature').a['href']
                scraped_link.append(big_item_link)
            bishesh = soup.find_all('div',class_='bishesh')
            for i in bishesh:
                items = i.find_all('div',class_='items')
                for j in items:
                    link = j.a['href']
                    scraped_link.append(link)
            print(f'Setopati page:{count} done.')
            count+=1
        except Exception as e:
            print(f'Exception occurred on setopati at page: {count}')
            continue
    # print(scraped_link)
    # sys.exit(0)
    scraped_news = []
    count = 1
    for link in scraped_link:
        try:
            response = requests.get(link).text
            soup = BeautifulSoup(response,'lxml')
            news_content = soup.find('div',class_='detail-box')
            topic = 'politics'
            title = soup.find('h1',class_='news-big-title').text
            date = news_content.select_one('div.detail-box>div:nth-of-type(2)').span.text
            # processing in required format  of date
            date = date.split(':')[1].split()[0:-1]
            date = ' '.join(date)
            body = news_content.div.text
            scraped_news.append((topic,date,title,body))
            # print(date)
            # print(scraped_news[count-1])
            print('Count: ',count)
            count+=1
        except Exception as e:
            print('Exception occurred in scraping news (setopati) in count = ',count )
            continue
        
    with open('news-setopati.csv', 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        try:
            writer.writerow(('topic', 'date', 'title', 'body'))
            for news in scraped_news:
                writer.writerow(news)
            print('Success!!!')
        except Exception as e:
            print('Exception occurred while writing in setopati news file')
            sys.exit(1)
