import pandas as pd


nep_to_eng_numbers = {'०': '0', '१': '1', '२': '2', '३': '3',
                      '४': '4', '५': '5', '६': '6', '७': '7', '८': '8', '९': '9'}

def init_annapurna_vars():
    month_names = ['वैशाख',
                   'जेठ',
                   'असार',
                   'साउन',
                   'भदौ',
                   'असोज',
                   'कात्तिक',
                   'मंसिर',
                   'पुष',
                   'माघ',
                   'फागुन',
                   'चैत']
    month_number = [i for i in range(1, 13)]
    month_map = dict(zip(month_names, month_number))
    return month_map


def init_setopati_vars():
    month_names = ['वैशाख',
                   'जेठ',
                   'असार',
                   'साउन',
                   'भदौ',
                   'असोज',
                   'कात्तिक',
                   'मंसिर',
                   'पुस',
                   'माघ',
                   'फागुन',
                   'चैत']
    month_number = [i for i in range(1, 13)]
    month_map = dict(zip(month_names, month_number))
    return month_map

    
# filename is preprocessed annapurna csv file
def manage_annapurna_date(filename):
    """
    Filename is preprocessed annapurna csv file,
    Then, saves into that same file
    """
    df_annapurna = pd.read_csv(filename)
    month_map = init_annapurna_vars()
    all_news_date = df_annapurna.date
    
    new_years = []
    new_months = []
    new_days = []
    combined_forms = []
    verbal_date_forms = []
    
    for date in all_news_date:
        splitted_form = date.split(' ')
        verbal_date_form = splitted_form[3]+', ' + \
            splitted_form[0]+' '+splitted_form[1]+" " + splitted_form[2]

        year = splitted_form[2]
        s = []
        for i in year:
            s.append(nep_to_eng_numbers[i])
        year = ''.join(s)
        month = month_map[splitted_form[0]]
        day = splitted_form[1].split(',')[0]
        s = []
        for i in day:
            s.append(nep_to_eng_numbers[i])
        day = ''.join(s)

        new_years.append(int(year))
        new_months.append(int(month))
        new_days.append(int(day))

        combined_form = str(year)+'-'+str(month)+'-'+str(day)
        combined_forms.append(combined_form)

        verbal_date_forms.append(verbal_date_form)

    df_annapurna['Year'] = new_years
    df_annapurna['Month'] = new_months
    df_annapurna['Day'] = new_days
    df_annapurna['Combined_Date'] = combined_forms
    df_annapurna['date'] = verbal_date_forms
    
    df_annapurna.to_csv(filename, index=False)
    return df_annapurna
    

def manage_setopati_date(filename):
    """
    Filename is preprocessed setopati csv file,
    Then, saves into that same file
    """
    df_setopati = pd.read_csv(filename)
    month_map = init_setopati_vars()
    
    all_news_date = df_setopati.date
    new_years = []
    new_months = []
    new_days = []
    combined_forms = []

    for date in all_news_date:
        splitted_form = date.split(' ')
        year = splitted_form[3]
        s = []
        for i in year:
            s.append(nep_to_eng_numbers[i])
        year = ''.join(s)
        month = month_map[splitted_form[1]]
        day = splitted_form[2].split(',')[0]
        s = []
        for i in day:
            s.append(nep_to_eng_numbers[i])
        day = ''.join(s)

        new_years.append(int(year))
        new_months.append(int(month))
        new_days.append(int(day))

        combined_form = str(year)+'-'+str(month)+'-'+str(day)
        combined_forms.append(combined_form)

    df_setopati['Year'] = new_years
    df_setopati['Month'] = new_months
    df_setopati['Day'] = new_days
    df_setopati['Combined_Date'] = combined_forms
    
    df_setopati.to_csv(filename,index=False)
    return df_setopati
