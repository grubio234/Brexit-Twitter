import json
import csv
import pandas
import os
from io import BytesIO # Python2&3.
import warnings

def toLowerCaseHelper(string):
    try:
        lower_case_string = string.lower()
    except AttributeError:
        warnings.warn("x has no method 'lower()', x = {}".format(x))
        lower_case_string = "empty"
    return lower_case_string

class TweetStore:

    data = []

    def __init__(self, filename):
        self.load_file(filename)

    def load_file(self, filename):
        with open(filename, "rb") as handler:
            file_content = handler.read()

        io = BytesIO(file_content)
        suffix = os.path.splitext(filename)[1]
        if suffix == ".json":
            self.data = pandas.read_json(io)
        elif suffix == ".csv":
            self.data = pandas.read_csv(io, error_bad_lines=False)
        else:
            raise NotImplementedError("Only .json or .csv files can be loaded!")

        self.remove_deleted()
        self.toLowerCase()

        return self


    def toLowerCase(self):
        self.data["text"] = self.data["text"].apply(toLowerCaseHelper)

    def remove_retweets(self):
        rt = lambda x: x[:2] == "rt"
        self.data = self.data[self.data["text"].apply(rt) == False]

    def remove_deleted(self, colname="text"):
        self.data = self.data[self.data["text"] != "deleted"]

    def remove_if_contains(self, keyword, df=None):
        """
            Remove all tweets that contain 'keyword' from self.data (if df is None)
            or from df (if df is given)
        """
        contains_key = lambda x: keyword in x

        if df is None:
            count_before = self.data["id"].count()
            self.data = self.data[self.data["text"].apply(contains_key) == False]
            count_after = self.data["id"].count()
        else:
            count_before = df["id"].count()
            df = df[df["text"].apply(contains_key) == False]
            count_after = df["id"].count()

        # return number of removed elements
        return count_before - count_after

    def get_tweets(self, colname="text"):
        return list(self.data[colname])

    def get_dataframe(self):
        return self.data
