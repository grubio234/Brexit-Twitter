import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from .ssix_words import analyzer_data, getValidWords, makeWordScores

class Analyzer:
    def __init__(self):
        pass

    def getTweetScore(self, word):
        raise NotImplementedError

    def getTweetScores(self, tweet_text_list):
        scores = []
        for tweet_text in tweet_text_list:
            scores.append(self.getTweetScore(tweet_text))
        return scores

class SSIXAnalyzer(Analyzer):
    def __init__(self, score_function=None):
        self.word_scores = makeWordScores(score_function)

    def getTweetScore(self, tweet_text):
        score = 0
        words_in_tweet = getValidWords(tweet_text)
        for word in words_in_tweet:
            if word in self.word_scores:
                score += self.word_scores[word]
        return score


def vaderLexiconFile(directory=analyzer_data):
    vader_lexicon = ( directory / "sentiment" /
        "vader_lexicon.zip" / "vader_lexicon" / "vader_lexicon.txt" )
    if not vader_lexicon.exists():
        nltk.download("vader_lexicon", download_dir=directory)
    return str(vader_lexicon)

class VaderAnalyzer(Analyzer):
    analyzer = SentimentIntensityAnalyzer(vaderLexiconFile())

    def getTweetScore(self, tweet_text):
        return self.analyzer.polarity_scores(tweet_text)['compound']