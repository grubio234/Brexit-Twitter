from __future__ import print_function
import pandas as pd
from TweetAnalyzer.config import data_dir
from TweetAnalyzer import SSIXAnalyzer, TweetStore, sentiments
from util_plotting import dailySentimentPlots

def categorizeIfHasKeyword(tweets, sentiment_counts, keywords):
    def perSentiment(tweets, sentiment_counts, keywords):
        def perSentimentAlgo(tweets, sentiment_counts, keywords):
            has_a_keyword = pd.Series(False, index=tweets.index)
            for keyword in keywords:
                has_this_kw = tweets["text"].apply(lambda text: keyword in text)
                has_a_keyword = has_a_keyword | has_this_kw
            for day in sentiment_counts.index:
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


def sentimentAnalysis(tweet_files=None, save_folder="./"):
    def setupDataFrames(tweet_files):
        if tweet_files is None:
            tweet_files = [data_dir + "May_16.csv"]

        tweets = TweetStore(tweet_files).getTweets()
        days = sorted(tweets["date"].unique())
        sentiments_per_day = pd.DataFrame(0, index=days, columns=sentiments)
        return tweets, sentiments_per_day

    tweets, sentiments_per_day = setupDataFrames(tweet_files)

    print("\n==== 1.) Categorize tweets by keyword. ====")
    keywords = {}
    keywords["leave"] = ["ukip", "no2eu", "britainout", "voteleave", "leaveeu"]
    keywords["stay"] = ["#strongerin", "remain", "ukineu"]
    keywords["undecided"] = ["euref", "eureferendum", "takecontrol"]
    tweets_wo_keyword = categorizeIfHasKeyword(tweets, sentiments_per_day, keywords)
    printTweetStats(tweets_wo_keyword, sentiments_per_day)

    print("\n==== 2.) Categorize tweets by sentiment analysis score. ====")
    score_function =  lambda n_leave, n_stay, n_undecided: n_stay - n_leave
    thresholds = {}
    thresholds["leave"] = -0.00661286
    thresholds["stay"]  = 0.00830461
    categorizeByScore(tweets_wo_keyword, sentiments_per_day, score_function, thresholds)
    without_category = pd.DataFrame()
    printTweetStats(without_category, sentiments_per_day)

    dailySentimentPlots(sentiments_per_day, save_folder)
    print("\n==== 3.) Plots saved at '{}'. ====".format(save_folder))

if __name__ == "__main__":
    sentimentAnalysis()