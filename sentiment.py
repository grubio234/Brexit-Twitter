from __future__ import print_function
print("Starting imports..")
# Own modules
from TweetAnalyzer.config import data_dir
from TweetAnalyzer import SSIXAnalyzer, TweetStore

# Python modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import date2num

def dictincr(dictionary, value):
    try:
        dictionary[value] += 1
    except:
        dictionary[value] = 1

print("Starting program..")

ssix = SSIXAnalyzer(data_dir)

leave_keys = ["ukip", "no2eu", "britainout", "voteleave", "leaveeu"]
other_keys = ["euref", "eureferendum", "takecontrol"]
stay_keys = ["#strongerin", "remain", "ukineu"]

def remove_if_contains(df, key):
    print("indices:", df.index)
    count_before = df["id"].count()
    df = df[df["text"].apply(contains_key) == False]
    count_after = df["id"].count()

    return df, count_before - count_after

def count_for_set(df, dates, keys):
    #dates_set = df["created_at"].dt.date.to_frame()
    #dates_set = np.array(date2num(dates_set)).flatten()
    dates_set = df["created_at"].dt.date.apply(date2num)
    print(set(dates_set.values))

    # distinct days
    counts = {}

    for i, idx in enumerate(df.index):
        if i % 5000 == 0:
            print("Processed {} tweets".format(i))

        tweet = df.loc[idx, "text"]
        day = dates_set[idx]
        for key in keys:
            if key in tweet:
                try:
                    counts[day] += 1
                except:
                    counts[day] = 1

                df = df.drop(idx)
                break

    return df, counts

l = TweetStore(data_dir + "May_16.csv")
df = l.getTweets()
df["created_at"] = pd.to_datetime(df["created_at"])
#dates = df["created_at"].dt.date.to_frame()
#dates = np.array(date2num(dates)).flatten()
dates = df["created_at"].dt.date.apply(date2num)

print("==== Size : {} ====".format(len(df.index)))

# Remove tweets containing keywords mapped to a fixed sentiment
df, counts_leave  = count_for_set(df, dates, leave_keys)
df, counts_other = count_for_set(df, dates, other_keys)
df, counts_stay = count_for_set(df, dates, stay_keys)

print("==== Size : {} ====".format(len(df.index)))

print("Days   : ", dates)
print("==== Leave ====")
print("Counts : ", counts_leave)
print("\n")
print("==== Other ====")
print("Counts : ", counts_other)
print("\n")
print("==== Stay  ====")
print("Counts : ", counts_stay)
print("\n")

# Save counts of keywords only for later usage with python -i
counts_leave_base = counts_leave.copy()
counts_other_base = counts_other.copy()
counts_stay_base = counts_stay.copy()

# Sentiment analysis for remaining tweets
threshold_leave = -0.00661286
threshold_stay = 0.00830461

#dates = df["created_at"].dt.date.to_frame()
#dates = np.array(date2num(dates)).flatten()
dates = df["created_at"].dt.date.apply(date2num)

for i, idx in enumerate(df.index):
    if i % 5000 == 0:
        print("Processed {} tweets".format(i))

    tweet = df.loc[idx, "text"]
    day = dates[idx]
    val = ssix.getTweetScores([tweet])[0]
    use_threshold = True
    if use_threshold:
        if val <= threshold_leave:
            dictincr(counts_leave, day)
        elif val >= threshold_stay:
            dictincr(counts_stay, day)
        else:
            dictincr(counts_other, day)
    else:
        if val < 0:
            dictincr(counts_leave, day)
        elif val > 0:
            dictincr(counts_stay, day)
        else:
            dictincr(counts_other, day)
"""
counts_stay = np.array(counts_stay.values())
counts_leave = np.array(counts_leave.values())
counts_other = np.array(counts_other.values())

"""
days = np.array(sorted(list(set(dates))))

print("Dates   : ", days)
print("==== Leave ====")
print("Counts : ", counts_leave)
print("\n")
print("==== Other ====")
print("Counts : ", counts_other)
print("\n")
print("==== Stay  ====")
print("Counts : ", counts_stay)
print("\n")

from matplotlib.dates import DayLocator, DateFormatter

# Plots
"""
#
# Total count leave / other / stay
#
fig = plt.figure(figsize=(15,8))
ax = plt.axes()
ax.set_title("Tweet count for leave / other / stay")
w = 0.2
ax.bar(days, counts_leave, width=w, color="r", label="leave")
ax.bar(days+w, counts_stay, width=w, color="b", label="stay")
ax.bar(days+2*w, counts_other, width=w, color="g", label="other")
ax.set_xlabel("Dates")
ax.set_ylabel("Tweet count")
ax.xaxis_date()
ax.autoscale(tight=True)
plt.legend(loc="best")
plt.savefig("total_daycount.pdf")
"""
from matplotlib.ticker import MultipleLocator

loc = MultipleLocator(base=1.0)
xfmt = DateFormatter('%d %b')

#
# Total count leave / stay
#
fig = plt.figure(figsize=(6,6))
ax = plt.axes()
ax.xaxis.set_major_formatter(xfmt)
ax.xaxis.set_major_locator(loc)
ax.set_title("Tweet count for leave / stay")
w = 0.2
y = np.array([counts_leave[day] for day in days])
ax.bar(days, y, width=w, color="r", label="leave")
y2 = np.array([counts_stay[day] for day in days])
ax.bar(days+w, y2, width=w, color="b", label="stay")
ax.set_xlabel("Dates")
ax.set_ylabel("Tweet count")
#ax.xaxis_date()
#ax.autoscale(tight=True)
#plt.legend(loc="best")
plt.savefig("total_daycount_ls.pdf")

#
# Relative count leave / other / stay
#

all_keys = set(())
dictionaries = [counts_leave, counts_stay, counts_other]

for dictionary in dictionaries:
    all_keys |= set(dictionary.keys())

for key in all_keys:
    for dictionary in dictionaries:
        if key not in dictionary:
            dictionary[key] = 0


counts_leave_vals = np.array([counts_leave[day] for day in days])
counts_stay_vals = np.array([counts_stay[day] for day in days])
counts_other_vals = np.array([counts_other[day] for day in days])
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
ax.bar(days, counts_leave_normalised, width=w, color="r", label="leave")
ax.bar(days, counts_stay_normalised, width=w, bottom=counts_leave_normalised, color="b", label="stay")
ax.bar(days, counts_other_normalised, width=w, bottom=1-counts_other_normalised, color="g", label="other")
ax.set_xlabel("Dates")
ax.set_ylabel("Tweet count")
#plt.legend(loc="best")
plt.savefig("relative_daycount.pdf")
"""
#
# Relative count leave / stay
#
tot = counts_leave + counts_stay
tot = np.max(np.vstack((tot, np.ones_like(tot))), axis=0)
counts_leave_normalised = 1.0*counts_leave/tot
counts_stay_normalised = 1.0*counts_stay/tot

fig = plt.figure(figsize=(15,8))
ax = plt.axes()
ax.set_title("Tweet count for leave / stay")
w = 0.8
ax.bar(days, counts_leave_normalised, width=w, color="r", label="leave")
ax.bar(days, counts_stay_normalised, width=w, bottom=counts_leave_normalised, color="b", label="stay")
ax.set_xlabel("Dates")
ax.set_ylabel("Tweet count")
ax.xaxis_date()
ax.autoscale(tight=True)
plt.legend(loc="best")
plt.savefig("relative_daycount_ls.pdf")
"""
