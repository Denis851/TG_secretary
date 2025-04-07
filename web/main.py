# FastAPI сервер с редактором расписания и графиками
from fastapi import Form
from typing import List

@app.get("/schedule", response_class=HTMLResponse)
def edit_schedule(request: Request, day: str = "Пн"):
    schedule = load_json("schedule", {})
    return templates.TemplateResponse("schedule.html", {
        "request": request,
        "selected_day": day,
        "days": list(schedule.keys()),
        "blocks": schedule.get(day, [])
    })

@app.post("/schedule")
def save_schedule(day: str = Form(...), time_0: str = Form(...), task_0: str = Form(...),
                  request: Request = None, **form_data):
    schedule = load_json("schedule", {})
    blocks = []
    i = 0
    while True:
        t_key = f"time_{i}"
        d_key = f"task_{i}"
        if t_key in form_data and d_key in form_data:
            blocks.append({"time": form_data[t_key], "task": form_data[d_key]})
            i += 1
        else:
            break
    schedule[day] = blocks
    save_json("schedule", schedule)
    return RedirectResponse(f"/schedule?day={day}", status_code=302)

@app.post("/schedule/add")
def add_block(day: str = Form(...)):
    schedule = load_json("schedule", {})
    schedule.setdefault(day, []).append({"time": "", "task": ""})
    save_json("schedule", schedule)
    return RedirectResponse(f"/schedule?day={day}", status_code=302)

from web import stats
app.include_router(stats.router)
