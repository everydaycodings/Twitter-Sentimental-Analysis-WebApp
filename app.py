import streamlit as st

st.title("Twitter Sentimental Analysis")

word_query = st.text_input("Enter the Hastag or any word")
number_of_tweets = st.slider("How many tweets YOu want o collect from {}".format(word_query), min_value=100, max_value=10000)
st.info("1 Tweets takes approx 0.1 sec so you may have to wait {} minute for {} Tweets, So Please Have Patient.".format(round((number_of_tweets*0.1/60),2), number_of_tweets))

