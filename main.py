import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer

from user import my_credentials # Get credentials from user.py (.gitignored)
USERNAME, PASSWORD, SECRET_TOKEN, CLIENT_ID = my_credentials()
# These can be created at https://www.reddit.com/prefs/apps


# Authentication
def auth():
        client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_TOKEN)

        post_data = {"grant_type": "password", "username": USERNAME, "password": PASSWORD}

        # Headers
        user_agent = "MyStats/0.0.1"
        headers = {"User-Agent": user_agent}

        # Send POST request to the Reddit API to get an access token
        url = "https://www.reddit.com/api/v1/access_token"
        response = requests.post(url, auth=client_auth, data=post_data, headers=headers)

        # Parse the response as JSON and return it
        return headers, response.json()['access_token']


# Subreddit, time filter and limit for the API request
def get_sub(subreddit='Python', time_filter='month', limit=100):

    # Current timestamp and one month ago
    now = datetime.now()
    one_month_ago = now - timedelta(days=30)

    # Convert to Unix time
    now_unix = int(now.timestamp())
    one_month_ago_unix = int(one_month_ago.timestamp())

    # Make the API request
    url = f'https://oauth.reddit.com/r/{subreddit}/top?t={time_filter}&limit={limit}&after={one_month_ago_unix}&before={now_unix}'
    res = requests.get(url, headers=headers)

    df = pd.DataFrame(columns=['subreddit', 'title', 'selftext', 'upvote_ratio', 'ups', 'downs', 'score'])

    # Loop through each post retrieved from the API request and append to df
    for post in res.json()['data']['children']:
        df.loc[len(df)] = {
            'subreddit': post['data']['subreddit'],
            'title': post['data']['title'],
            'selftext': post['data']['selftext'],
            'upvote_ratio': post['data']['upvote_ratio'],
            'ups': post['data']['ups'],
            'downs': post['data']['downs'],
            'score': post['data']['score']
        }
    return df

def word_count(df):
    # regular english stop words filter + custom filter
    stop_words = 'english'
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    
    vectorizer.fit(df['title'])
    
    title_tfidf = vectorizer.transform(df['title'])     # Sparse matrix of TF-IDF features
    feature_names = vectorizer.get_feature_names_out()  # Get the names of the features/words
    sum_scores = title_tfidf.sum(axis=0)                # Sum the TF-IDF scores for each feature for all titles
    
    # Convert scores to 1D array, sort descending order
    top_scores = np.squeeze(np.asarray(sum_scores))
    sorted_scores_indices = np.argsort(top_scores)[::-1]
    
    print("Top 10 features by TF-IDF score:")
    for i in range(10):
        feature_index = sorted_scores_indices[i]
        feature_score = top_scores[feature_index]
        feature_name = feature_names[feature_index]
        print(f"{feature_name}: {feature_score:.3f}")


if __name__ == "__main__":
        headers, access_token = auth()
        headers = {**headers, **{'Authorization': f'bearer {access_token}'}}

        subreddit = get_sub()
        word_count(subreddit)
