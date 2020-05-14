import csv
import json
from io import BytesIO
import pandas as pd

class TweetStoreException(Exception):
    pass

def loadDataFrame(filename):
        with open(filename, "rb") as handler:
            file_bytes = handler.read()
            file_data = BytesIO(file_bytes)

        file_extension = "." + filename.split(".")[-1]
        if file_extension == ".json":
            df = pd.read_json(file_data)
        elif file_extension == ".csv":
            df = pd.read_csv(file_data, error_bad_lines=False)
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

    def __init__(self, filenames=None):
        self.tweets = pd.DataFrame(columns=self.features)
        if isinstance(filename, str):
            filenames = [filenames]
        for fn in filenames:
            self.addTweets(fn)

    def addTweets(self, filename):
        new_tweets = loadTweets(filename, self.features)
        self.tweets.append(new_tweets)

    def getTweetTexts(self, text_column="text"):
        return self.tweets[text_column]

    def getTweets(self):
        return self.tweets