from io import BytesIO
import datetime
import pandas as pd

class TweetStoreException(Exception):
    pass

def loadDataFrame(filename):
        with open(filename, "rb") as handler:
            file_bytes = handler.read()
            file_data = BytesIO(file_bytes)

        file_extension = "." + str(filename).split(".")[-1]
        if file_extension == ".json":
            df = pd.read_json(file_data)
        elif file_extension == ".csv":
            df = pd.read_csv(file_data, error_bad_lines=False)
        else:
            raise NotImplementedError("Only .json or .csv "
                "files can be loaded! '{}' files are not implemented yet"
                "".format(file_extension))
        return df

def addDate(df, time_stamp="created_at"):
    df["date"] = pd.to_datetime(df[time_stamp]).dt.date

def checkMissingFeature(df_columns, features):
    for feature in features:
        if feature not in df_columns:
            columns_string = ", ".join(df_columns)
            raise TweetStoreException("The feature '{}' is missing from the "
            "source. Available features are {}."
            "".format(feature, columns_string))

def withoutDeletedTweets(df, text_column="text"):
    return df[df[text_column] != "deleted"].copy()


class TweetStore:
    base_features = [
        "created_at",
        "id",
        "text",
        "user_time_zone"
        ]
    features = base_features + [
        "date"
    ]

    def __init__(self, filenames=None):
        self.tweets = pd.DataFrame(columns=self.features)
        if isinstance(filenames, str):
            filenames = [filenames]
        for fn in filenames:
            self.addTweets(fn)

    def loadTweets(self, filename):
        full_df = loadDataFrame(filename)
        checkMissingFeature(full_df.columns, self.base_features)
        tweets = full_df[self.base_features]
        tweets_sanitized = withoutDeletedTweets(tweets)
        addDate(tweets_sanitized)
        checkMissingFeature(tweets_sanitized.columns, self.features)
        return tweets_sanitized

    def addTweets(self, filename):
        new_tweets = self.loadTweets(filename)
        self.tweets = self.tweets.append(new_tweets)

    def getTweetTexts(self, text_column="text"):
        return self.tweets[text_column]

    def getTweets(self):
        return self.tweets