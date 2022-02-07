import tweepy
import pandas as pd
import configparser
import re
from textblob import TextBlob
from wordcloud import WordCloud
import streamlit as st
import datetime, pytz

emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002500-\U00002BEF"  # chinese char
        u"\U00002702-\U000027B0"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001f926-\U0001f937"
        u"\U00010000-\U0010ffff"
        u"\u2640-\u2642" 
        u"\u2600-\u2B55"
        u"\u200d"
        u"\u23cf"
        u"\u23e9"
        u"\u231a"
        u"\ufe0f"  # dingbats
        u"\u3030"  # flags (iOS)
                           "]+", flags=re.UNICODE)




def twitter_connection():

    config = configparser.ConfigParser()
    config.read("config.ini")

    api_key = config["twitter"]["api_key"]
    api_key_secret = config["twitter"]["api_key_secret"]
    access_token = config["twitter"]["access_token"]

    auth = tweepy.OAuthHandler(api_key, api_key_secret)
    api = tweepy.API(auth)

    return api

api = twitter_connection()


def cleanTxt(text):
    text = re.sub('@[A-Za-z0–9]+', '', text) #Removing @mentions
    text = re.sub('#', '', text) # Removing '#' hash tag
    text = re.sub('RT[\s]+', '', text) # Removing RT
    text = re.sub('https?:\/\/\S+', '', text)
    text = re.sub("\n","",text) # Removing hyperlink
    text = re.sub(":","",text) # Removing hyperlink
    text = re.sub("_","",text) # Removing hyperlink
    text = emoji_pattern.sub(r'', text)
    return text

def extract_mentions(text):
    text = re.findall("(@[A-Za-z0–9\d\w]+)", text)
    return text

def extract_hastag(text):
    text = re.findall("(#[A-Za-z0–9\d\w]+)", text)
    return text

def getSubjectivity(text):
   return TextBlob(text).sentiment.subjectivity

# Create a function to get the polarity
def getPolarity(text):
   return  TextBlob(text).sentiment.polarity

def getAnalysis(score):
  if score < 0:
    return 'Negative'
  elif score == 0:
    return 'Neutral'
  else:
    return 'Positive'

@st.cache(allow_output_mutation=True)
def preprocessing_data(word_query, number_of_tweets, function_option):

  if function_option == "Search By #Tag and Words":
    posts = tweepy.Cursor(api.search_tweets, q=word_query, count = 200, lang ="en", tweet_mode="extended").items((number_of_tweets))
  
  if function_option == "Search By Username":
    posts = tweepy.Cursor(api.user_timeline, screen_name=word_query, count = 200, tweet_mode="extended").items((number_of_tweets))
  
  data  = pd.DataFrame([tweet.full_text for tweet in posts], columns=['Tweets'])

  data["mentions"] = data["Tweets"].apply(extract_mentions)
  data["hastags"] = data["Tweets"].apply(extract_hastag)
  data['links'] = data['Tweets'].str.extract('(https?:\/\/\S+)', expand=False).str.strip()
  data['retweets'] = data['Tweets'].str.extract('(RT[\s@[A-Za-z0–9\d\w]+)', expand=False).str.strip()

  data['Tweets'] = data['Tweets'].apply(cleanTxt)
  discard = ["CNFTGiveaway", "GIVEAWAYPrizes", "Giveaway", "Airdrop", "GIVEAWAY", "makemoneyonline", "affiliatemarketing"]
  data = data[~data["Tweets"].str.contains('|'.join(discard))]

  data['Subjectivity'] = data['Tweets'].apply(getSubjectivity)
  data['Polarity'] = data['Tweets'].apply(getPolarity)

  data['Analysis'] = data['Polarity'].apply(getAnalysis)

  return data


def download_data(data, label):
    current_time = datetime.datetime.now(pytz.timezone('Asia/Kolkata'))
    current_time = "{}.{}-{}-{}".format(current_time.date(), current_time.hour, current_time.minute, current_time.second)
    export_data = st.download_button(
                        label="Download {} data as CSV".format(label),
                        data=data.to_csv(),
                        file_name='{}{}.csv'.format(label, current_time),
                        mime='text/csv',
                        help = "When You Click On Download Button You can download your {} CSV File".format(label)
                    )
    return export_data


def analyse_mention(data):

  mention = pd.DataFrame(data["mentions"].to_list()).add_prefix("mention_")

  try:
    mention = pd.concat([mention["mention_0"], mention["mention_1"], mention["mention_2"]], ignore_index=True)
  except:
    mention = pd.concat([mention["mention_0"]], ignore_index=True)
  
  mention = mention.value_counts().head(10)
  
  return mention



def analyse_hastag(data):
  
  hastag = pd.DataFrame(data["hastags"].to_list()).add_prefix("hastag_")

  try:
    hastag = pd.concat([hastag["hastag_0"], hastag["hastag_1"], hastag["hastag_2"]], ignore_index=True)
  except:
    hastag = pd.concat([hastag["hastag_0"]], ignore_index=True)
  
  hastag = hastag.value_counts().head(10)

  return hastag




def graph_sentiment(data):

  analys = data["Analysis"].value_counts().reset_index().sort_values(by="index", ascending=False)
  
  return analys