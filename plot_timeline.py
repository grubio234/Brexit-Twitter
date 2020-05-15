from __future__ import print_function
from TweetAnalyzer.config import data_dir
from TweetAnalyzer import SSIXAnalyzer, TweetStore
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
from matplotlib.dates import date2num, DayLocator, DateFormatter
from matplotlib.ticker import MultipleLocator

def get_day(created_at):
    return created_at[:10]

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
    print(keywords)
    print(len(data["text"]))
    if not keywords is None:
        data = data[data["text"].apply(valid_keyword) == True]

    if not timezones is None:
        data = data[data["user_time_zone"].apply(valid_timezone) == True]

    data["created_at"] = data["created_at"].astype("datetime64")
    a = data["created_at"].groupby(data["created_at"].dt.date).count()


    print(a)
    a = a.to_frame()
    return np.array(date2num(a.index)), np.array(a.values)

def fill_with_zeros(x, y):
    """
        Elements in x and y don't necessarily have the same length.
        This function makes them compatible by inserting zeros at the right places.
    """
    # get all distinct x values
    x_full = set([])
    for xv in x:
        x_full |= set(xv)

    N = len(x_full)
    x_filled = np.array(list(x_full))
    print(x_filled)

    x_res = len(x)*[x_filled]
    y_res = []

    for xv, yv in zip(x, y):
        y_filled = np.zeros(N)
        for j in range(xv.size):
            for i in range(N):
                if xv[j] == x_filled[i]:
                    y_filled[i] = yv[j]
                    break
        y_res.append(y_filled)

    return x_res, y_res


def plot_timelines(ax, x, y, colors, labels):
    N = len(x)
    assert N == len(y), "x and y must be lists of same length"

    bar_width = 0.8/N
    xfmt = DateFormatter('%d %b')
    ax.xaxis.set_major_formatter(xfmt)
    ax.xaxis.set_major_locator(MultipleLocator(base=1.0))
    for i in range(N):
        xk = x[i] + bar_width*(i - N/2 - 1)
        ax.bar(xk, y[i], width=bar_width, color=colors[i], label=labels[i])
    #ax.xaxis_date()
    #ax.autoscale(tight=True)

def plot_stacked_timelines(ax, x, y, colors, labels):
    """
        Plot stacked timelines to ax
    """
    N = len(x)
    assert N == len(y), "x and y must be lists of same length"
    assert N > 0, "x and y must not be empty"

    bar_width = 0.8 # bar width in plot

    ybottom = np.zeros(x[0].size) # needed for stacking
    for i in range(N):
        ax.bar(x[i], y[i], bottom=ybottom, width=bar_width, color=colors[i], label=labels[i])
        ybottom += y[i].flatten()
        print("Plotted ", labels[i])


def foreach_keyword(tweets_csv, keywords, timezones=None):
    """
        Filter for each keyword in keywords and matching timezones
    """
    x, y, labels = [], [], []
    for keyword in keywords:
        if keyword == "":
            xn, yn = get_timeline_count(tweets_csv, timezones)
            labels.append("All tweets")
        else:
            xn, yn = get_timeline_count(tweets_csv, [keyword], timezones)
            labels.append("Matching '{}'".format(keyword))
        x.append(xn)
        y.append(yn)

    return x, y, labels


def run_experiment(tweets_csv, keywords, timezoneslist, titles, colors):

    for timezones, title in zip(timezoneslist, titles):
        fig = plt.figure(figsize=(6,6))
        ax = plt.axes()
        loc = MultipleLocator(base=5.0)
        loc.MAXTICKS = 10000
        xfmt = DateFormatter('%d %b')
        ax.xaxis.set_major_formatter(xfmt)
        ax.xaxis.set_major_locator(loc)
        box = ax.get_position()
        #ax.set_position([box.x0, box.y0, box.width*0.85, box.height])
        if len(timezones) == 1 and timezones[0] == "":
            ax.set_title("All timezones")
        else:
            ax.set_title("Timezone: {}".format(title))

        x, y, labels = foreach_keyword(tweets_csv, keywords, timezones)
        xf, yf = fill_with_zeros(x, y)
        plot_stacked_timelines(ax, xf, yf, colors, labels)

        ax.set_xlabel("Date")
        ax.set_ylabel("Tweet count")
        ax.xaxis_date()
        ax.autoscale()
        #plt.legend(loc="best", bbox_to_anchor=(1, 0.6))
        plt.savefig("frequency_stacked_{}.pdf".format(title))

def timeZonesEurope():
    return ["Amsterdam", "Andorra", "Athens", "Belfast", "Belgrade", "Berlin", "Bern",
      "Brussels", "Bucharest", "Budapest", "Copenhagen", "Dublin", "Edinburgh",
      "Helsinki", "Istanbul", "Kaliningrad", "Kiev", "Lisbon", "London", "Luxembourg",
      "Madrid", "Malta", "Minsk", "Moscow", "Oslo", "Paris", "Prague", "Riga",
      "Rome", "Sarajevo", "Skopje", "Sofia", "Sofia", "Stockholm", "Tallinn",
      "Vienna", "Warsaw", "Zurich"]

def run_stacked():
    tweets_csv = data_dir + "april_13_15.csv"
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
    x, y, labels = foreach_keyword(tweets_csv, keywords)
    plot_timelines(ax, x, y, colors, labels)

    ax.set_xlabel("Date")
    ax.set_ylabel("Tweet count")
    #plt.legend(loc="best")
    plt.savefig("frequency_brexit.pdf")

if __name__ == "__main__":
    #run_brexit()
    run_stacked()
