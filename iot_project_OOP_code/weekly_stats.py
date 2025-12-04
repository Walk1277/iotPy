# visualization/weekly_stats.py
import matplotlib.pyplot as plt
import numpy as np
import datetime

def show_weekly_stats(df):
    if df.empty:
        print("No weekly data.")
        return

    key = ["drowsiness", "sudden acceleration", "sudden stop"]
    df_key = df[df["EventType"].isin(key)]

    df_key["Date"] = df_key["Timestamp"].dt.date
    week = df_key.groupby(["Date", "EventType"]).size().unstack(fill_value=0)

    today = datetime.date.today()
    days = list((today - datetime.timedelta(days=i)) for i in range(6, -1, -1))
    days = list(reversed(days))

    week = week.reindex(days, fill_value=0)
    labels = [d.strftime("%m/%d") for d in days]

    plt.figure(figsize=(12,6))
    x = np.arange(7)
    w = 0.25

    plt.bar(x - w, week["drowsiness"], width=w, label="drowsiness", color="red")
    plt.bar(x,     week["sudden acceleration"], width=w, label="accel", color="orange")
    plt.bar(x + w, week["sudden stop"], width=w, label="stop", color="blue")

    plt.xticks(x, labels)
    plt.legend()
    plt.show()

