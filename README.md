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




📷 Demo
Dashboard Overview
<img width="1088" height="910" alt="image" src="https://github.com/user-attachments/assets/6100b412-5cf4-47f5-829b-783f6fd69125" />

Station Detail

<img width="1056" height="851" alt="image" src="https://github.com/user-attachments/assets/0050474c-4862-4966-b640-da373b2edad9" />

Charts Visualization
<img width="1170" height="898" alt="image" src="https://github.com/user-attachments/assets/509d24fd-b579-41b5-aed1-69f27c2da242" />
