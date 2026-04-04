
from datetime import datetime
import gc
import requests
import pandas as pd
from db import get_connection

def fetch_weather_data(session, api_url):
    try:
        response = session.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()

        stations = data["records"]["Station"]
        rows = []

        for station in stations:
            station_name = station.get("StationName")
            station_id = station.get("StationId")
            obs_time = station.get("ObsTime", {}).get("DateTime")

            weather_elements = station.get("WeatherElement", {})
            air_temp = weather_elements.get("AirTemperature")
            relative_humidity = weather_elements.get("RelativeHumidity")

            rows.append({
                "station": station_name,
                "station_id": station_id,
                "datetime": obs_time,
                "temp": air_temp,
                "humidity": relative_humidity
            })

        return pd.DataFrame(rows)

    except Exception as e:
        print("fetch_weather_data 發生錯誤：", e)
        return pd.DataFrame()


def clean_and_filter_stations(df_raw, target_stations):
    try:
        if df_raw is None or df_raw.empty:
            return pd.DataFrame()

        df = df_raw.copy()

        target_station_ids = list(target_stations.values())
        id_to_name = {v: k for k, v in target_stations.items()}

        df = df[df["station_id"].isin(target_station_ids)].copy()

        if df.empty:
            return pd.DataFrame()

        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df["temp"] = pd.to_numeric(df["temp"], errors="coerce")
        df["humidity"] = pd.to_numeric(df["humidity"], errors="coerce")

        df = df.dropna(subset=["station", "station_id", "datetime", "temp", "humidity"])

        # 用你指定的名稱覆蓋站名，避免 API 名稱不一致
        df["station"] = df["station_id"].map(id_to_name)

        return df.reset_index(drop=True)

    except Exception as e:
        print("clean_and_filter_stations 發生錯誤：", e)
        return pd.DataFrame()


def insert_into_postgresql(df):
    if df is None or df.empty:
        print("沒有可寫入的資料")
        return

    conn = None
    cur = None

    try:
        conn = get_connection()
        cur = conn.cursor()

        for _, row in df.iterrows():
            cur.execute("""
                INSERT INTO weather_data
                (station_id, location_name, recorded_at, temperature_celsius, humidity, data_source, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
                ON CONFLICT (station_id, recorded_at)
                DO NOTHING
            """, (
                row["station_id"],
                row["station"],
                row["datetime"].to_pydatetime(),
                float(row["temp"]),
                float(row["humidity"]),
                "cwa_station_api"
            ))

        conn.commit()
        print("寫入完成")

    except Exception as e:
        if conn:
            conn.rollback()
        print("insert_into_postgresql 發生錯誤：", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


API_URL = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization=rdec-key-123-45678-011121314"
#"https://opendata.cwa.gov.tw/api/v1/rest/datastore/O-A0003-001?Authorization=rdec-key-123-45678-011121314"
target_stations = {
    "基隆": "466940",
    "台中": "467490",
    "台南": "467410",
    "高雄": "467441",
    "宜蘭": "467080",
    "花蓮": "466990",
    "台東": "467660",
    "台北": "466920",
    "屏東": "C2R170",
    "桃園": "C2C480"
}

def main():
    print("=" * 60)
    print("開始抓取時間：", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    session = requests.Session()

    try:
        df_raw = fetch_weather_data(session, API_URL)
        df_selected = clean_and_filter_stations(df_raw, target_stations)

        if not df_selected.empty:
            print(df_selected[["station", "station_id", "datetime", "temp", "humidity"]])
            print("共取得站點數：", df_selected["station"].nunique())
            print("API回傳時間：", df_selected["datetime"].iloc[0])
            insert_into_postgresql(df_selected)
        else:
            print("本次未取得目標站點資料")
        
    except Exception as e:
        print("發生錯誤：", e)

    finally:
        session.close()
        gc.collect()


if __name__ == "__main__":
    print("氣象資料抓取程式啟動中...")
    main()