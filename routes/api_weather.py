from flask import Blueprint, jsonify, request
from services.weather_service import (
    get_all_cities,
    get_latest_by_city,
    get_history_by_city,
    get_summary_stats_by_city,
    get_station_latest_list
)

api_weather_bp = Blueprint("api_weather", __name__, url_prefix="/api/weather")


@api_weather_bp.route("/cities", methods=["GET"])
def get_cities():
    cities = get_all_cities()

    return jsonify({
        "status": "success",
        "data": cities
    })


@api_weather_bp.route("/latest/<city>", methods=["GET"])
def get_latest_city(city):
    data = get_latest_by_city(city)

    if not data:
        return jsonify({
            "status": "error",
            "message": f"找不到城市：{city}"
        }), 404

    return jsonify({
        "status": "success",
        "data": data
    })


@api_weather_bp.route("/history/<city>", methods=["GET"])
def get_history_city(city):
    limit = request.args.get("limit", default=50, type=int)
    data = get_history_by_city(city, limit=limit)

    if not data:
        return jsonify({
            "status": "error",
            "message": f"找不到城市資料：{city}"
        }), 404

    return jsonify({
        "status": "success",
        "count": len(data),
        "data": data
    })


@api_weather_bp.route("/stats/<city>", methods=["GET"])
def get_stats_city(city):
    days = request.args.get("days", default=7, type=int)
    data = get_summary_stats_by_city(city, days=days)

    if not data:
        return jsonify({
            "status": "error",
            "message": f"找不到城市統計資料：{city}"
        }), 404

    return jsonify({
        "status": "success",
        "data": data
    })


@api_weather_bp.route("/stations/latest", methods=["GET"])
def get_stations_latest():
    data = get_station_latest_list()

    return jsonify({
        "status": "success",
        "count": len(data),
        "data": data
    })