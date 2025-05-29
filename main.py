from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import httpx
import os
import json
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

app = FastAPI()

# Загрузка списка городов при старте
with open("city_list.json", encoding="utf-8") as f:
    all_cities = json.load(f)

# Статика и шаблоны
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def form_get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def form_post(request: Request, city: str = Form(...)):
    forecast_data = []
    error = None

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(BASE_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            seen_dates = set()

            for item in data["list"]:
                dt_txt = item["dt_txt"]  # формат: "2025-05-28 12:00:00"
                if "12:00:00" in dt_txt:
                    date = dt_txt.split()[0]
                    if date not in seen_dates:
                        seen_dates.add(date)
                        forecast_data.append({
                            "дата": date,
                            "температура": f"{item['main']['temp']} °C",
                            "погода": item["weather"][0]["description"],
                            "ветер": f"{item['wind']['speed']} м/с"
                        })
        else:
            error = response.json().get("message", "Ошибка получения данных")

    return templates.TemplateResponse("index.html", {
        "request": request,
        "forecast": forecast_data,
        "error": error,
        "city": city
    })

@app.get("/autocomplete")
async def autocomplete(q: str):
    q_lower = q.lower()
    matches = [
        {"name": city["name"], "country": city["country"]}
        for city in all_cities
        if city["name"].lower().startswith(q_lower)
    ]
    return JSONResponse(matches[:10])  # максимум 10 подсказок


