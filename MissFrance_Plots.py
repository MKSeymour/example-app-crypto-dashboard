# Libraries


import pandas as pd
import plotly
import json
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import json
# % matplotlib inline
from wordcloud import WordCloud, STOPWORDS

# Get the data.

def read_file(filepath):
    with open(path, "r") as jsonFile:
        df = json.load(jsonFile)
    print('File was loaded with {} records'.format(len(df)))
    return df


def to_dataframe(json_file):
    import pandas as pd
    return pd.DataFrame.from_dict(json_file, orient='index')


def data_processing(df):
    # convert to datetime
    df.created = df.created.apply(lambda x : pd.to_datetime(str(x)).strftime('%b-%d-%Y'))
    df.added = pd.to_datetime(df.added)

    # convert to string
    df.text = df.text.astype(str)
    df.geo = df.geo.astype(str)
    df.lang = df.lang.astype(str)
    df.user_name = df.user_name.astype(str)
    df.miss = df.miss.astype(str)

    # check empty
    df.user_location = df.user_location.apply(lambda x: None if str(x) == '' else str(x))
    df.lang = df.lang.apply(lambda x: None if str(x) == '' else str(x))
    df.geo = df.geo.apply(lambda x: None if str(x) == 'None' else str(x))

    return df


path = 'tweets.json'
tweets_miss = data_processing(to_dataframe(read_file(path)))

#tweets_miss.head(5)
print(tweets_miss.info())


# --- VIEW IN STREAMLIT----------------------------------------------------------------------------------------

import streamlit as st
import numpy as np

st.set_page_config(layout="wide",
    page_title="#TaMissBuzz",
    page_icon= ':crown:')
st.set_option('deprecation.showPyplotGlobalUse', False)

#st.image("https://s3.us-west-2.amazonaws.com/secure.notion-static.com/4be3ed19-3304-4f8e-b4a4-6e65c9ed30db/tlchargement.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20221112%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20221112T140832Z&X-Amz-Expires=86400&X-Amz-Signature=51eabc483ff8e6700cf268901274385a7aa736603933e5212a10d038e113cbdf&X-Amz-SignedHeaders=host&response-content-disposition=filename%3D%22t%25C3%25A9l%25C3%25A9chargement.png%22&x-id=GetObject")
st.title("#TaMissBuzz")
st.subheader("Quelle miss Outre-Mer a le plus de succès sur Twitter ??!")

col1, col2 = st.columns([1, 1])
#with col1:
    #st.image(str(file_path+"loan.png"))
    #st.image("https://s3.us-west-2.amazonaws.com/secure.notion-static.com/4be3ed19-3304-4f8e-b4a4-6e65c9ed30db/tlchargement.png?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20221109%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20221109T205742Z&X-Amz-Expires=86400&X-Amz-Signature=98e2a1253f307cf6b28a48b41db2a256f59032a43649833ec640b13118bc7e76&X-Amz-SignedHeaders=host&response-content-disposition=filename%3D%22t%25C3%25A9l%25C3%25A9chargement.png%22&x-id=GetObject")

with col1:
    st.write("Selon toi qui arrivera en tête ?")



# ----PLOT-------------------------------------------------------------------------------------------------

#  DATA PREP

#st.bar_chart(tweets_miss, x = 'miss', y ='retweets')
#st.bar_chart(tweets_miss, x = 'created', y ='miss')


om_miss = list(set(tweets_miss.miss))
om_miss.remove('neutre')

activity_over_date = tweets_miss.groupby( by = ['created', 'miss']).agg(
    {'miss' : 'count', 'retweets' : 'sum'}).rename(columns = {'miss' :'tweets'}).reset_index(1)

activity_over_date = activity_over_date[activity_over_date.miss.isin(om_miss)].sort_values(by="created")
activity_over_date['total_activity'] = activity_over_date.tweets + activity_over_date.retweets


# ----------------------------------------------------------

# 3 - SELECT DATE - CUMULATIVE ACTIVITY

cumulative_activity = {}

i = 0
# current = tweets_count_over_date[tweets_count_over_date.miss== "Miss Guadeloupe"]
for miss in list(activity_over_date.miss.unique()):
    for date in list(activity_over_date.index):
        current = activity_over_date[(activity_over_date.miss == miss) & (activity_over_date.index <= date)]
        to_add = [date, miss, current["total_activity"].sum()]
        cumulative_activity[i] = list(to_add)
        i += 1

cumulative_activity = pd.DataFrame.from_dict(cumulative_activity, orient='index')
cumulative_activity.columns = ['date', 'miss', 'total_activity']
cumulative_activity = cumulative_activity.sort_values(by='date')
#cumulative_activity['date'] = cumulative_activity.date.apply(lambda x: x.strftime('%d/%m/%Y'))



# --------------------P L O T --------------------------------------------------------------


## Quelle miss Outre-Mer a le plus de succès sur Twitter ✅
fig = px.bar(cumulative_activity,x='miss', y='total_activity',
              animation_group='miss', animation_frame= "date", range_y=[0,2000] )
fig.update_xaxes(categoryorder = 'array', categoryarray = om_miss,)
st.plotly_chart(fig,use_container_width=True)



## VISION PAR MISS
current_miss = st.selectbox("Quelle miss t'intéresse ?", om_miss, 0)

current_activity = activity_over_date[activity_over_date.miss == current_miss]
current_tweets = tweets_miss[tweets_miss.miss == current_miss]

col1, col2 = st.columns([1, 1])
with col1 :
    image = "https://github.com/MKSeymour/MissFrance2023/blob/main/miss_guadeloupe_2023.jpg?raw=true"
    st.image(image, caption= 'test', width=300)


### Nombre de tweets ✅
total_tweets = len(current_tweets)
total_activity = cumulative_activity[cumulative_activity.miss == current_miss]['total_activity'].iloc[-1]
col2.metric(label = "Buzz Twitter", value = total_activity)
col2.metric(label = "Tweets", value = total_tweets)

### Activité Twitter par jour ✅
fig=px.line(current_activity ,x=current_activity.index, y='total_activity', color = 'miss' )
st.plotly_chart(fig,use_container_width=True)

### Nuage de mots

# stopword français
f = open('stop_words_french.json')
fr_stopwords = list(json.load(f))

# Start with one review:
text = " ".join(tweet for tweet in current_tweets['text'])

# Create stopword list:
stopwords = set(STOPWORDS)
stopwords.update(fr_stopwords)


# Display the generated image:
# lower max_font_size, change the maximum number of word and lighten the background:
wordcloud = WordCloud(stopwords=stopwords, max_words=50,
                      background_color="white", colormap="inferno",
                     min_font_size=5, max_font_size=200).generate(text)
fig, ax = plt.subplots()
ax.imshow(wordcloud, interpolation="bilinear")
ax.axis("off")
st.pyplot(fig)







# 4 - TEST AREA
st.write("TEST PLOT")

import time
progress_bar = st.progress(0)
status_text = st.empty()



for i in range(100):
    # Update progress bar.
    progress_bar.progress(i + 1)

    new_rows = np.random.randn(10, 2)

    # Update status text.
    status_text.text(
        'The latest random number is: %s' % new_rows[-1, 1])

    # Append data to the chart.
    # Pretend we're doing some computation that takes time.
    time.sleep(0.1)

status_text.text('Done!')
st.balloons()
