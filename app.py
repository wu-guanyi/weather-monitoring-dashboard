from flask import Flask, render_template, request
from flasgger import Swagger
from services.weather_service import (
    get_all_cities,
    get_latest_by_city,
    get_history_by_city,
    get_daily_stats_by_city,
    get_chart_data_by_city,
    get_station_latest_list
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


@app.route("/stations")
def stations_page():
    try:
        station_latest = get_station_latest_list()
    except Exception as e:
        print(f"stations_page 發生錯誤: {e}")
        station_latest = []

    return render_template("stations.html", station_latest=station_latest)


@app.route("/station/<station_name>")
def station_detail(station_name):
    try:
        latest = get_latest_by_city(station_name)
        history = get_history_by_city(station_name, limit=10)
        daily_stats = get_daily_stats_by_city(station_name)
        chart_data = get_chart_data_by_city(station_name, limit=50)
    except Exception as e:
        print(f"station_detail 發生錯誤: {e}")
        latest = None
        history = []
        daily_stats = []
        chart_data = []

    return render_template(
        "station_detail.html",
        station_name=station_name,
        latest=latest,
        history=history,
        daily_stats=daily_stats,
        chart_data=chart_data
    )


if __name__ == "__main__":
    app.run(debug=True)