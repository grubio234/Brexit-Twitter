
from __future__ import print_function
import re
import json
import pandas as pd
from io import StringIO
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import numpy as np

analyzer_data = Path(__file__).parent / "data"
class Analyzer:
    unwanted_chars = "!\"§$%&/()=?{[]}\\`´*+~'-_.:,;<>|^°"

    def __init__(self):
        pass

    def getTweetScore(self, word):
        raise NotImplementedError

    def getTweetScores(self, tweet_text_list):
        vals = np.zeros(len(tweet_text_list))
        for i, tweet_text in enumerate(tweet_text_list):
            vals[i] = self.getTweetScore(tweet_text)
        return vals

    def getCleanedWord(self, word):
        word = word.lower()
        word = word.strip(self.unwanted_chars)
        word = re.sub(r"[^\x20-\x7e]", "", word)
        return word

    def getValidWords(self, sentence):
        valid_words = []
        for word in sentence.split():
            if not "http" in word:
                cleaned_word = self.getCleanedWord(word)
                valid_words.append(cleaned_word)
        return valid_words


class SSIXAnalyzer(Analyzer):

    weight = {}
    common_wordlist = analyzer_data / "common_words.txt"

    def removeCommonWords(self, dictionary):
        filename = self.data_dir + self.common_wordlist
        with open(filename) as f:
            for line in f.readlines():
                word = line.strip()
                try:
                    del dictionary[word]
                except:
                    pass

    def add_text_to_dict(self, dictionary, text):
        wordlist = self.getValidWords(text)
        for word in wordlist:
            try:
                dictionary[word] += 1
            except:
                dictionary[word] = 1

    def normalizeToOne(self, dictionary):
        factor = 1./np.sum(dictionary.values())
        for key in dictionary:
            dictionary[key] = dictionary[key]*factor

    def __init__(self, data_dir, ssix_data="ssix.json", ssix_tweets="ssix_tweets.csv"):

        self.data_dir = data_dir

        try:
            print("Trying to load weight dict from " + data_dir + "weight.json..")
            self.weight = json.load(open(data_dir+"weight.json"))
            return
        except:
            print("Weight dict not found in weight.json, recomputing it..")

        with open(data_dir + ssix_tweets) as handler:
            tweets_csv = handler.read()
        tweets_panda = pd.read_csv(StringIO.StringIO(tweets_csv))

        print("Initializing dictionaries from SSIX Brexit Gold Standard..")
        with open(data_dir + ssix_data) as handler:
            ssix = pd.read_json(handler)

        # tweets now contains all information: sentiments and twitter data
        tweets = ssix.merge(tweets_panda, on="id", how="inner")

        # put words in dicts
        leave, stay, undecided = {}, {}, {}
        for i in xrange(len(tweets.index)):
            if tweets.loc[i, "text"] != "deleted":
                sentiment = tweets.loc[i, "sentiment"]
                text = tweets.loc[i, "text"]

                if sentiment == "leave":
                    self.add_text_to_dict(leave, text)
                elif sentiment == "stay":
                    self.add_text_to_dict(stay, text)
                else:
                    self.add_text_to_dict(undecided, text)

        print("Computing weight dictionary..")
        dictionaries = [leave, stay, undecided]

        for dictionary in dictionaries:
            self.removeCommonWords(dictionary)
            self.normalizeToOne(dictionary)

        all_keys = leave.keys()
        all_keys.extend(stay.keys())
        all_keys.extend(undecided.keys())

        for key in all_keys:
            occurences = np.zeros(3)
            for i, dictionary in enumerate(dictionaries):
                try:
                    occurences[i] += dictionary[key]
                except:
                    pass
            self.weight[key] = self.weight_function(*occurences)

        print("Max values: ", np.max(self.weight.values()))

        print("Saving weight dict to " + data_dir + "weight.json ..")
        try:
            json.dump(self.weight, open(data_dir+"weight.json", "w"))
        except:
            print("Couldn't save dictionary to file.")

        print("Done.")

    def weight_function(self, n_leave, n_stay, n_undecided):
        return n_stay - n_leave
        #return (b**2 - a**2)/np.log(np.e - 1 + a + b + c)

    def getTweetScore(self, tweet_text):
        val = 0
        words_in_tweet = self.getValidWords(tweet_text)
        for word in words_in_tweet:
            if word in self.weight:
                val += self.weight[word]
        return val


def vaderLexiconFile(directory=analyzer_data):
    vader_lexicon = ( directory / "sentiment" /
        "vader_lexicon.zip" / "vader_lexicon" / "vader_lexicon.txt" )
    if not vader_lexicon.is_file():
        nltk.download("vader_lexicon", download_dir=directory)
    return str(vader_lexicon)

class VaderAnalyzer(Analyzer):

    analyzer = SentimentIntensityAnalyzer(vaderLexiconFile())

    def getTweetScore(self, tweet_text):
        return self.analyzer.polarity_scores(tweet_text)['compound']