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
