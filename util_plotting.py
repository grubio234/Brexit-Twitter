import matplotlib.pyplot as plt
from matplotlib.dates import date2num, DateFormatter

def dailySentimentPlots(daily_sent, save_path="./"):
    def plotTemplate():
        xfmt = DateFormatter('%d %b')
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(1, 1, 1)
        ax.xaxis.set_major_formatter(xfmt)
        ax.set_xlabel("Dates")
        ax.set_ylabel("Tweet count")

        return fig, ax

    num_days = date2num(daily_sent.index)

    fig, ax = plotTemplate()
    w = 0.2
    ax.bar(num_days,   daily_sent["leave"], width=w, color="r", label="leave")
    ax.bar(num_days+w, daily_sent["stay"],  width=w, color="b", label="stay")
    ax.set_title("Tweet count for leave / stay")
    fig.savefig(save_path+"total_daycount_ls.pdf")

    daily_rel = daily_sent.copy()
    daily_rel["total"] = daily_rel.sum(axis=1)
    daily_rel["total"] = daily_rel["total"].replace(0, 1).astype(float)
    daily_rel = daily_rel.div(daily_rel["total"], axis=0)

    fig, ax = plotTemplate()
    w = 0.6
    ax.bar(num_days, daily_rel["leave"],     label="leave", width=w, color="r")
    ax.bar(num_days, daily_rel["stay"],      label="stay",  width=w, color="b",
            bottom=daily_rel["leave"])
    ax.bar(num_days, daily_rel["undecided"], label="other", width=w, color="g",
            bottom=1-daily_rel["undecided"])
    ax.set_title("Tweet count for leave / other / stay")
    fig.savefig(save_path+"relative_daycount.pdf")

def keywordFrequencyPlot(df, title, save_as, colors, mode=None):
    def emptyDataFramePlot(title, save_as):
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(1, 1, 1)
        plt.xticks([])
        plt.yticks([])
        ax.set_title(title)
        fig.text(0.5, 0.5, "Empty DataFrame", ha='center', va='center', size=24, alpha=.5)
        fig.savefig(save_as)
    if df.empty:
        emptyDataFramePlot(title, save_as)
    else:
        fig = plt.figure(figsize=(6,6))
        ax = fig.add_subplot(1, 1, 1)
        ax.set_title(title)
        daily_width = 0.8
        xfmt = DateFormatter('%d %b')
        ax.xaxis.set_major_formatter(xfmt)
        ax.set_xlabel("Date")
        ax.set_ylabel("Tweet count")
        N = len(df.columns)

        y_bottom = None
        days = date2num(df.index)
        for i, col in enumerate(df.columns):
            if mode == "stacked":
                ax.bar(days, df[col], bottom=y_bottom, width=daily_width, color=colors[i], label=col)
                y_bottom = y_bottom + df[col] if y_bottom is not None else df[col]
            else:
                bar_width = daily_width/N
                xk = days + bar_width*(i - N/2 - 1)
                ax.bar(xk, df[col], width=bar_width, color=colors[i], label=col)
        ax.legend(loc="best")
        fig.savefig(save_as)