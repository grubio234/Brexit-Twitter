from __future__ import print_function
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DayLocator, DateFormatter
from matplotlib.ticker import MultipleLocator
import numpy as np
from TweetAnalyzer.config import data_dir
from TweetAnalyzer import SSIXAnalyzer, TweetStore

print("Starting program..")

ssix = SSIXAnalyzer(data_dir)

leave_keys = ["ukip", "no2eu", "britainout", "voteleave", "leaveeu"]
other_keys = ["euref", "eureferendum", "takecontrol"]
stay_keys = ["#strongerin", "remain", "ukineu"]


def count_for_set(df, keys):

    # distinct days
    counts = defaultdict(int)

    for i, idx in enumerate(df.index):
        if i % 5000 == 0:
            print("Processed {} tweets".format(i))

        tweet = df.loc[idx, "text"]
        day = df["date"][idx]
        for key in keys:
            if key in tweet:
                counts[day] += 1

                df = df.drop(idx)
                break

    return df, counts

tweets = TweetStore(data_dir + "May_16.csv")
df = tweets.getTweets()

print("==== Size : {} ====".format(len(df.index)))

# Remove tweets containing keywords mapped to a fixed sentiment
df, counts_leave  = count_for_set(df, leave_keys)
df, counts_other = count_for_set(df, other_keys)
df, counts_stay = count_for_set(df, stay_keys)

print("==== Size : {} ====".format(len(df.index)))

print("Days   : ", df["date"].unique)
print("==== Leave ====")
print("Counts : ", counts_leave)
print("\n")
print("==== Other ====")
print("Counts : ", counts_other)
print("\n")
print("==== Stay  ====")
print("Counts : ", counts_stay)
print("\n")

# Sentiment analysis for remaining tweets
threshold_leave = -0.00661286
threshold_stay = 0.00830461

for i, idx in enumerate(df.index):
    if i % 5000 == 0:
        print("Processed {} tweets".format(i))

    tweet = df.loc[idx, "text"]
    day = df["date"][idx]
    val = ssix.getTweetScores([tweet])[0]
    use_threshold = True
    if use_threshold:
        if val <= threshold_leave:
            counts_leave[day] += 1
        elif val >= threshold_stay:
            counts_stay[day] += 1
        else:
            counts_other[day] += 1
    else:
        if val < 0:
            counts_leave[day] += 1
        elif val > 0:
            counts_stay[day] += 1
        else:
            counts_other[day] += 1

print("Dates   : ", df["date"])
print("==== Leave ====")
print("Counts : ", counts_leave)
print("\n")
print("==== Other ====")
print("Counts : ", counts_other)
print("\n")
print("==== Stay  ====")
print("Counts : ", counts_stay)
print("\n")


loc = MultipleLocator(base=1.0)
xfmt = DateFormatter('%d %b')

fig = plt.figure(figsize=(6,6))
ax = plt.axes()
ax.xaxis.set_major_formatter(xfmt)
ax.xaxis.set_major_locator(loc)
ax.set_title("Tweet count for leave / stay")
w = 0.2
y = np.array([counts_leave[day] for day in df["date"]])
np_days = date2num(df["date"])
ax.bar(np_days, y, width=w, color="r", label="leave")
y2 = np.array([counts_stay[day] for day in df["date"]])
ax.bar(np_days+w, y2, width=w, color="b", label="stay")
ax.set_xlabel("Dates")
ax.set_ylabel("Tweet count")
plt.savefig("total_daycount_ls.pdf")

all_keys = set(())
dictionaries = [counts_leave, counts_stay, counts_other]

for dictionary in dictionaries:
    all_keys |= set(dictionary.keys())

for key in all_keys:
    for dictionary in dictionaries:
        if key not in dictionary:
            dictionary[key] = 0


counts_leave_vals = np.array([counts_leave[day] for day in df["date"]])
counts_stay_vals = np.array([counts_stay[day] for day in df["date"]])
counts_other_vals = np.array([counts_other[day] for day in df["date"]])
tot = counts_leave_vals + counts_stay_vals + counts_other_vals
tot = np.max(np.vstack((tot, np.ones_like(tot))), axis=0)
counts_leave_normalised = 1.0*counts_leave_vals/tot
counts_other_normalised = 1.0*counts_other_vals/tot
counts_stay_normalised = 1.0*counts_stay_vals/tot

fig = plt.figure(figsize=(6,6))
ax = plt.axes()
ax.xaxis.set_major_formatter(xfmt)
ax.xaxis.set_major_locator(loc)
ax.set_title("Tweet count for leave / other / stay")
w = 0.6
ax.bar(np_days, counts_leave_normalised, width=w, color="r", label="leave")
ax.bar(np_days, counts_stay_normalised, width=w, bottom=counts_leave_normalised, color="b", label="stay")
ax.bar(np_days, counts_other_normalised, width=w, bottom=1-counts_other_normalised, color="g", label="other")
ax.set_xlabel("Dates")
ax.set_ylabel("Tweet count")
plt.savefig("relative_daycount.pdf")