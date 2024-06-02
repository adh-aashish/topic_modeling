from . import news_scrape as ns
from . import preprocess_news
import pandas as pd
from . import manage_date_format
import nepali_datetime

# get new latest news by scraping
# suppose i know page start, end  by using nepali_datetime then finally at last 
# drop those rows which are duplicate


def test():
    return 'Working fine'

def pipeline_aggregate_data():
    try:
        df_all_news = pd.read_csv('../data/all_news_from_jestha_20_2075_to_now.csv')
        # sometimes 0 maybe headline news of other date, but we sorted so latest date kai huna 
        # parxa top ma hopefully
        prev_datestring = df_all_news.iloc[1].Combined_Date
        prev_datetime = nepali_datetime.datetime.strptime(prev_datestring, '%Y-%m-%d')
        delta_days = (nepali_datetime.date.today() - prev_datetime).days

        start_page = 1
        end_page = delta_days # this is to be found



        ns.annapurna(start_page,end_page-1)
        ns.setopati(start_page,end_page-2)
        # preprocess the news
        df_setopati = pd.read_csv('../data/news_setopati_latest_part.csv')
        df_setopati = preprocess_news.preprocess(df_setopati)
        df_setopati.to_csv('../data/news_setopati_preprocessed_latest_part.csv', index=False)

        df_annapurna = pd.read_csv('../data/news_annapurna_latest_part.csv')
        df_annapurna = preprocess_news.preprocess(df_annapurna)
        df_annapurna.to_csv('../data/news_annapurna_preprocessed_latest_part.csv', index=False)

        # add date columns in them
        df_annapurna = manage_date_format.manage_annapurna_date('../data/news_annapurna_preprocessed_latest_part.csv')
        df_setopati = manage_date_format.manage_setopati_date('../data/news_setopati_preprocessed_latest_part.csv')

        # join setopati and annapurna post news

        df_total = pd.concat([df_annapurna, df_setopati],ignore_index=True)

        # sort the news
        df_total = df_total.sort_values(
            by=['Year', 'Month', 'Day'], ascending=False, ignore_index=True)

        df_total = df_total[df_total['Combined_Date'] != prev_datestring ]


        df_total.to_csv(
            '../data/all_news_latest_part.csv', index=False)


        # join this latest sorted part into previously collected news
        df_all_news = pd.concat([df_all_news, df_total], ignore_index=True)
        df_all_news.to_csv('../data/all_news_from_jestha_20_2075_to_now.csv',index=False)
    except Exception as e:
        print(f'Error occurred in pipeline aggregate data: {e}')
        return False
    return True
