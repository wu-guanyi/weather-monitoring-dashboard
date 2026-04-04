from flask import Blueprint, request
from services.weather_service import (
    get_all_cities,
    get_latest_by_city,
    get_history_by_city,
    get_daily_stats_by_city,
    get_chart_data_by_city,
    get_station_latest_list,
    get_summary_stats_by_city
)
from utils.response import success_response, error_response
from utils.validators import validate_city, validate_limit

weather_api = Blueprint("weather_api", __name__, url_prefix="/api")


def get_allowed_cities():
    """取得可查詢城市清單"""
    return get_all_cities()


def validate_city_or_error(city):
    """驗證 city 是否合法，失敗則回傳錯誤 response"""
    allowed_cities = get_allowed_cities()
    valid, error_msg = validate_city(city, allowed_cities)
    if not valid:
        return False, error_response(message=error_msg, status=400)
    return True, None


def validate_limit_or_error(limit, default, max_limit):
    """驗證 limit 是否合法，失敗則回傳錯誤 response"""
    valid, error_msg, parsed_limit = validate_limit(limit, default=default, max_limit=max_limit)
    if not valid:
        return False, error_response(message=error_msg, status=400), None
    return True, None, parsed_limit


@weather_api.route("/cities", methods=["GET"])
def api_get_cities():
    """
    取得所有可查詢城市列表
    ---
    tags:
      - Weather API
    responses:
      200:
        description: 成功取得城市列表
        schema:
          type: object
          properties:
            status:
              type: string
              example: success
            message:
              type: string
              example: 取得城市列表成功
            data:
              type: array
              items:
                type: string
              example: ["台北", "台中", "高雄"]
      500:
        description: 伺服器錯誤
        schema:
          type: object
          properties:
            status:
              type: string
              example: error
            message:
              type: string
              example: 取得城市列表失敗
            data:
              nullable: true
              example: null
    """
    try:
        cities = get_allowed_cities()
        return success_response(data=cities, message="取得城市列表成功")
    except Exception as e:
        return error_response(message=f"取得城市列表失敗: {str(e)}", status=500)


@weather_api.route("/latest", methods=["GET"])
def api_get_latest():
    """
    取得指定城市最新天氣資料
    ---
    tags:
      - Weather API
    parameters:
      - name: city
        in: query
        type: string
        required: true
        description: 城市名稱，例如台北
        example: 台北
    responses:
      200:
        description: 成功取得最新資料
      400:
        description: 參數錯誤
      404:
        description: 查無資料
      500:
        description: 伺服器錯誤
    """
    try:
        city = request.args.get("city")

        valid, error_resp = validate_city_or_error(city)
        if not valid:
            return error_resp

        result = get_latest_by_city(city)
        if not result:
            return error_response(message=f"查無 {city} 最新資料", status=404)

        return success_response(data=result, message=f"{city} 最新資料取得成功")

    except Exception as e:
        return error_response(message=f"取得最新資料失敗: {str(e)}", status=500)


@weather_api.route("/history", methods=["GET"])
def api_get_history():
    """
    取得指定城市歷史天氣資料
    ---
    tags:
      - Weather API
    parameters:
      - name: city
        in: query
        type: string
        required: true
        description: 城市名稱
        example: 台北
      - name: limit
        in: query
        type: integer
        required: false
        description: 回傳筆數上限，預設 10，最大 100
        example: 10
    responses:
      200:
        description: 成功取得歷史資料
      400:
        description: 參數錯誤
      500:
        description: 伺服器錯誤
    """
    try:
        city = request.args.get("city")
        limit = request.args.get("limit", 10)

        valid, error_resp = validate_city_or_error(city)
        if not valid:
            return error_resp

        valid_limit, limit_error_resp, parsed_limit = validate_limit_or_error(limit, default=10, max_limit=100)
        if not valid_limit:
            return limit_error_resp

        result = get_history_by_city(city, limit=parsed_limit)
        return success_response(data=result, message=f"{city} 歷史資料取得成功")

    except Exception as e:
        return error_response(message=f"取得歷史資料失敗: {str(e)}", status=500)


@weather_api.route("/daily-stats", methods=["GET"])
def api_get_daily_stats():
    """
    取得指定城市每日統計資料
    ---
    tags:
      - Weather API
    parameters:
      - name: city
        in: query
        type: string
        required: true
        description: 城市名稱
        example: 台北
    responses:
      200:
        description: 成功取得每日統計資料
      400:
        description: 參數錯誤
      500:
        description: 伺服器錯誤
    """
    try:
        city = request.args.get("city")

        valid, error_resp = validate_city_or_error(city)
        if not valid:
            return error_resp

        result = get_daily_stats_by_city(city)
        return success_response(data=result, message=f"{city} 每日統計取得成功")

    except Exception as e:
        return error_response(message=f"取得每日統計失敗: {str(e)}", status=500)


@weather_api.route("/chart", methods=["GET"])
def api_get_chart():
    """
    取得指定城市圖表資料
    ---
    tags:
      - Weather API
    parameters:
      - name: city
        in: query
        type: string
        required: true
        description: 城市名稱
        example: 台北
      - name: limit
        in: query
        type: integer
        required: false
        description: 回傳圖表資料筆數，預設 50，最大 200
        example: 50
    responses:
      200:
        description: 成功取得圖表資料
      400:
        description: 參數錯誤
      500:
        description: 伺服器錯誤
    """
    try:
        city = request.args.get("city")
        limit = request.args.get("limit", 50)

        valid, error_resp = validate_city_or_error(city)
        if not valid:
            return error_resp

        valid_limit, limit_error_resp, parsed_limit = validate_limit_or_error(limit, default=50, max_limit=200)
        if not valid_limit:
            return limit_error_resp

        result = get_chart_data_by_city(city, limit=parsed_limit)
        return success_response(data=result, message=f"{city} 圖表資料取得成功")

    except Exception as e:
        return error_response(message=f"取得圖表資料失敗: {str(e)}", status=500)


@weather_api.route("/stations/latest", methods=["GET"])
def api_get_stations_latest():
    """
    取得所有測站最新資料
    ---
    tags:
      - Weather API
    responses:
      200:
        description: 成功取得各站最新資料
      500:
        description: 伺服器錯誤
    """
    try:
        result = get_station_latest_list()
        return success_response(data=result, message="各站最新資料取得成功")
    except Exception as e:
        return error_response(message=f"取得各站最新資料失敗: {str(e)}", status=500)


@weather_api.route("/summary", methods=["GET"])
def api_get_summary():
    """
    取得指定城市摘要統計資料
    ---
    tags:
      - Weather API
    parameters:
      - name: city
        in: query
        type: string
        required: true
        description: 城市名稱
        example: 台北
    responses:
      200:
        description: 成功取得摘要資料
      400:
        description: 參數錯誤
      404:
        description: 查無資料
      500:
        description: 伺服器錯誤
    """
    try:
        city = request.args.get("city")

        valid, error_resp = validate_city_or_error(city)
        if not valid:
            return error_resp

        result = get_summary_stats_by_city(city)
        if not result:
            return error_response(message=f"查無 {city} 摘要資料", status=404)

        return success_response(data=result, message=f"{city} 摘要資料取得成功")

    except Exception as e:
        return error_response(message=f"取得摘要資料失敗: {str(e)}", status=500)