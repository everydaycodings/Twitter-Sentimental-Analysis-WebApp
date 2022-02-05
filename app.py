import streamlit as st
from helper import preprocessing_data, graph_sentiment

st.title("Twitter Sentimental Analysis")

function_option = st.sidebar.selectbox("Select The Funtionality: ", ["Search By #Tag and Words", "Search By Username"])

if function_option == "Search By #Tag and Words":
    word_query = st.text_input("Enter the Hastag or any word")

if function_option == "Search By Username":
    word_query = st.text_input("Enter the Username ( Don't include @ )")

number_of_tweets = st.slider("How many tweets You want to collect from {}".format(word_query), min_value=100, max_value=10000)
st.info("1 Tweets takes approx 0.05 sec so you may have to wait {} minute for {} Tweets, So Please Have Patient.".format(round((number_of_tweets*0.05/60),2), number_of_tweets))

if st.button("Analysis Sentiment"):

    data = preprocessing_data(word_query, number_of_tweets, function_option)
    analyse = graph_sentiment(data)
    st.write(data)
    st.bar_chart(analyse)
    