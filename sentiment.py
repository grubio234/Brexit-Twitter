from __future__ import print_function
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DayLocator, DateFormatter
from matplotlib.ticker import MultipleLocator
import numpy as np
import pandas as pd
from TweetAnalyzer.config import data_dir
from TweetAnalyzer import SSIXAnalyzer, TweetStore, sentiments

def categorizeIfHasKeyword(tweets, sentiment_counts, keywords):
    def perSentiment(tweets, sentiment_counts, keywords):
        def perSentimentAlgo(tweets, sentiment_counts, keywords):
            has_a_keyword = pd.Series(False, index=tweets.index)
            for keyword in keywords:
                has_this_kw = tweets["text"].apply(lambda text: keyword in text)
                has_a_keyword = has_a_keyword | has_this_kw
            for day in sentiments_per_day.index:
                is_today = tweets["date"] == day
                found_today = has_a_keyword & is_today
                sentiment_counts[day] += sum(found_today)
            return tweets[~has_a_keyword]

        def nWithAndNoCat(uncategorized, sentiment_counts):
            n_wo_category = len(uncategorized)
            n_with_category = sentiment_counts.sum(axis=0)
            return n_with_category, n_wo_category

        n = {}
        n["oldWCat"], n["oldNoCat"] = nWithAndNoCat(tweets, sentiment_counts)
        remaining_tweets = perSentimentAlgo(tweets, sentiment_counts, keywords)
        w_cat, no_cat = nWithAndNoCat(remaining_tweets, sentiment_counts)

        n["newWCat"], n["newNoCat"] = w_cat, no_cat
        if n["oldWCat"] + n["oldNoCat"] != n["newWCat"] + n["newNoCat"]:
            raise Exception("Some events were lost while performing the "
                "categorization. {oldWCat}+{oldNoCat} != {newWCat}+{newNoCat}"
                "".format(**n))
        return remaining_tweets

    remaining_tweets = tweets.copy()
    for sentiment in sentiments:
        remaining_tweets = perSentiment(remaining_tweets,
                            sentiment_counts[sentiment], keywords[sentiment])
    return remaining_tweets

def printTweetStats(undistributed_tweets, sentiments_per_day):
    n_undistributed = len(undistributed_tweets)
    sentiments_all_time = sentiments_per_day.sum()
    n_distributed = sentiments_all_time.sum()
    print("Number of undistributed tweets: {}.".format(n_undistributed))
    print("Number of distributed tweets: {}.".format(n_distributed))
    print(sentiments_all_time)
    print(sentiments_per_day)

tweets = TweetStore(data_dir + "May_16.csv")
df = tweets.getTweets()
idx = sorted(df["date"].unique())
sentiments_per_day = pd.DataFrame(0, index=idx, columns=sentiments)

keywords = {}
keywords["leave"]     = ["ukip", "no2eu", "britainout", "voteleave", "leaveeu"]
keywords["undecided"] = ["euref", "eureferendum", "takecontrol"]
keywords["stay"]      = ["#strongerin", "remain", "ukineu"]

print("\n==== 1.) Categorize tweets by keyword. ====")
df = categorizeIfHasKeyword(df, sentiments_per_day, keywords)
printTweetStats(df, sentiments_per_day)


print("\n==== 2.) Categorize tweets by sentiment analysis score. ====")
score_function =  lambda n_leave, n_stay, n_undecided: n_stay - n_leave
thresholds = {}
thresholds["leave"] = -0.00661286
thresholds["stay"]  = 0.00830461

def categorizeByScore(tweets, sentiments_per_day, score_function, thresholds):
    def scoreToSentiment(score):
        if score <= thresholds["leave"]:
            return "leave"
        elif score >= thresholds["stay"]:
            return "stay"
        else:
            return "undecided"

    ssix = SSIXAnalyzer(score_function)
    tweets["score"] = tweets["text"].apply(ssix.getTweetScore)
    tweets["sentiment"] = tweets["score"].apply(scoreToSentiment)

    for day in sentiments_per_day.index:
        day_tweets = tweets[tweets["date"] == day]
        for s in sentiments:
            sentiments_per_day[s][day] += sum(day_tweets["sentiment"] == s)


categorizeByScore(df, sentiments_per_day, score_function, thresholds)
without_category = pd.DataFrame()
printTweetStats(without_category, sentiments_per_day)

def dailySentimentPlots(sentiments_per_day, save_path="./"):
    loc = MultipleLocator(base=1.0)
    xfmt = DateFormatter('%d %b')

    fig = plt.figure(figsize=(6,6))
    ax = plt.axes()
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(loc)
    ax.set_title("Tweet count for leave / stay")
    w = 0.2

    np_days = date2num(sentiments_per_day.index.tolist())
    ax.bar(np_days, sentiments_per_day["leave"], width=w, color="r", label="leave")
    ax.bar(np_days+w, sentiments_per_day["stay"], width=w, color="b", label="stay")
    ax.set_xlabel("Dates")
    ax.set_ylabel("Tweet count")
    plt.savefig(save_path+"total_daycount_ls.pdf")

    tot = sentiments_per_day["leave"] + sentiments_per_day["stay"] + sentiments_per_day["undecided"]
    tot.replace(0, 1, inplace=True)
    tot.astype(float)

    fig = plt.figure(figsize=(6,6))
    ax = plt.axes()
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(loc)
    ax.set_title("Tweet count for leave / other / stay")
    w = 0.6
    ax.bar(np_days, sentiments_per_day["leave"] / tot, width=w, color="r", label="leave")
    ax.bar(np_days, sentiments_per_day["stay"] / tot, width=w, bottom=sentiments_per_day["leave"] / tot, color="b", label="stay")
    ax.bar(np_days, sentiments_per_day["undecided"] / tot, width=w, bottom=1-sentiments_per_day["undecided"] / tot, color="g", label="other")
    ax.set_xlabel("Dates")
    ax.set_ylabel("Tweet count")
    plt.savefig(save_path+"relative_daycount.pdf")

dailySentimentPlots(sentiments_per_day)