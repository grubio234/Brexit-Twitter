""""
Create a .csv file with a small subset of the tweets from each day.

The resulting file is checked into the source control to have a small test
provided directly with the source code.
This script is mainly provided for the sake of completeness.
If you choose to run it, be careful to check what you check in to the history.
While it is already bad practice to provide the rather lengthy test set, it
would be even worse to alter its contents and blow up the repository.
"""
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
import pandas as pd

if __name__ == "__main__":
    csv_folder = Path.home() / "Downloads" / "brexit_tweets"
    tweets_per_day = 100
    year = "[0-9]"*4
    month = "[0-9]"*2
    day = "[0-9]"*2
    name_pattern = "{}-{}-{}.csv".format(year, month, day)
    daily_test_tweets = {}
    for daily_csv in csv_folder.glob(name_pattern):
        daily_csv = str(daily_csv)
        daily_tweets = pd.read_csv(daily_csv, index_col="id")
        test_tweets_today = daily_tweets.head(tweets_per_day)
        daily_test_tweets[daily_csv] = test_tweets_today
    sorted_days = sorted(list(daily_test_tweets))
    time_sorted_tweets = [daily_test_tweets[day] for day in sorted_days]
    test_tweets = pd.concat(time_sorted_tweets)
    test_name = "test_tweets.csv"
    test_tweets.to_csv(test_name)