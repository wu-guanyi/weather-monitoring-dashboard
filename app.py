from flask import Flask, render_template, request
from flasgger import Swagger
from services.weather_service import (
    get_all_cities,
    get_latest_by_city,
    get_history_by_city,
    get_daily_stats_by_city,
    get_chart_data_by_city
)
from routes.weather_api import weather_api

app = Flask(__name__)

app.config["SWAGGER"] = {
    "title": "Weather Monitoring Dashboard API",
    "uiversion": 3,
    "version": "1.0.0",
    "description": "即時天氣監測系統 API 文件"
}

swagger = Swagger(app)

app.register_blueprint(weather_api)


@app.route("/")
def index():
    latest = None
    history = []
    chart_data = []
    daily_stats = []
    selected_city = request.args.get("city", "台北")
    daily_chart_labels = []
    daily_avg_temps = []

    try:
        latest = get_latest_by_city(selected_city)
        history = get_history_by_city(selected_city, limit=10)
        chart_data = get_chart_data_by_city(selected_city, limit=50)
        daily_stats = get_daily_stats_by_city(selected_city)

        for row in reversed(daily_stats):
            daily_chart_labels.append(row["stat_date"])
            daily_avg_temps.append(
                float(row["avg_temp"]) if row["avg_temp"] is not None else None
            )

    except Exception as e:
        print(f"index 發生錯誤: {e}")

    cities = get_all_cities()

    return render_template(
        "index.html",
        latest=latest,
        history=history,
        chart_data=chart_data,
        daily_stats=daily_stats,
        selected_city=selected_city,
        cities=cities,
        daily_chart_labels=daily_chart_labels,
        daily_avg_temps=daily_avg_temps
    )


if __name__ == "__main__":
    app.run(debug=True)