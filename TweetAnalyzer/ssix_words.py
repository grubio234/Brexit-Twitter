from collections import defaultdict
import re
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
from .tweet_store import TweetStore, loadDataFrame


analyzer_data = Path(__file__).parent / "data"
sentiments = ["leave", "stay", "undecided"]
unwanted_chars = "!\"§$%&/()=?{[]}\\`´*+~'-_.:,;<>|^°"

def getCleanedWord(word):
    word = word.lower()
    word = word.strip(unwanted_chars)
    word = re.sub(r"[^\x20-\x7e]", "", word)
    return word

def getValidWords(sentence):
    valid_words = []
    for word in sentence.split():
        if not "http" in word:
            cleaned_word = getCleanedWord(word)
            valid_words.append(cleaned_word)
    return valid_words

def getSSIXData():
    ssix_sentiments_file = analyzer_data / "brexit-sample-20160506-annotated.json"
    ssix_sentiments = loadDataFrame(str(ssix_sentiments_file))

    ssix_tweets_file = analyzer_data / "ssix_tweets.csv"
    ssix_tweets = TweetStore(str(ssix_tweets_file)).getTweets()

    ssix_data = ssix_tweets.merge(ssix_sentiments, on="id", how="inner")
    return ssix_data

def getRawWordCounts(df, sentiment):
    word_counts = defaultdict(int)
    single_sentiment_tweet_texts = df[df["sentiment"] == sentiment]["text"]
    for tweet_text in single_sentiment_tweet_texts:
        for word in getValidWords(tweet_text):
            word_counts[word] += 1
    return word_counts

def removeCommonWords(word_dict):
    common_wordlist = analyzer_data / "common_words.txt"
    with open(common_wordlist) as f:
        for line in f.readlines():
            common_word = line.strip()
            word_dict.pop(common_word, None)

def normalizeDictValueSumToOne(dictionary):
        norm_factor = 1. / sum(dictionary.values())
        for key in dictionary:
            dictionary[key] = norm_factor * dictionary[key]

def getWordQuota(df, sentiment):
    word_counts = getRawWordCounts(df, sentiment)
    removeCommonWords(word_counts)
    normalizeDictValueSumToOne(word_counts)
    return word_counts

def getWordQuotaPerSentiment():
    ssix_data = getSSIXData()
    word_quota_per_sentiment = {k: {} for k in sentiments}
    for sentiment in word_quota_per_sentiment:
        word_quota = getWordQuota(ssix_data, sentiment)
        word_quota_per_sentiment[sentiment] = word_quota
    return word_quota_per_sentiment

def getWordScore(word_quota_per_sentiment, score_function):
    union_of_words = set().union(*word_quota_per_sentiment.values())
    word_score = {}
    for word in union_of_words:
        quota_per_sentiment = []
        for sentiment in sentiments:
            quota = word_quota_per_sentiment[sentiment][word]
            quota_per_sentiment.append(quota)
        score = score_function(*quota_per_sentiment)
        word_score[word] = score
    return word_score

def makeWordScores(score_function=None):
    """score_function : 3 floats -> 1 float.
    """
    if score_function is None:
        score_function =  lambda n_leave, n_stay, n_undecided: n_stay - n_leave

    word_quota_per_sentiment = getWordQuotaPerSentiment()
    word_score = getWordScore(word_quota_per_sentiment, score_function)
    return word_score