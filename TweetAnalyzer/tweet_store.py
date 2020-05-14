import json
import csv
import pandas
from io import BytesIO # Python2&3.
import warnings

class TweetStoreException(Exception):
    pass

def loadDataFrame(filename):
        with open(filename, "rb") as handler:
            file_bytes = handler.read()
            file_data = BytesIO(file_bytes)

        file_extension = "." + filename.split(".")[-1]
        if file_extension == ".json":
            df = pandas.read_json(file_data)
        elif file_extension == ".csv":
            df = pandas.read_csv(file_data, error_bad_lines=False)
        else:
            raise TweetStoreException("NotImplementedError: Only .json or .csv "
                "files can be loaded! '{}' files are not implemented yet"
                "".format(file_extension))
        return df

def checkMissingColumn(df_columns, features):
    for feature in features:
        if feature not in df_columns:
            columns_string = ", ".join(df_columns)
            raise TweetStoreException("The feature '{}' is missing from the "
            "source. Available features are {}."
            "".format(feature, columns_string))

def withoutDeletedTweets(df, text_column="text"):
    return df[df[text_column] != "deleted"]

def loadTweets(filename, features):
    full_df = loadDataFrame(filename)
    checkMissingColumn(full_df.columns, features)
    tweets = full_df[features]
    tweets_sanitized = withoutDeletedTweets(tweets)
    return tweets_sanitized


class TweetStore:
    features = [
        "created_at",
        "id",
        "text",
        "user_time_zone"
        ]

    def __init__(self, filename):
        self.load_file(filename)

    def load_file(self, filename):
        self.dataFrame = loadTweets(filename, self.features)


    def remove_retweets(self):
        rt = lambda x: x[:2] == "rt"
        self.dataFrame = self.dataFrame[self.dataFrame["text"].apply(rt) == False]


    def remove_if_contains(self, keyword, df=None):
        """
            Remove all tweets that contain 'keyword' from self.dataFrame (if df is None)
            or from df (if df is given)
        """
        contains_key = lambda x: keyword in x

        if df is None:
            count_before = self.dataFrame["id"].count()
            self.dataFrame = self.dataFrame[self.dataFrame["text"].apply(contains_key) == False]
            count_after = self.dataFrame["id"].count()
        else:
            count_before = df["id"].count()
            df = df[df["text"].apply(contains_key) == False]
            count_after = df["id"].count()

        # return number of removed elements
        return count_before - count_after

    def get_tweets(self, colname="text"):
        return list(self.dataFrame[colname])

    def get_dataframe(self):
        return self.dataFrame
