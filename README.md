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

## 📷 Demo

### Dashboard Overview
![Dashboard](https://github.com/user-attachments/assets/dfc24cbc-1161-4074-8525-2c8c74bb49c7)

### Station Detail
![Station Detail](https://github.com/user-attachments/assets/ef5673b7-a510-4f36-abd7-ad319717b872)

### Charts Visualization
![Charts](https://github.com/user-attachments/assets/6936b21d-156d-43ab-be11-ec04258de4bd)

