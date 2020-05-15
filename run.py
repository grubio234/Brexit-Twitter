from __future__ import print_function
import runpy
from sentiment import sentimentAnalysis
from TweetAnalyzer.config import data_dir

def simpleTest():
    from TweetAnalyzer.config import data_dir
    from TweetAnalyzer import SSIXAnalyzer, VaderAnalyzer

    ssix = SSIXAnalyzer(data_dir)
    vader = VaderAnalyzer()

    # Test case 1
    tweets = ["Terrorists want us to eat more fudge",
              "But they don't want Jonas as he has no beard anymore",
              "Fuck that spineless moron cameron #mimimi",
              "Actually the EU is awesome #stay"]

    print(ssix.getTweetScores(tweets))
    print(vader.getTweetScores(tweets))

def testTimeLine():
    runpy.run_path("plot_timeline.py")

if __name__ == "__main__":
    save_folder = "./"

    simpleTest()
    sentimentAnalysis(data_dir + "May_16.csv", save_folder)
    testTimeLine()