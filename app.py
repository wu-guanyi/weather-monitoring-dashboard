from flask import Flask, render_template
from flask import request
from psycopg2.extras import RealDictCursor
from db import get_connection
from datetime import datetime
import pandas as pd
app = Flask(__name__)


@app.route("/")
def index():
    latest = None
    history = []
    chart_data = []
    daily_stats = []
    selected_city = request.args.get("city", "台北")

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 最近 50 筆資料
        cur.execute("""
            SELECT recorded_at, temperature_celsius, humidity
            FROM (
                SELECT recorded_at, temperature_celsius, humidity
                FROM weather_data
                WHERE location_name = %s
                ORDER BY recorded_at DESC
                LIMIT 50
            ) t
            ORDER BY recorded_at ASC
        """, (selected_city,))
        chart_rows = cur.fetchall()
        # 最新一筆資料
        cur.execute("""
            SELECT location_name, recorded_at, temperature_celsius, humidity, data_source
            FROM weather_data
            WHERE location_name = %s
            ORDER BY recorded_at DESC
            LIMIT 1
        """, (selected_city,))
        latest_row = cur.fetchone()

        # 最近 10 筆資料
        cur.execute("""
            SELECT location_name, recorded_at, temperature_celsius, humidity, data_source
            FROM weather_data
            WHERE location_name = %s
            ORDER BY recorded_at DESC
            LIMIT 10
        """, (selected_city,))
        history_rows = cur.fetchall()

        # 每日統計
        cur.execute("""
            SELECT
                DATE(recorded_at) AS stat_date,
                ROUND(AVG(NULLIF(temperature_celsius, -99))::numeric, 2) AS avg_temp,
                ROUND(MAX(NULLIF(temperature_celsius, -99))::numeric, 2) AS max_temp,
                ROUND(MIN(NULLIF(temperature_celsius, -99))::numeric, 2) AS min_temp,
                ROUND(AVG(NULLIF(humidity, -99))::numeric, 2) AS avg_humidity,
                ROUND(MAX(NULLIF(humidity, -99))::numeric, 2) AS max_humidity,
                ROUND(MIN(NULLIF(humidity, -99))::numeric, 2) AS min_humidity,

                COUNT(*) AS total_count,  -- 總筆數
                COUNT(NULLIF(temperature_celsius, -99)) AS valid_temp_count,
                COUNT(NULLIF(humidity, -99)) AS valid_humidity_count

            FROM weather_data
            WHERE location_name = %s
            GROUP BY DATE(recorded_at)
            ORDER BY stat_date DESC
        """, (selected_city,))
        daily_rows = cur.fetchall()

        if latest_row:
            recorded_time = latest_row[1]
            now = datetime.now(recorded_time.tzinfo) if recorded_time.tzinfo else datetime.now()
            delay = int((now - recorded_time).total_seconds() // 60)

            latest = {
                "location_name": latest_row[0],
                "recorded_at": recorded_time.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_celsius": latest_row[2],
                "humidity": latest_row[3],
                "data_source": latest_row[4],
                "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "delay_minutes": delay
            }

            # 補值
            df = pd.DataFrame(chart_rows, columns=['recorded_at', 'temperature', 'humidity'])

            df['temperature'] = pd.to_numeric(df['temperature'], errors='coerce')
            df['humidity'] = pd.to_numeric(df['humidity'], errors='coerce')

            # 把 -99 當成缺值
            df['temperature'] = df['temperature'].ffill().bfill()
            df['humidity'] = df['humidity'].ffill().bfill()

            # 用前一筆補
            df['temperature'] = df['temperature'].ffill()
            df['humidity'] = df['humidity'].ffill()

            chart_data = []
            for _, row in df.iterrows():
                temp_val = None if pd.isna(row['temperature']) else float(row['temperature'])
                humidity_val = None if pd.isna(row['humidity']) else float(row['humidity'])

                chart_data.append({
                    "recorded_at": row['recorded_at'].strftime("%Y-%m-%d %H:%M:%S"),
                    "temperature_celsius": temp_val,
                    "humidity": humidity_val
                })

        for row in history_rows:
            history.append({
                "location_name": row[0],
                "recorded_at": row[1].strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_celsius": row[2],
                "humidity": row[3],
                "data_source": row[4]
            })

        for row in daily_rows:
            daily_stats.append({
                "stat_date": row[0].strftime("%Y-%m-%d"),
                "avg_temp": row[1],
                "max_temp": row[2],
                "min_temp": row[3],
                "avg_humidity": row[4],
                "max_humidity": row[5],
                "min_humidity": row[6],
                "record_count": row[7],
                "valid_temp_count": row[8],
                "valid_humidity_count": row[9]
            })
        daily_chart_labels = []
        daily_avg_temps = []

        for row in daily_rows[::-1]:  # 反轉，讓日期由舊到新
            daily_chart_labels.append(row[0].strftime("%Y-%m-%d"))
            daily_avg_temps.append(float(row[1]))
        cur.close()
        conn.close()

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


@app.route("/stations")
def stations():
    station_latest = []

    try:
        conn = get_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        cur.execute("""
            SELECT DISTINCT ON (location_name)
                location_name,
                recorded_at,
                temperature_celsius,
                humidity,
                data_source
            FROM weather_data
            ORDER BY location_name, recorded_at DESC
        """)
        rows = cur.fetchall()

        for row in rows:
            recorded_time = row["recorded_at"]
            now = datetime.now(recorded_time.tzinfo) if recorded_time.tzinfo else datetime.now()
            delay = int((now - recorded_time).total_seconds() // 60)

            station_latest.append({
                "location_name": row["location_name"],
                "recorded_at": recorded_time.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_celsius": row["temperature_celsius"],
                "humidity": row["humidity"],
                "data_source": row["data_source"],
                "delay_minutes": delay
            })

        # 依溫度高到低排序
        station_latest.sort(key=lambda x: x["temperature_celsius"], reverse=True)

        cur.close()
        conn.close()

    except Exception as e:
        print("stations 發生錯誤：", e)

    return render_template("stations.html", station_latest=station_latest)


@app.route("/station/<station_name>")
def station_detail(station_name):
    latest = None
    history = []
    chart_data = []
    daily_stats = []

    try:
        conn = get_connection()
        cur = conn.cursor()

        # 最近 50 筆資料，該站
        cur.execute("""
            SELECT recorded_at, temperature_celsius, humidity
            FROM (
                SELECT recorded_at, temperature_celsius, humidity
                FROM weather_data
                WHERE location_name = %s
                ORDER BY recorded_at DESC
                LIMIT 50
            ) t
            ORDER BY recorded_at ASC
        """, (station_name,))
        chart_rows = cur.fetchall()

        # 最新一筆資料，該站
        cur.execute("""
            SELECT location_name, recorded_at, temperature_celsius, humidity, data_source
            FROM weather_data
            WHERE location_name = %s
            ORDER BY recorded_at DESC
            LIMIT 1
        """, (station_name,))
        latest_row = cur.fetchone()

        # 最近 10 筆資料，該站
        cur.execute("""
            SELECT location_name, recorded_at, temperature_celsius, humidity, data_source
            FROM weather_data
            WHERE location_name = %s
            ORDER BY recorded_at DESC
            LIMIT 10
        """, (station_name,))
        history_rows = cur.fetchall()

        # 每日統計，該站
        # 每日統計，該站
        cur.execute("""
            SELECT
                DATE(recorded_at) AS stat_date,
                ROUND(AVG(NULLIF(temperature_celsius, -99))::numeric, 2) AS avg_temp,
                ROUND(MAX(NULLIF(temperature_celsius, -99))::numeric, 2) AS max_temp,
                ROUND(MIN(NULLIF(temperature_celsius, -99))::numeric, 2) AS min_temp,
                ROUND(AVG(NULLIF(humidity, -99))::numeric, 2) AS avg_humidity,
                ROUND(MAX(NULLIF(humidity, -99))::numeric, 2) AS max_humidity,
                ROUND(MIN(NULLIF(humidity, -99))::numeric, 2) AS min_humidity,
                COUNT(*) AS total_count,
                COUNT(NULLIF(temperature_celsius, -99)) AS valid_temp_count,
                COUNT(NULLIF(humidity, -99)) AS valid_humidity_count
            FROM weather_data
            WHERE location_name = %s
            GROUP BY DATE(recorded_at)
            ORDER BY stat_date DESC
        """, (station_name,))
        daily_rows = cur.fetchall()

        if latest_row:
            recorded_time = latest_row[1]
            now = datetime.now(recorded_time.tzinfo) if recorded_time.tzinfo else datetime.now()
            delay = int((now - recorded_time).total_seconds() // 60)

            latest = {
                "location_name": latest_row[0],
                "recorded_at": recorded_time.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_celsius": latest_row[2],
                "humidity": latest_row[3],
                "data_source": latest_row[4],
                "updated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
                "delay_minutes": delay
            }

        for row in chart_rows:
            chart_data.append({
                "recorded_at": row[0].strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_celsius": row[1],
                "humidity": row[2]
            })

        for row in history_rows:
            history.append({
                "location_name": row[0],
                "recorded_at": row[1].strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_celsius": row[2],
                "humidity": row[3],
                "data_source": row[4]
            })

        for row in daily_rows:
            daily_stats.append({
                "stat_date": row[0].strftime("%Y-%m-%d"),
                "avg_temp": row[1],
                "max_temp": row[2],
                "min_temp": row[3],
                "avg_humidity": row[4],
                "max_humidity": row[5],
                "min_humidity": row[6],
                "total_count": row[7],
                "valid_temp_count": row[8],
                "valid_humidity_count": row[9]
            })

        cur.close()
        conn.close()

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


if __name__ == "__main__":
    app.run(debug=False)