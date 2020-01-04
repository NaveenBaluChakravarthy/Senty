"""
Project Number: #01
Title : Sentiment Analysis
Author : Naveen Chakravarthy Balasubramanian
Description : Lot of negativity in the news these days. Taking InShorts as case study, prepare a summary of the news according to sentiments to understand overall emotion of the news of the day
"""

# Defining contractions list 
def contractions():
    contrac = pd.read_excel('Contraction.xlsx', sheet_name='Contractions')
    return contrac

# Importing the libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import unicodedata
import matplotlib.pyplot as plt
import seaborn as sns
from afinn import Afinn
from nltk.stem import WordNetLemmatizer

# Defining the source
source = ['https://inshorts.com/en/read/technology',
          'https://inshorts.com/en/read/sports',
          'https://inshorts.com/en/read/national',
          'https://inshorts.com/en/read/business',
          'https://inshorts.com/en/read/politics',
          'https://inshorts.com/en/read/startup',
          'https://inshorts.com/en/read/entertainment',
          'https://inshorts.com/en/read/miscellaneous',
          'https://inshorts.com/en/read/hatke',
          'https://inshorts.com/en/read/science',
          'https://inshorts.com/en/read/automobile',          
          'https://inshorts.com/en/read/world']

# Scraping the data from web - InShorts 
dataq = []
for site in source:
    category = site.split('/')[-1]
    data = requests.get(site)
    soup = BeautifulSoup(data.content, 'html.parser')
    arts = [{'Category': category,
             'Headline': souphdr.find('span', attrs={"itemprop":"headline"}).string,
             'Article': soupart.find('div', attrs={"itemprop":"articleBody"}).string
             } 
            for souphdr, soupart in 
            zip(soup.find_all('div', class_= ["news-card-title news-right-box"]), 
                soup.find_all('div', class_= ["news-card-content news-right-box"]))
            ]
    dataq.extend(arts)    
dataset = pd.DataFrame(dataq)
dataset = dataset[['Category', 'Headline', 'Article']]

# Cleaning the text
contraction = contractions()
lemmatizer = WordNetLemmatizer()
X = []
for n in range(0, len(dataset)):
    string = re.sub('[^a-zA-Z0-9]', ' ', dataset['Article'][n])
    string = unicodedata.normalize('NFKD', string).encode('ascii', 'ignore').decode('utf-8', 'ignore')
    string = string.lower()
    string = string.split()
    m = -1
    corpus = ""
    for i in range(0, len(string)):
        x = next(iter(contraction[contraction['Contractions'] == string[i]].index.values.astype(int)), m)
        if x != -1:
            y = contraction.iloc[x:x+1, 1:2].values
            for word in y:
                corpus += str(word) + " "
        else:
            corpus += string[i] + " "
    corpus = re.sub('[^a-zA-Z0-9]', ' ', corpus)
    corpus = corpus.split()
    corpus = [lemmatizer.lemmatize(word, pos = 'v') for word in corpus]
    corpus = ' '.join(corpus)
    X.append(corpus)
    
# Sentiment Analysis
afin = Afinn()
scores = []
for k in range(0, len(X)):
    scores.append(afin.score(X[k]))
sentiment = ['positive' if score > 0 
             else 'negative' if score < 0 
             else 'neutral' 
             for score in scores]

# Building a dataframe
X_cons = pd.DataFrame([list(dataset['Category']), scores, sentiment]).T
X_cons.columns = ['Category', 'Score', 'Sentiment']
X_cons.groupby(by=['Category']).describe()

# Visuailizing the results
colorpalette = {"positive" : "#0BFE0B", 
                "negative" : "#FE360B", 
                "neutral"  : "#3444EE"}
plot = sns.catplot(x = "Category", 
                   hue = 'Sentiment', 
                   data = X_cons, 
                   kind = 'count', 
                   palette = colorpalette,
                   aspect = 3
                   )
plt.title("""       Inshorts - News Sentiment Analysis
       *************************************
          The more the red, the more is the negativity in the news
              Do you really want to read the news this morning?""")
plot.savefig("SentimentAnalysis.jpg")

