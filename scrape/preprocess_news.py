import pandas as pd
import numpy as np


def preprocess_text(text, characters_to_remove):
    # Create a translation table with None for characters to remove
    # characters to be replaced by '' (empty)
    table = str.maketrans('', '', ''.join(characters_to_remove))
    # characters to be replaced by ' ' (space)
    table[ord('—')] = ' '
    table[ord('‘')] = ' '
    table[ord('’')] = ' '
    table[ord('।')] = ' '

    # Use translate to remove specified characters
    cleaned_text = text.translate(table)
    cleaned_text = ' '.join(cleaned_text.split())
    return cleaned_text



def preprocess(df):
    characters = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+',
        '=', '{', '}', '[', ']', '|', '\\', ':', ';', '"', "'", '<', '>',
        ',', '.', '/', '?', '`', '~', '-', '…', '०', '१', '२', '३', '४', '५', '६', '७', '८', '९']
    
    # remove rows with nan value
    df = df.dropna()
    # now do preprocessing
    df.loc[:, 'body'] = df['body'].apply(lambda x: preprocess_text(x, characters))
    return df


if __name__=="__main__":
    # df = pd.read_csv('news_setopati_latest_part.csv')
    # df = pd.read_csv('news_annapurna_latest_part.csv')
    # df = preprocess(df)
    
    # df.to_csv('news_setopati_preprocessed_latest_part.csv', index=False)
    pass