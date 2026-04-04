from datetime import datetime
import pandas as pd
from db import get_connection


def format_datetime(dt):
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def calculate_delay_minutes(recorded_time):
    if recorded_time is None:
        return None

    now = datetime.now(recorded_time.tzinfo) if recorded_time.tzinfo else datetime.now()
    return int((now - recorded_time).total_seconds() // 60)


def get_all_cities():
    conn = None
    cur = None
    try:
        conn = get_connection(dict_cursor=True)
        cur = conn.cursor()

        cur.execute("""
            SELECT DISTINCT location_name
            FROM weather_data
            ORDER BY location_name
        """)
        rows = cur.fetchall()

        return [row["location_name"] for row in rows]

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_latest_by_city(city):
    conn = None
    cur = None
    try:
        conn = get_connection(dict_cursor=True)
        cur = conn.cursor()

        cur.execute("""
            SELECT location_name, recorded_at, temperature_celsius, humidity, data_source
            FROM weather_data
            WHERE location_name = %s
            ORDER BY recorded_at DESC
            LIMIT 1
        """, (city,))
        row = cur.fetchone()

        if not row:
            return None

        return {
            "location_name": row["location_name"],
            "recorded_at": format_datetime(row["recorded_at"]),
            "temperature_celsius": row["temperature_celsius"],
            "humidity": row["humidity"],
            "data_source": row["data_source"],
            "delay_minutes": calculate_delay_minutes(row["recorded_at"])
        }

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_history_by_city(city, limit=50):
    conn = None
    cur = None
    try:
        conn = get_connection(dict_cursor=True)
        cur = conn.cursor()

        cur.execute("""
            SELECT location_name, recorded_at, temperature_celsius, humidity, data_source
            FROM weather_data
            WHERE location_name = %s
            ORDER BY recorded_at DESC
            LIMIT %s
        """, (city, limit))
        rows = cur.fetchall()

        result = []
        for row in reversed(rows):  # 由舊到新
            result.append({
                "location_name": row["location_name"],
                "recorded_at": format_datetime(row["recorded_at"]),
                "temperature_celsius": row["temperature_celsius"],
                "humidity": row["humidity"],
                "data_source": row["data_source"]
            })

        return result

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_daily_stats_by_city(city):
    conn = None
    cur = None
    try:
        conn = get_connection(dict_cursor=True)
        cur = conn.cursor()

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
        """, (city,))
        rows = cur.fetchall()

        result = []
        for row in rows:
            result.append({
                "stat_date": row["stat_date"].strftime("%Y-%m-%d"),
                "avg_temp": row["avg_temp"],
                "max_temp": row["max_temp"],
                "min_temp": row["min_temp"],
                "avg_humidity": row["avg_humidity"],
                "max_humidity": row["max_humidity"],
                "min_humidity": row["min_humidity"],
                "total_count": row["total_count"],
                "valid_temp_count": row["valid_temp_count"],
                "valid_humidity_count": row["valid_humidity_count"]
            })

        return result

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_chart_data_by_city(city, limit=50):
    conn = None
    cur = None
    try:
        conn = get_connection(dict_cursor=True)
        cur = conn.cursor()

        cur.execute("""
            SELECT recorded_at, temperature_celsius, humidity
            FROM (
                SELECT recorded_at, temperature_celsius, humidity
                FROM weather_data
                WHERE location_name = %s
                ORDER BY recorded_at DESC
                LIMIT %s
            ) t
            ORDER BY recorded_at ASC
        """, (city, limit))
        rows = cur.fetchall()

        if not rows:
            return []

        df = pd.DataFrame(rows)
        df["temperature_celsius"] = pd.to_numeric(df["temperature_celsius"], errors="coerce")
        df["humidity"] = pd.to_numeric(df["humidity"], errors="coerce")

        # 把 -99 當成缺值
        df["temperature_celsius"] = df["temperature_celsius"].replace(-99, pd.NA)
        df["humidity"] = df["humidity"].replace(-99, pd.NA)

        # 補值
        df["temperature_celsius"] = df["temperature_celsius"].ffill().bfill()
        df["humidity"] = df["humidity"].ffill().bfill()

        result = []
        for _, row in df.iterrows():
            result.append({
                "recorded_at": row["recorded_at"].strftime("%Y-%m-%d %H:%M:%S"),
                "temperature_celsius": None if pd.isna(row["temperature_celsius"]) else float(row["temperature_celsius"]),
                "humidity": None if pd.isna(row["humidity"]) else float(row["humidity"])
            })

        return result

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_station_latest_list():
    conn = None
    cur = None
    try:
        conn = get_connection(dict_cursor=True)
        cur = conn.cursor()

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

        result = []
        for row in rows:
            result.append({
                "location_name": row["location_name"],
                "recorded_at": format_datetime(row["recorded_at"]),
                "temperature_celsius": row["temperature_celsius"],
                "humidity": row["humidity"],
                "data_source": row["data_source"],
                "delay_minutes": calculate_delay_minutes(row["recorded_at"])
            })

        result.sort(
            key=lambda x: x["temperature_celsius"] if x["temperature_celsius"] is not None else -999,
            reverse=True
        )

        return result

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


def get_summary_stats_by_city(city, days=7):
    conn = None
    cur = None
    try:
        conn = get_connection(dict_cursor=True)
        cur = conn.cursor()

        cur.execute("""
            SELECT
                location_name,
                ROUND(AVG(NULLIF(temperature_celsius, -99))::numeric, 2) AS avg_temp,
                ROUND(MAX(NULLIF(temperature_celsius, -99))::numeric, 2) AS max_temp,
                ROUND(MIN(NULLIF(temperature_celsius, -99))::numeric, 2) AS min_temp,
                ROUND(AVG(NULLIF(humidity, -99))::numeric, 2) AS avg_humidity,
                COUNT(*) AS total_records
            FROM weather_data
            WHERE location_name = %s
              AND recorded_at >= NOW() - (%s * INTERVAL '1 day')
            GROUP BY location_name
        """, (city, days))
        row = cur.fetchone()

        if not row:
            return None

        return {
            "location_name": row["location_name"],
            "avg_temp": row["avg_temp"],
            "max_temp": row["max_temp"],
            "min_temp": row["min_temp"],
            "avg_humidity": row["avg_humidity"],
            "total_records": row["total_records"]
        }

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()