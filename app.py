from attr import has
import streamlit as st
from helper import preprocessing_data, graph_sentiment, analyse_mention, analyse_hastag, download_data


def app():

    st.set_page_config(
        page_title="Social Dashboard",
        page_icon="icon.png",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.header("Social Media Analytics Dashboard")

    function_option = st.sidebar.selectbox("Select the platform: ",["Twitter", "Facebook", "Instagram"] )

    if function_option == "Twitter":
        # st.image('banner.png')
        st.sidebar.checkbox("Include retweets")
        
        st.write(" ")
        st.write(" ")
        st.write(" ")
        word_query = st.text_input("Enter a hashtag or any word", placeholder="#query")
        
        st.write(" ")
        number_of_tweets = st.slider("How many tweets would you like to analyse {}".format(word_query), min_value=100, max_value=10000)
        st.info("1 Tweets takes approx 0.05 sec so you may have to wait 5 seconds for 100 Tweets.")

        if st.button("Analyse Sentiment"):

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

    else: st.header("Coming Soon")

if __name__ == '__main__':
    app()   
