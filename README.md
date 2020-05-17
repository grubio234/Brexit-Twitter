# Brexit-Twitter

<p align="center">
  <img src="assets/brexit.jpg" alt="brexit-imge"/>
</p>

A Twitter sentiment analysis studying the Brexit referendum 2017.

This code was originally created for the final project of [Data Science in Techno-Socio-Economic Systems](http://www.vorlesungsverzeichnis.ethz.ch/Vorlesungsverzeichnis/lerneinheit.view?lang=en&lerneinheitId=113553&semkez=2017S&ansicht=KATALOGDATEN&) course at ETH Zurich in 2017.
The team members were [@Cryoris](https://github.com/Cryoris) and [@kunathj](https://github.com/kunathj).
The short [report](BrexitPaper_29-05-2017.pdf) should give an idea of what this project is all about.

## Deviation of the project from the report

The report is clearly only a snapshot of this project.
So far changes mainly targeted code readability and not feature enhancement.
Nevertheless you should not expect to be able to exactly reproduce the report.
Some effort went into (routines for) cleaning the tweet texts.
Some entries that were erroneous were skipped before.
Their addition will change details in the plots.

Not all plotting routines are documented in this repository.
Notably, the pie chart code is not included.
The table creation was never automated.
Some work would thus be needed to be able to dynamically reproduce the report for the sake of comparing the results.
The latex source and the original figures are stored with the [data](#the-data-location).

## Data source

This project is based on Tweets from the years 2016 and 2017.
The 2016 tweets were provided by the [COSS](https://coss.ethz.ch/) group at ETH.
The 2017 tweets were obtained via a Twitter API.
Note that the procedure for collection the tweets differed between the 2016 and 2017 campaign, but also between different days in 2017.

While those data files, are hosted externally, a small [test data set](test_data/test_tweets.csv) is provided in this repository.

The [SSIX project](https://bitbucket.org/ssix-project/brexit-gold-standard/src/master/#markdown-header-dataset) produced a _Brexit Gold Standard_.
The Sentiment analyser in our project is based on their set of humanly annotated tweets.
Those Brexit-related tweets were categorized into (_leave_, _stay_, ...) sentiments depending on the tweet text.

### The data location

Accompanying material and data is hosted on [OneDrive](https://1drv.ms/f/s!AkdwqUOfP6nWhIkfNyqrBu0hNY2bmw).
Please raise an [issue](https://github.com/kunathj/Brexit-Twitter/issues) in case this link becomes stale.
After downloading that data file, add a `custom_config.py` file similar to [the default file](TweetAnalyzer/config/default_config.py).
