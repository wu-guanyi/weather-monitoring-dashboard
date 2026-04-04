from flask import Blueprint, render_template, request
from services.weather_service import (
    get_latest_by_city,
    get_history_by_city,
    get_daily_stats_by_city,
    get_chart_data_by_city,
    get_station_latest_list
)

web_bp = Blueprint("web", __name__)


@web_bp.route("/")
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
            daily_avg_temps.append(float(row["avg_temp"]) if row["avg_temp"] is not None else None)

    except Exception as e:
        print("index 發生錯誤：", e)

    return render_template(
        "index.html",
        latest=latest,
        history=history,
        chart_data=chart_data,
        daily_stats=daily_stats,
        selected_city=selected_city,
        daily_chart_labels=daily_chart_labels,
        daily_avg_temps=daily_avg_temps,
    )


@web_bp.route("/stations")
def stations():
    station_latest = []

    try:
        station_latest = get_station_latest_list()
    except Exception as e:
        print("stations 發生錯誤：", e)

    return render_template("stations.html", station_latest=station_latest)


@web_bp.route("/station/<station_name>")
def station_detail(station_name):
    latest = None
    history = []
    chart_data = []
    daily_stats = []

    try:
        latest = get_latest_by_city(station_name)
        history = get_history_by_city(station_name, limit=10)
        chart_data = get_chart_data_by_city(station_name, limit=50)
        daily_stats = get_daily_stats_by_city(station_name)

    except Exception as e:
        print("station_detail 發生錯誤：", e)

    return render_template(
        "station_detail.html",
        station_name=station_name,
        latest=latest,
        history=history,
        chart_data=chart_data,
        daily_stats=daily_stats
    )