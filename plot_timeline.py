from __future__ import print_function
from TweetAnalyzer.config import data_dir
from TweetAnalyzer import SSIXAnalyzer, TweetStore
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from matplotlib.dates import date2num, DayLocator, DateFormatter
from matplotlib.ticker import MultipleLocator

def get_timeline_count(tweets_file, keywords=None, timezones=None):
    # get dataframe
    l = TweetStore(tweets_file)
    data = l.getTweets()

    def valid_keyword(x):
        for keyword in keywords:
            if keyword in x:
                return True
        return False

    def valid_timezone(t):
        for timezone in timezones:
            if timezone in t:
                return True
        return False

    if not timezones is None:
        data = data[data["user_time_zone"].apply(valid_timezone) == True]
    if not keywords is None:
        data = data[data["text"].apply(valid_keyword) == True]

    per_day = data["date"].value_counts()
    return per_day

def plot_timelines(ax, df, colors, mode=None):
    if df.empty:
        raise Exception("Empty dfs can not be handled with this function.")

    bar_width = 0.8
    xfmt = DateFormatter('%d %b')
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(MultipleLocator(base=1.0))
    N = len(df.columns)

    ybottom = pd.Series(0, index=df.index)
    days = date2num(df.index)
    for i, col in enumerate(df.columns):
        if mode == "stacked":
            ax.bar(days, df[col], bottom=ybottom, width=bar_width, color=colors[i], label=col)
            ybottom += df[col]
            print("Plotted ", col)

        else:
            xk = days + bar_width/N*(i - N/2 - 1)
            ax.bar(xk, df[col], width=bar_width, color=colors[i], label=col)
        #ax.xaxis_date()
        #ax.autoscale(tight=True)

def foreach_keyword(tweets_csv, keywords, timezones=None):
    """
        Filter for each keyword in keywords and matching timezones
    """
    x, y, labels = [], [], []
    df = pd.DataFrame()
    for keyword in keywords:
        df[keyword] = get_timeline_count(tweets_csv, [keyword], timezones)
        #if keyword == "":
        #    xn, yn = get_timeline_count(tweets_csv, timezones)
        #    labels.append("All tweets")
        #else:
        #    xn, yn = get_timeline_count(tweets_csv, [keyword], timezones)
        #    labels.append("Matching '{}'".format(keyword))
        #x.append(xn)
        #y.append(yn)
    #return x, y, labels
    return df


def run_experiment(tweets_csv, keywords, timezoneslist, titles, colors):

    for timezones, title in zip(timezoneslist, titles):
        fig = plt.figure(figsize=(6,6))
        df = foreach_keyword(tweets_csv, keywords, timezones)
        if df.empty:
            print("FIXME: Empty DataFrame handling: {}.".format(title)) # TODO
            plt.xticks([])
            plt.yticks([])
            fig.text(0.5, 0.5, "{} {} empty DataFrame".format(timezones[0], title), ha='center', va='center',
                size=24, alpha=.5)
        else:
            loc = MultipleLocator(base=5.0)
            loc.MAXTICKS = 10000
            xfmt = DateFormatter('%d %b')
            ax = fig.add_subplot(1, 1, 1)
            ax.xaxis.set_major_formatter(xfmt)
            ax.xaxis.set_major_locator(loc)
            box = ax.get_position()
            #ax.set_position([box.x0, box.y0, box.width*0.85, box.height])
            if len(timezones) == 1 and timezones[0] == "":
                ax.set_title("All timezones")
            else:
                ax.set_title("Timezone: {}".format(title))
            plot_timelines(ax, df, colors, mode="stacked")
            ax.set_xlabel("Date")
            ax.set_ylabel("Tweet count")
            ax.xaxis_date()
            ax.autoscale()
        #plt.legend(loc="best", bbox_to_anchor=(1, 0.6))
        fig.savefig("frequency_stacked_{}.pdf".format(title))

def timeZonesEurope():
    return ["Amsterdam", "Andorra", "Athens", "Belfast", "Belgrade", "Berlin", "Bern",
      "Brussels", "Bucharest", "Budapest", "Copenhagen", "Dublin", "Edinburgh",
      "Helsinki", "Istanbul", "Kaliningrad", "Kiev", "Lisbon", "London", "Luxembourg",
      "Madrid", "Malta", "Minsk", "Moscow", "Oslo", "Paris", "Prague", "Riga",
      "Rome", "Sarajevo", "Skopje", "Sofia", "Sofia", "Stockholm", "Tallinn",
      "Vienna", "Warsaw", "Zurich"]

def run_stacked():
    tweets_csv = data_dir + "april_13_15.csv"
    tweets_csv = data_dir + "May_16.csv"
    keywords = ["strongerin", "ukineu", "ukip", "leave", "remain", "euref"]
    timezones = [ ["London"],
                  ["US"],
                  ["Edinburgh"],
                  ["Dublin"] ]
    titles = ["London", "US", "Edinburgh", "Dublin"]
    colors = ["b", "g", "r", "m", "c", "y", "k"]

    # Create stacked plots
    run_experiment(tweets_csv, keywords, timezones, titles, colors)

def run_brexit():
    tweets_csv = data_dir + "april_13_15.csv"
    # Create plot for total activity
    keywords = ["", "brexit"]
    colors = ["b", "r"]

    fig = plt.figure(figsize=(6,6))
    ax = plt.axes()
    ax.set_title("Brexit-related tweet count")
    df = foreach_keyword(tweets_csv, keywords)
    plot_timelines(ax, df, colors)

    ax.set_xlabel("Date")
    ax.set_ylabel("Tweet count")
    #plt.legend(loc="best")
    plt.savefig("frequency_brexit.pdf")

if __name__ == "__main__":
    #run_brexit()
    run_stacked()
