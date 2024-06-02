from bs4 import BeautifulSoup
import requests
import csv
import sys
import chardet



# print(choosen)
# print(int(sys.argv[2]))

def annapurna(initial_page, final_page):
    # initial_page = 1001
    # final_page= 1815
    scraped_link = []
    count = initial_page
    for i in range(initial_page, final_page+1):
        try:
            response = requests.get(
                f'https://annapurnapost.com/category/politics/?page={i+1}').text
            soup = BeautifulSoup(response, 'lxml')
            highlight = soup.find('div', class_='category__banner').a['href']
            scraped_link.append(highlight)
            news_grid = soup.find('div', class_='category__news-grid')
            news_collection = news_grid.find_all('div', class_='grid__card')
            print(f'Annapurna page:{count} done.')
            count += 1
            for news in news_collection:
                a_tag = news.find('div', class_='card__details').h3.a
                # a_tag_text = a_tag.text
                a_tag_link = a_tag['href']
                scraped_link.append(a_tag_link)
        except Exception as e:
            print(f'Exception occurred on Annapurna at page: {count}')
            continue

    print(len(scraped_link))
    count = 1

    with open('../data/news_annapurna_latest_part.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(('topic', 'date', 'title', 'body', 'link', 'source'))
        # for news in scraped_news:
        #     writer.writerow(news)
        for link in scraped_link:
            try:
                temp_link = f'https://annapurnapost.com{link}'
                response = requests.get(temp_link).text
                soup = BeautifulSoup(response, 'lxml')
                news_content = soup.find('div', class_='ap__news-content')
                # topic = news_content.a.text.strip()
                topic = 'politics'
                title = news_content.h1.text.strip()
                date = news_content.find('p', class_='date').text.strip()
                body = news_content.find(
                    'div', class_='news__details').text.strip()
                source = 'AnnapurnaPost'
                # print(type(topic),type(date),type(title),type(body),type(link),type(source))
                # scraped_news.append((topic,date,title,body,temp_link,source))
                writer.writerow((topic, date, title, body, temp_link, source))

                print('Written in file : ', count)
                count += 1
            except Exception as e:
                print(
                    'Exception occurred in scraping news (Annapurna Post) in count = ', count)
                continue
        # print('Success !!!')

def setopati(initial_page,final_page):
    # IMP/TODO: the \xao character is a lot inside the text of this setopati, that
    # means the space character as said but if it impacts,need to take care of that
    # thing.
    # initial_page = 6
    # final_page = 38
    scraped_link = []
    count = initial_page
    for i in range(initial_page, final_page+1):
        try:
            response = requests.get(
                f'https://www.setopati.com/politics?page={i}').text
            soup = BeautifulSoup(response, 'lxml')
            if count == initial_page:
                # since the big item news is repeated
                # in setopati across pages.
                big_item_link = soup.find(
                    'div', class_='big-feature').a['href']
                scraped_link.append(big_item_link)
            bishesh = soup.find_all('div', class_='bishesh')
            for i in bishesh:
                items = i.find_all('div', class_='items')
                for j in items:
                    link = j.a['href']
                    scraped_link.append(link)
            print(f'Setopati page:{count} done.')
            count += 1
        except Exception as e:
            print(f'Exception occurred on Setopati at page: {count}')
            continue
    # print(scraped_link)
    # sys.exit(0)

    count = 1
    with open('../data/news_setopati_latest_part.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(('topic', 'date', 'title',
                         'body', 'link', 'source'))
        for link in scraped_link:
            try:
                response = requests.get(link).text
                soup = BeautifulSoup(response, 'lxml')
                news_content = soup.find('div', class_='detail-box')
                topic = 'politics'
                title = soup.find('h1', class_='news-big-title').text
                date = news_content.select_one(
                    'div.detail-box>div:nth-of-type(2)').span.text
                # processing in required format  of date
                date = date.split(':')[1].split()[0:-1]
                date = ' '.join(date)
                body = news_content.div.text
                source = 'Setopati'
                writer.writerow((topic, date, title, body, link, source))
                # print(date)
                # print(scraped_news[count-1])
                print('Written in file : ', count)
                count += 1
            except Exception as e:
                print('Exception occurred in scraping news (setopati) in count = ', count)
                continue

# Gorkhapatra = Deprecated ( since only news upto Baisakh 1, 2079 in their site ,but we want upto 2075 - mangsir , otherwise only certain section have 
# news from multiple sources i.e. after Baisakh 1, 2079 which may cause bias in model. )
def gorkhapatra():
    # total_pages = 150
    # scraped_link= []
    # count = 1
    initial_page = 1
    final_page = 1026
    scraped_link = []
    count = initial_page
    for i in range(initial_page, final_page+1):
        try:
            response = requests.get(
                f'https://gorkhapatraonline.com/categories/politics?page={i}').text
            soup = BeautifulSoup(response, 'lxml')
            news_in_a_page = soup.find_all('h2', class_='item-title')
            for news in news_in_a_page:
                link = news.a['href']
                scraped_link.append(link)
            print(f'Gorkhapatra page:{count} done.')
            count += 1
        except Exception as e:
            print(f'Exception occurred on Gorkhapatra at page: {count}')
            continue

    # print(len(scraped_link))
    # print(scraped_link)
    scraped_news = []
    count = 1
    for link in scraped_link:
        try:
            response = requests.get(link).text
            soup = BeautifulSoup(response, 'lxml')
            headline = soup.find('h1', class_='single-top-title').text
            content = soup.select_one(".single-blog-content")
            date = content.find('div').select_one(
                'div > div:nth-of-type(2)').text
            body = content.select_one("div.blog-details:nth-of-type(4)").text
            topic = 'politics'
            source = 'Gorkhapatra'
            information = (topic, date, headline, body, link, source)
            scraped_news.append(information)
            # print(scraped_news)
            print('Count: ', count)
            count += 1
        except Exception as e:
            print('Exception occurred in scraping news (Gorkhapatra) in count = ', count)
            continue

    with open('news_gorkhapatra_1.csv', 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        try:
            writer.writerow(('topic', 'date', 'title',
                            'body', 'link', 'source'))
            for news in scraped_news:
                writer.writerow(news)
            print('Success!!!')
        except Exception as e:
            print('Exception occurred while writing in gorkhapatra')
            sys.exit(1)



if __name__=="__main__":
    if len(sys.argv) != 4:
        print('Usage: python news_srape.py <annapurna|setopati> <initial_page> <final_page>')
        sys.exit(1)
    
    choosen = sys.argv[1]
    initial_page = int(sys.argv[2])
    final_page = int(sys.argv[3])
    if choosen == "annapurna":
        annapurna(initial_page,final_page)
    elif choosen == "setopati":
        setopati(initial_page,final_page)




    