# 🌦️ Weather App (Python + Tkinter)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-green)
![Last Commit](https://img.shields.io/github/last-commit/10daviesb/weather-app)

A beautiful, lightweight desktop app that shows the current weather for any city worldwide.  
Built with Python, Tkinter GUI, and OpenWeatherMap API.

---

## ✨ Features

- 🌎 Select a country (with flag emojis!)
- 🏙️ Select or type a city (auto-suggests cities for the chosen country)
- ☁️ Displays:
  - Temperature
  - Feels like
  - Weather description (with emojis)
  - Humidity
  - Wind Speed
- 🔄 Refresh button with a **10-minute cooldown** and live countdown timer
- 🔧 Settings menu to **change the default city** (remembers across app restarts)
- ⚡ Loads the OpenWeatherMap city list dynamically at startup
- 🛡️ API key hidden using `.env` file for security

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/weather-app.git
cd weather-app
```

### 2. Install requirements

```bash
pip install -r requirements.txt
```

### 3. Setup your `.env`

Create a `.env` file in the project root:

```plaintext
API_KEY=your_openweathermap_api_key_here
```

(You can get a free API key at [OpenWeatherMap](https://openweathermap.org/api))

### 4. Make sure you have `city.list.json`

Download the `city.list.json` from OpenWeatherMap bulk data:  
👉 [http://bulk.openweathermap.org/sample/](http://bulk.openweathermap.org/sample/)

Place it inside the project folder.

---

## 🖥️ Running the App

```bash
python weather_app_gui.py
```

---

## 📦 Built With

- [Python](https://www.python.org/)
- [Tkinter](https://wiki.python.org/moin/TkInter)
- [OpenWeatherMap API](https://openweathermap.org/api)

---

## 📄 License

This project is licensed under the MIT License.  
See the [LICENSE](LICENSE) file for details.

---

## 📷 Screenshots

*Soon™*

---

## 🛠️ Future Improvements

- Add light/dark theme toggle
- Improve search with fuzzy matching
- Package as a standalone executable (.exe)

---

## 🙌 Credits

Built by **Bradley Davies** ❤️
