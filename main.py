import time
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from sklearn.feature_extraction.text import TfidfVectorizer

from user import my_credentials # Get credentials from user.py (.gitignored)
USERNAME, PASSWORD, SECRET_TOKEN, CLIENT_ID = my_credentials()
# These can be created at https://www.reddit.com/prefs/apps


# Authentication
def auth():
    try:
        # Set up authentication
        client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, SECRET_TOKEN)

        # Set up post data
        post_data = {"grant_type": "password", "username": USERNAME, "password": PASSWORD}

        # Set up headers
        user_agent = "RedViz/0.0.1"
        headers = {"User-Agent": user_agent}

        # Send POST request to the Reddit API to get an access token
        url = "https://www.reddit.com/api/v1/access_token"
        response = requests.post(url, auth=client_auth, data=post_data, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the response as JSON and return it
            print(f"Successful HTTP request {response.status_code}: {response.reason}")
            return headers, response.json()['access_token']
        else:
            # Print error message and reason
            print(f"Request failed with status code {response.status_code}: {response.reason}")
            return None
    except requests.exceptions.RequestException as e:
        # Print error message and reason
        print(f"Request failed: {e}")
        return None



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

def get_tfidf(df, length=10, verbose=False):
    # regular english stop words filter TODO: Custom filter
    stop_words = 'english'
    vectorizer = TfidfVectorizer(stop_words=stop_words)
    
    vectorizer.fit(df['title'])
    
    title_tfidf = vectorizer.transform(df['title'])     # Sparse matrix of TF-IDF features
    feature_names = vectorizer.get_feature_names_out()  # Get the names of the features/words
    sum_scores = title_tfidf.sum(axis=0)                # Sum the TF-IDF scores for each feature for all titles
    
    # Convert scores to 1D array, sort descending order
    top_scores = np.squeeze(np.asarray(sum_scores))
    sorted_scores_indices = np.argsort(top_scores)[::-1]
    
    if verbose:
        print(f"Top {length} features by TF-IDF score:")
        for i in range(length):
            feature_index = sorted_scores_indices[i]
            feature_score = top_scores[feature_index]
            feature_name = feature_names[feature_index]
            print(f"{feature_name}: {feature_score:.3f}")

    top_features_list = []
    for i in range(length):
        feature_index = sorted_scores_indices[i]
        feature_score = top_scores[feature_index]
        feature_name = feature_names[feature_index]
        top_features_list.append((feature_name, feature_score))
    return top_features_list


# Converting date format YYYY MM to Unix timestamps
def month_to_unix(year, month):
    if isinstance(month, str):
        month_dict = {"january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
                      "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12}
        month = month_dict[month.lower()]
    start_timestamp = int(time.mktime(time.strptime(f"{year}-{month}-01", "%Y-%m-%d")))
    end_timestamp = int(time.mktime(time.strptime(f"{year}-{month}-01", "%Y-%m-%d"))) + 2678400
    return (start_timestamp, end_timestamp)

# Converting unix timestamps back to YYYY MM
def unix_to_month(start_timestamp, end_timestamp):
    start_date = datetime.fromtimestamp(start_timestamp)
    end_date = datetime.fromtimestamp(end_timestamp)
    #return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
    return (start_date.year, start_date.month), (end_date.year, end_date.month)

# Plots
def plot_bar(data, title='Title'):
    x, y = zip(*data)
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.bar(x, y, color=plt.cm.tab20(np.linspace(0, 1, len(x))))
    ax.set_xlabel('Feature')
    ax.set_ylabel('Score')
    ax.set_title(title)
    plt.xticks(rotation=45, ha='right')
    plt.show()


def plot_pie(data, title='Title'):
    labels, values = zip(*data)
    fig, ax = plt.subplots(figsize=(16, 9))
    ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
    ax.set_title(title)
    plt.show()


if __name__ == "__main__":
        headers, access_token = auth()
        headers = {**headers, **{'Authorization': f'bearer {access_token}'}}
        print(headers)
