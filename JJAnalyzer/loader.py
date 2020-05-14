import json
import csv
import pandas
import os
#from StringIO import StringIO # Python2.
from io import BytesIO # Python2&3.
import warnings

def safe_to_lower(x):
    try:
        res = x.lower()
    except:
        warnings.warn("x has no method 'lower()', x = {}".format(x))
        res = "empty"
    return res

class Loader:

    data = []

    def __init__(self, filename):
        self.load_file(filename)

    def load_file(self, filename):
        try:
            with open(filename, "rb") as handler:
                content = handler.read()
        except:
            raise SystemError("Couldn't open file " + filename)

        io = BytesIO(content)
        suffix = os.path.splitext(filename)[1]
        if suffix == ".json":
            self.data = pandas.read_json(io)
        elif suffix == ".csv":
            self.data = pandas.read_csv(io, error_bad_lines=False)
        else:
            raise NotImplementedError("Only .json or .csv files can be loaded!")

        self.remove_deleted()
        self.to_lower()

        return self


    def to_lower(self):
        #self.data["text"] = self.data["text"].apply(lambda x: x.lower())
        self.data["text"] = self.data["text"].apply(safe_to_lower)

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
