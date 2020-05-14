# -*- coding: utf-8 -*-
from __future__ import print_function
from .config import data_dir
import numpy as np # numpy
import re # regular expressions
import json # json strings
import os.path
import pandas as pd # panda dataframe
import nltk
from io import StringIO
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path

from nltk.sentiment.vader import SentimentIntensityAnalyzer

analyzer_data = Path(__file__).parent / "data"
class Analyzer:

    data_dir = ""
    common_wordlist = analyzer_data / "common_words.txt"
    unwanted_chars = "!\"§$%&/()=?{[]}\\`´*+~'-_.:,;<>|^°"

    def __init__(self):
        pass

    def get_value(self, word):
        raise NotImplementedError

    def get_values(self, textlist):
        raise NotImplementedError

    def validate(self, text):
        """
            Validate a given sentence
              text (string) : input sentence
            Returns:
              wordlist (list) : list of valid words in the sentence
        """
        wordlist = []
        for word in text.split():
            word = word.lower()
            word = word.strip(self.unwanted_chars)
            word = re.sub(r"[^\x20-\x7e]", "", word)
            if not "http" in word:
                wordlist.append(word)
        return wordlist

    def remove_common(self, dictionary):
        """
            Remove common words from given dictionary
        """
        filename = self.data_dir + self.common_wordlist
        with open(filename) as f:
            for line in f.readlines():
                word = line.strip()
                try:
                    del dictionary[word]
                except:
                    pass

    def normalize(self, dictionary):
        """
            Normalize a dictionary, such that the sum of all values is 1
        """
        factor = 1./np.sum(dictionary.values())
        for key in dictionary:
            dictionary[key] = dictionary[key]*factor

class SSIXAnalyzer(Analyzer):

    weight = {}
    data_dir = ""

    def add_text_to_dict(self, dictionary, text):
        """
            Add all words in text to dictionary by increasing value of the dictionary by
            one, using the word as key
        """
        wordlist = self.validate(text)
        for word in wordlist:
            try:
                dictionary[word] += 1
            except:
                dictionary[word] = 1

    def __init__(self, data_dir, ssix_data="ssix.json", ssix_tweets="ssix_tweets.csv"):

        self.data_dir = data_dir

        # try to load weight dict from file, if not possible re-compute it
        try:
            print("Trying to load weight dict from " + data_dir + "weight.json..")
            self.weight = json.load(open(data_dir+"weight.json"))
            return
        except:
            print("Weight dict not found in weight.json, recomputing it..")

        # get ssix tweets
        with open(data_dir + ssix_tweets) as handler:
            tweets_csv = handler.read()
        tweets_panda = pd.read_csv(StringIO.StringIO(tweets_csv))

        # tokenize
        #tweets_panda["tokenized"] = ""
        #for i, raw_text in enumerate(tweets_panda["text"]):
        #    tweets_panda.set_value(i, "tokenized", nltk.word_tokenize(unicode(raw_text, "utf-8")))

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
        # list of dictionaries for easy handling
        dictionaries = [leave, stay, undecided]

        # remove common words from dictionaries and normalize
        for dictionary in dictionaries:
            self.remove_common(dictionary)
            self.normalize(dictionary)

        # get a set of all keys
        all_keys = leave.keys()
        all_keys.extend(stay.keys())
        all_keys.extend(undecided.keys())

        # compute weight dictionary
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

    def weight_function(self, a, b, c):
        """
            Weight function
              a (float) : Number of occurences in leave
              b (float) : Number of occurences in stay
              c (float) : Number of occurences in undecided
        """
        return b - a
        #return (b**2 - a**2)/np.log(np.e - 1 + a + b + c)

    def judge_text(self, text):
        """
            Compute sentiment of given string
              text (string) : input string
            Returns:
              val (float) : sentiment of string
        """
        wordlist = self.validate(text)
        val = 0
        for word in wordlist:
            try:
                val += self.weight[word]
            except:
                pass
        return val


    def get_value(self, word):
        """
            Get value of a single word
        """
        wordlist = self.validate(word)
        if len(wordlist) > 1:
            raise ValueError("get_value takes only a single word!")
        try:
            val = self.weight[wordlist[0]]
        except:
            val = 0
        return val

    def get_values(self, textlist):
        """
            Get values of a list of strings
              textlist (list) : list of strings, input sentences
            Returns:
              vals (list) : list of floats, sentiment for each input sentence
        """
        vals = []
        for text in textlist:
            vals.append(self.judge_text(text))
        return vals


def vaderLexiconFile(directory=analyzer_data):
    vader_lexicon_file = ( directory / "sentiment" /
        "vader_lexicon.zip" / "vader_lexicon" / "vader_lexicon.txt" )
    if not vader_lexicon_file.is_file():
        nltk.download("vader_lexicon", download_dir=directory)
    return str(vader_lexicon_file)

class VaderAnalyzer(Analyzer):

    analyzer = SentimentIntensityAnalyzer(vaderLexiconFile())

    def __init__(self):
        pass

    def get_value(self, word):
        """
            Get value of a single word
        """
        wordlist = self.validate(word)
        if len(wordlist) > 1:
            raise ValueError("get_value takes only a single word!")
        return self.analyzer.polarity_scores(wordlist[0])['compound']

    def get_values(self, textlist):
        """
            Get values of a list of strings
              textlist (list) : list of strings, input sentences
            Returns:
              vals (list) : list of floats, sentiment for each input sentence
        """
        vals = []
        for text in textlist:
            vals.append(self.analyzer.polarity_scores(text)['compound'])
        return vals
