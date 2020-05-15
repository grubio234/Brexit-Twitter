from __future__ import print_function
from TweetAnalyzer.config import data_dir
from TweetAnalyzer import SSIXAnalyzer, TweetStore
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from matplotlib.dates import date2num, DayLocator, DateFormatter

def dailyCountsForKeywordGroup(tweets, keyword_group, timezones=None):
    def hasKeyword(text):
        for keyword in keyword_group:
            if keyword in text:
                return True
        return False
    def isInTimezone(t):
        for timezone in timezones:
            if timezone in t:
                return True
        return False

    mask = pd.Series(True, index=tweets.index)
    if not timezones is None:
        mask = tweets["user_time_zone"].apply(isInTimezone) & mask
    if not keyword_group is None:
        mask = tweets["text"].apply(hasKeyword) & mask

    per_day = tweets["date"][mask].value_counts()
    return per_day

def dailyCountsPerGroup(tweets, keyword_groups, timezones=None):
    keyword_counts = pd.DataFrame()
    for name, kw_group in keyword_groups.items():
        daily_counts = dailyCountsForKeywordGroup(tweets, kw_group, timezones)
        keyword_counts[name] = daily_counts
    return keyword_counts




def emptyDataFramePlot(title, save_as):
    fig = plt.figure(figsize=(6,6))
    ax = fig.add_subplot(1, 1, 1)
    plt.xticks([])
    plt.yticks([])
    ax.set_title(title)
    fig.text(0.5, 0.5, "Empty DataFrame", ha='center', va='center', size=24, alpha=.5)
    fig.savefig(save_as)

def keywordFrequencyPlot(df, title, save_as, colors, mode=None):
    if df.empty:
        emptyDataFramePlot(title, save_as)
    else:
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(1, 1, 1)
        ax.legend(loc="best")
        ax.set_title(title)
        daily_width = 0.8
        xfmt = DateFormatter('%d %b')
        ax.xaxis.set_major_formatter(xfmt)
        ax.set_xlabel("Date")
        ax.set_ylabel("Tweet count")
        N = len(df.columns)

        ybottom = pd.Series(0, index=df.index)
        days = date2num(df.index)
        for i, col in enumerate(df.columns):
            if mode == "stacked":
                ax.bar(days, df[col], bottom=ybottom, width=daily_width, color=colors[i], label=col)
                ybottom += df[col]
                print("Plotted ", col)

            else:
                bar_width = daily_width/N
                xk = days + bar_width*(i - N/2 - 1)
                ax.bar(xk, df[col], width=bar_width, color=colors[i], label=col)
        fig.savefig(save_as)


def run_stacked(tweets, keywords, timezones, colors):
    keywords = ["strongerin", "ukineu", "ukip", "leave", "remain", "euref"]
    colors = ["b", "g", "r", "m", "c", "y", "k"]
    timezones = {
        "London": ["London"],
        "US": ["US"],
        "Edinburgh": ["Edinburgh"],
        "Dublin": ["Dublin"],
        "Europe": timeZonesEurope(),
    }

def timeZonesEurope():
    return ["Amsterdam", "Andorra", "Athens", "Belfast", "Belgrade", "Berlin", "Bern",
      "Brussels", "Bucharest", "Budapest", "Copenhagen", "Dublin", "Edinburgh",
      "Helsinki", "Istanbul", "Kaliningrad", "Kiev", "Lisbon", "London", "Luxembourg",
      "Madrid", "Malta", "Minsk", "Moscow", "Oslo", "Paris", "Prague", "Riga",
      "Rome", "Sarajevo", "Skopje", "Sofia", "Sofia", "Stockholm", "Tallinn",
      "Vienna", "Warsaw", "Zurich"]

def run_stacked(tweets):
    keyword_list = ["strongerin", "ukineu", "ukip", "leave", "remain", "euref"]
    keywords = {kw: kw for kw in keyword_list}
    colors = ["b", "g", "r", "m", "c", "y", "k"]
    timezones = {
        "London": ["London"],
        "US": ["US"],
        "Edinburgh": ["Edinburgh"],
        "Dublin": ["Dublin"],
        "Europe": timeZonesEurope(),
    }


    for name, timezones in timezones.items():
        title = "Timezone: {}".format(name)
        save_as = "frequency_stacked_{}.pdf".format(name)
        df = dailyCountsPerGroup(tweets, keywords, timezones)

        keywordFrequencyPlot(df, title, save_as, colors, mode="stacked")

def run_brexit(tweets):
    keywords = {
        "All tweets": None,
        "Matching 'brexit'": "brexit",
    }
    colors = ["b", "r"]

    save_as = "frequency_brexit.pdf"
    title = "Brexit-related tweet count"

    df = dailyCountsPerGroup(tweets, keywords)

    keywordFrequencyPlot(df, title, save_as, colors)

if __name__ == "__main__":
    tweet_files = data_dir + "april_13_15.csv"
    tweet_files = data_dir + "May_16.csv"
    tweets = TweetStore(tweet_files).getTweets()
    run_brexit(tweets)
    run_stacked(tweets)
