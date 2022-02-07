from attr import has
import streamlit as st
from helper import preprocessing_data, graph_sentiment, analyse_mention, analyse_hastag, download_data

st.set_page_config(
     page_title="Data Analysis Web App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://github.com/everydaycodings/Data-Analysis-Web-App',
         'Report a bug': "https://github.com/everydaycodings/Data-Analysis-Web-App/issues/new",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
)


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
    mention = analyse_mention(data)
    hastag = analyse_hastag(data)

    st.write(" ")
    st.write(" ")
    st.header("Extracted and Preprocessed Dataset")
    st.write(data)
    download_data(data, label="twitter_sentiment_filtered")
    st.write(" ")
    
    col1, col2, col3 = st.columns(3)
    with col2:
        st.markdown("### EDA On the Data")


    col1, col2 = st.columns(2)

    with col1:
        st.text("Top 10 @Mentions in {} tweets".format(number_of_tweets))
        st.bar_chart(mention)
    with col2:
        st.text("Top 10 Hastags used in {} tweets".format(number_of_tweets))
        st.bar_chart(hastag)
    
    col3, col4 = st.columns(2)
    with col3:
        st.text("Top 10 Used Links for {} tweets".format(number_of_tweets))
        st.bar_chart(data["links"].value_counts().head(10).reset_index())
    
    with col4:
        st.text("All the Tweets that containes top 10 links used")
        filtered_data = data[data["links"].isin(data["links"].value_counts().head(10).reset_index()["index"].values)]
        st.write(filtered_data)

    st.subheader("Twitter Sentment Analysis")
    st.bar_chart(analyse)
    