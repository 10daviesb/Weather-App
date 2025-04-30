# 🌦️ Weather App (Python + Tkinter)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-green)
![Last Commit](https://img.shields.io/github/last-commit/10daviesb/Weather-App)

A beautiful, lightweight desktop app that shows the current weather for any city worldwide.  
Built with Python, Tkinter GUI, and OpenWeatherMap API.

---

## Table of Contents

- [✨ Features](#✨-features)
- [🛠️ Architecture](#🛠️-architecture)
- [💻 Tech Stack](#💻-tech-stack)
- [🚀 Getting Started](#🚀-getting-started)
- [🖥️ Running the App](#🖥️-running-the-app)
- [📦 Built With](#📦-built-with)
- [📷 Screenshots](#📷-screenshots)
- [🙌 Credits](#🙌-credits)
- [📄 License](#📄-license)

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
- 🔧 Settings menu to **toggle temperature units** and **dark mode**
- ⚡ Loads the OpenWeatherMap city list dynamically at startup
- 🛡️ API key hidden using `.env` file for security
- 🌐 **Offline Mode**: Cache the last successful weather fetch for offline viewing
- 🗂️ **Search History**: Quickly access recently viewed cities
- 🌐 **Multi-language Support**: Switch between English and Dutch dynamically

---

## 🛠️ Architecture

The project is organized as follows:
```
weather_app/              # Project root
├── city.list.json        # Bulk city data for auto-suggestions
├── weather_app.py        # Main application script (GUI + logic)
├── .env                  # Stores your OpenWeatherMap API key
├── weather_cache.json    # Cached weather data for offline mode
├── settings.json         # User preferences (default city, units, theme)
└── requirements.txt      # Python dependencies
```

### Key Components

- **`weather_app.py`**: Contains modular functions for data loading, API interaction, UI rendering, and state management.
- **`city.list.json`**: Dynamically loaded at runtime to populate country and city selectors.
- **`.env`**: Secures your API key via the `python-dotenv` package.

---

## 💻 Tech Stack

- **Language:** Python 3.8+
- **GUI Framework:** Tkinter
- **HTTP Client:** `requests`
- **Environment Management:** `python-dotenv`
- **Image Handling:** `Pillow`
- **Data Sources:** OpenWeatherMap API

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

## 🙌 Credits

Built by **Bradley Davies** ❤️
