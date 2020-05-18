from __future__ import print_function
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
import pandas as pd
from TweetAnalyzer.config import data_dir, test_data_dir
from TweetAnalyzer import SSIXAnalyzer, TweetStore
from util_plotting import keywordFrequencyPlot

timezones_2016_already_encountered = False
def isUTCOffsetNotTimezone(tz):
    if isinstance(tz, int):
        if not timezones_2016_already_encountered:
            timezones_2016_already_encountered = True
            print("This timezones value is an integer. The behaviour is "
                "expected for the 2016 tweets colleted by COSS. They were not "
                "collecting the user's timezone but instead his utc offset in "
                "minutes. Here, these values will be interpreted as 'timezone "
                "not provided'. This information will only be printed once.")
        return True
    return False

def dailyCountsForKeywordGroup(tweets, keyword_group, timezones=None):
    def hasKeyword(text):
        for keyword in keyword_group:
            if keyword in text:
                return True
        return False
    def isInTimezone(t):
        if isUTCOffsetNotTimezone(t):
            return False
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

def timeZonesEurope():
    return ["Amsterdam", "Andorra", "Athens", "Belfast", "Belgrade", "Berlin",
        "Bern", "Brussels", "Bucharest", "Budapest", "Copenhagen", "Dublin",
        "Edinburgh", "Helsinki", "Istanbul", "Kaliningrad", "Kiev", "Lisbon",
        "London", "Luxembourg", "Madrid", "Malta", "Minsk", "Moscow", "Oslo",
        "Paris", "Prague", "Riga", "Rome", "Sarajevo", "Skopje",
        "Sofia", "Stockholm", "Tallinn", "Vienna", "Warsaw", "Zurich"]

def keywordSharePerTimezone(tweets, save_folder="./"):
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

    for name, zones in timezones.items():
        df = dailyCountsPerGroup(tweets, keywords, zones)

        title = "Timezone: {}".format(name)
        save_as = "frequency_stacked_{}.pdf".format(name)
        keywordFrequencyPlot(df, title, save_as, colors, mode="stacked")

def brexitMentionFrequencyInDataset(tweets, save_folder="./"):
    keywords = {
        "All tweets": None,
        "Matching 'brexit'": "brexit",
    }
    colors = ["b", "r"]

    df = dailyCountsPerGroup(tweets, keywords)

    title = "Brexit-related tweet count"
    save_as = "frequency_brexit.pdf"
    keywordFrequencyPlot(df, title, save_as, colors)

if __name__ == "__main__":
    tweet_files = [str(fn) for fn in Path(test_data_dir).glob("*.csv")]
    tweets = TweetStore(tweet_files).getTweets()
    brexitMentionFrequencyInDataset(tweets)
    keywordSharePerTimezone(tweets)
