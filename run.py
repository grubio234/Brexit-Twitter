from __future__ import print_function
from TweetAnalyzer.config import data_dir
from TweetAnalyzer import SSIXAnalyzer, VaderAnalyzer, TweetStore
from sentiment import sentimentAnalysis
from keyword_frequency import (brexitMentionFrequencyInDataset,
                                keywordSharePerTimezone)

def ssixVsVader():
    print("\n==== Test performance of this analyzer vs the general-purpose "
        "Vader sentiment analyzer.")
    test_tweets = [
        "Terrorists want us to eat more fudge",
        "But they don't want Jonas as he has no beard anymore",
        "Fuck that spineless moron cameron #mimimi",
        "Actually the EU is awesome #stay"
    ]
    score_function =  lambda n_leave, n_stay, n_undecided: n_stay - n_leave
    ssix = SSIXAnalyzer(score_function)
    vader = VaderAnalyzer()

    ssix_scores = ssix.getTweetScores(test_tweets)
    vader_scores = vader.getTweetScores(test_tweets)
    for i, tweet in enumerate(test_tweets):
        print("Tweet:", tweet)
        print("  SSIX score:  ", ssix_scores[i])
        print("  Vader score: ", vader_scores[i])

if __name__ == "__main__":

    ssixVsVader()

    save_folder = "./"
    tweet_files = data_dir + "May_16.csv"
    tweets = TweetStore(tweet_files).getTweets()

    sentimentAnalysis(tweets, save_folder)
    brexitMentionFrequencyInDataset(tweets, save_folder)
    keywordSharePerTimezone(tweets, save_folder)