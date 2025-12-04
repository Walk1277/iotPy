# visualization/daily_timeline.py
import matplotlib.pyplot as plt
import datetime

def show_daily_timeline(df):
    if df.empty:
        print("No data.")
        return

    today = datetime.datetime.now().date()
    df_today = df[df["Timestamp"].dt.date == today]

    if df_today.empty:
        print("No events today.")
        return

    event_map = {
        "drowsiness": 4,
        "sudden acceleration": 3,
        "sudden stop": 2,
        "Start program": 1.5,
        "program quit": 1
    }

    df_today["Y"] = df_today["EventType"].map(event_map)
    plt.figure(figsize=(12, 6))
    colors = {4: "red", 3: "orange", 2: "blue", 1.5: "cyan", 1: "green"}

    for event, y in event_map.items():
        sub = df_today[df_today["EventType"] == event]
        if len(sub) > 0:
            plt.scatter(sub["Timestamp"], [y]*len(sub), s=100, color=colors[y], label=event)

    plt.legend()
    plt.title("Daily Timeline")
    plt.show()

