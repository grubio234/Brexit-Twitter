from __future__ import print_function
import runpy

def simpleTest():
    from JJAnalyzer.config import data_dir
    from JJAnalyzer import SSIXAnalyzer, VaderAnalyzer

    ssix = SSIXAnalyzer(data_dir)
    vader = VaderAnalyzer()

    # Test case 1
    tweets = ["Terrorists want us to eat more fudge",
              "But they don't want Jonas as he has no beard anymore",
              "Fuck that spineless moron cameron #mimimi",
              "Actually the EU is awesome #stay"]

    print(ssix.get_values(tweets))
    print(vader.get_values(tweets))

def testSentiment():
    runpy.run_path("sentiment.py")

def testTimeLine():
    runpy.run_path("plot_timeline.py")

if __name__ == "__main__":
    simpleTest()
    testSentiment()
    testTimeLine()