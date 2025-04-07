from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import matplotlib.pyplot as plt
import io
import json
from datetime import datetime, timedelta

router = APIRouter()

def load_json(path, default):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except:
        return default

@router.get("/stats/checklist")
def checklist_progress():
    data = load_json("data/checklist.json", [])
    date_count = {}
    for item in data:
        date = item.get("date", datetime.today().strftime("%Y-%m-%d"))
        date_count[date] = date_count.get(date, 0) + 1

    dates = sorted(date_count.keys())[-7:]
    values = [date_count[d] for d in dates]

    fig, ax = plt.subplots()
    ax.bar(dates, values)
    ax.set_title("📋 Задачи по дням")
    plt.xticks(rotation=45)
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return StreamingResponse(buf, media_type="image/png")

@router.get("/stats/goals")
def goals_progress():
    data = load_json("data/goals.json", [])
    goal_counter = {}
    for goal in data:
        goal_counter[goal] = goal_counter.get(goal, 0) + 1

    goals = list(goal_counter.keys())
    counts = list(goal_counter.values())

    fig, ax = plt.subplots()
    ax.pie(counts, labels=goals, autopct='%1.1f%%')
    ax.set_title("🎯 Цели")
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()
    return StreamingResponse(buf, media_type="image/png")
