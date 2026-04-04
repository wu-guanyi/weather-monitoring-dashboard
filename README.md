<<<<<<< HEAD
API Endpoints
1. 取得城市列表
GET /api/cities
2. 取得指定城市最新資料
GET /api/latest?city=台北
3. 取得指定城市歷史資料
GET /api/history?city=台北&limit=10
4. 取得指定城市每日統計
GET /api/daily-stats?city=台北
5. 取得指定城市圖表資料
GET /api/chart?city=台北&limit=50
6. 取得所有站點最新資料
GET /api/stations/latest
7. 取得指定城市摘要資料
GET /api/summary?city=台北
=======
# 🌦 Weather Monitoring Dashboard

A Flask-based weather monitoring system that collects real-time temperature and humidity data from multiple regions in Taiwan.

## 🚀 Features
- Real-time weather data collection (every 10 minutes)
- Monitoring of 10 regions across Taiwan
- Temperature & humidity visualization using Chart.js
- Daily statistical analysis (avg, max, min)
- Missing data handling (-99 filtering & forward fill)

## 🛠 Tech Stack
- Python (Flask)
- PostgreSQL
- Pandas
- Chart.js
- Taiwan CWA Open Data API

## 📊 System Architecture
1. Fetch weather data via API
2. Store data in PostgreSQL
3. Process data with Pandas (cleaning & filling missing values)
4. Visualize data in dashboard

## 📦 Installation
```bash
pip install -r requirements.txt
python app.py
```



📷 Demo
Dashboard Overview
<img width="1088" height="910" alt="image" src="https://github.com/user-attachments/assets/6100b412-5cf4-47f5-829b-783f6fd69125" />

Station Detail

<img width="1056" height="851" alt="image" src="https://github.com/user-attachments/assets/0050474c-4862-4966-b640-da373b2edad9" />


<img width="1170" height="898" alt="image" src="https://github.com/user-attachments/assets/509d24fd-b579-41b5-aed1-69f27c2da242" />
>>>>>>> 17a4bb9b49e975e76c868bd3ba325d88011108b4
