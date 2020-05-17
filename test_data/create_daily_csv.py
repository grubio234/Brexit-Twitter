""""
As the original files were not kept, there is no reason to run this script.
It is merely kept for the sake of completeness.

This is the script that was run on our original data to produce the per-day
.csv files.

A FutureWarning is thrown by pandas/numpy.
This seems to stem from specifying the index_col when reading a very large
number of entries (from a csv file):
Comparisons have to be perform between the indizes to check that they are
unique and thus valid indizes.
The warning is thrown starting from files with ~ one million entries.
Our data set consists of roughly 1.3 million unique tweets.
"""
from __future__ import print_function
import pandas as pd
from merge_to_single_csv import mergeCSV
from coss_format_to_csv import dailyCOSSToCSV

def splitToDailyCSV(df, file_prefix):
    dates = pd.to_datetime(df.created_at).dt.date
    for the_day in dates.unique():
        day = df[dates == the_day]
        file_name = file_prefix + the_day.strftime("%Y-%m-%d") + ".csv"
        day.to_csv(file_name)
        print("File saved at: {}.".format(file_name))

def createDaily2016(daily_data_folder="./"):
    coss_data_folder = "brexit_tweets_COSS_2016/"
    dailyCOSSToCSV(coss_data_folder, daily_data_folder)

def createDaily2017(daily_data_folder="./"):
    csv_source_2017 = [
        "brexit_all_2.csv",
        "brexit_backup0805.csv",
        "brexit_data.csv",
    ]
    full_2017_destination = "all_2017.csv"

    try:
        full_2017 = pd.read_csv(full_2017_destination, index_col="id")
    except:
        print("Loading the file {} did not work. The script will attempt to"
            "create that file from the pieces. This can take a minute."
            "".format(full_2017_destination))
        mergeCSV(csv_source_2017, destination=full_2017_destination)
        full_2017 = pd.read_csv(full_2017_destination, index_col="id")
    splitToDailyCSV(full_2017, daily_data_folder)

if __name__ == "__main__":
    daily_data_folder = "./"
    createDaily2016(daily_data_folder)
    createDaily2017(daily_data_folder)