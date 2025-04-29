# weather_app_gui.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
import requests
import json
import os
from io import BytesIO
from dotenv import load_dotenv

# --- Load Environment Variables ---
load_dotenv()
API_KEY = os.getenv("API_KEY")

# --- Constants ---
GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
ONECALL_URL = "https://api.openweathermap.org/data/3.0/onecall"
ICON_URL = "http://openweathermap.org/img/wn/{}@2x.png"
SETTINGS_FILE = "settings.json"
CITY_DATA_FILE = "city.list.json"
COOLDOWN_TIME = 600

# --- Global Variables ---
countries = {}
countries_with_flags = []
country_code_map = {}
cities_by_country = {}
city_list = []
cooldown_seconds_left = 0
unit_preference = "metric"
search_history = []
dark_mode = False
icon_image = None

country_names = {
    "GB": "United Kingdom",
    "US": "United States",
    "JP": "Japan",
    "IN": "India",
    "FR": "France",
    "DE": "Germany",
    "NL": "Netherlands",
    "AU": "Australia",
    "CA": "Canada",
    "BR": "Brazil",
    "CN": "China",
    "ZA": "South Africa",
    "RU": "Russia",
    "ES": "Spain",
    "IT": "Italy",
    "MX": "Mexico",
}

# --- Load City List ---
def load_city_data():
    global countries, countries_with_flags, cities_by_country, country_code_map

    if not os.path.exists(CITY_DATA_FILE):
        messagebox.showerror("Missing File", f"{CITY_DATA_FILE} not found in the app folder.")
        return

    with open(CITY_DATA_FILE, "r", encoding="utf-8") as f:
        city_data = json.load(f)

    temp_countries = {}
    for entry in city_data:
        name = entry["name"]
        country_code = entry["country"]

        if country_code not in temp_countries:
            temp_countries[country_code] = []
        temp_countries[country_code].append(name)

    for code, cities in temp_countries.items():
        country = country_names.get(code)
        if country:
            flag = chr(127397 + ord(code[0])) + chr(127397 + ord(code[1]))
            label = f"{flag} {country}"
            countries_with_flags.append(label)
            countries[label] = code
            country_code_map[label] = country
            cities_by_country[country] = sorted(set(cities))

# --- Helper Functions ---
def get_coordinates(city, country_code):
    params = {"q": f"{city},{country_code}", "limit": 1, "appid": API_KEY}
    try:
        response = requests.get(GEO_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
    except:
        pass
    return None, None

def get_weather(lat, lon):
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": unit_preference}
    try:
        response = requests.get(ONECALL_URL, params=params)
        response.raise_for_status()
        return response.json()
    except:
        return None

def emoji_for_description(description):
    description = description.lower()
    if "cloud" in description:
        return "☁️"
    if "rain" in description:
        return "🌧️"
    if "sun" in description or "clear" in description:
        return "☀️"
    if "snow" in description:
        return "❄️"
    if "storm" in description:
        return "⛈️"
    return "🌈"

def display_weather(data):
    global icon_image
    if data:
        current = data.get("current", {})
        temp = round(current.get("temp", 0))
        feels_like = round(current.get("feels_like", 0))
        desc = current.get("weather", [{}])[0].get("description", "").capitalize()
        icon = current.get("weather", [{}])[0].get("icon", "01d")
        humidity = current.get("humidity", 0)
        wind_speed = round(current.get("wind_speed", 0))
        emoji = emoji_for_description(desc)

        unit_label = "°C" if unit_preference == "metric" else "°F"
        speed_label = "m/s" if unit_preference == "metric" else "mph"

        icon_url = ICON_URL.format(icon)
        try:
            response = requests.get(icon_url)
            img_data = response.content
            icon_img = Image.open(BytesIO(img_data)).resize((64, 64))
            icon_image = ImageTk.PhotoImage(icon_img)
            icon_label.config(image=icon_image)
        except:
            icon_label.config(image="")

        weather_label.config(
            text=(
                f"{emoji} {desc}\n"
                f"Temperature: {temp}{unit_label}\n"
                f"Feels like: {feels_like}{unit_label}\n"
                f"Humidity: {humidity}%\n"
                f"Wind Speed: {wind_speed} {speed_label}"
            )
        )
        save_weather_cache(data)
    else:
        cached = load_weather_cache()
        if cached:
            display_weather(cached)
            weather_label.config(text=weather_label.cget("text") + "\n(Offline mode: showing cached data)")
        else:
            weather_label.config(text="Could not fetch weather.")

def save_weather_cache(data):
    with open("weather_cache.json", "w") as f:
        json.dump(data, f)

def load_weather_cache():
    if os.path.exists("weather_cache.json"):
        with open("weather_cache.json", "r") as f:
            return json.load(f)
    return None

def save_default_city(country, city):
    settings = {
        "country": country,
        "city": city,
        "unit": unit_preference,
        "dark_mode": dark_mode,
        "search_history": search_history[-10:]
    }
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f)

def toggle_units():
    global unit_preference
    unit_preference = "imperial" if unit_preference == "metric" else "metric"
    fetch_weather()

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    bg = "#2e2e2e" if dark_mode else "#f0f0f0"
    fg = "#ffffff" if dark_mode else "#000000"
    root.config(bg=bg)
    for widget in root.winfo_children():
        try:
            widget.config(bg=bg, fg=fg)
        except:
            pass

def fetch_weather():
    global cooldown_seconds_left
    country_label = country_box.get()
    city_name = city_box.get()

    if not country_label or not city_name:
        messagebox.showerror("Input Error", "Please select a country and city.")
        return

    if city_name not in search_history:
        search_history.append(city_name)
        history_box["values"] = search_history[-10:]

    country_code = countries.get(country_label)
    lat, lon = get_coordinates(city_name, country_code)

    if lat is None or lon is None:
        weather_label.config(text="City not found.")
    else:
        data = get_weather(lat, lon)
        display_weather(data)
        save_default_city(country_label, city_name)
        start_cooldown()
def start_cooldown():
    global cooldown_seconds_left
    cooldown_seconds_left = COOLDOWN_TIME
    fetch_button.config(state="disabled")
    update_timer()

def update_timer():
    global cooldown_seconds_left
    if cooldown_seconds_left > 0:
        mins, secs = divmod(cooldown_seconds_left, 60)
        timer_label.config(text=f"Refresh available in {mins:02}:{secs:02}")
        cooldown_seconds_left -= 1
        root.after(1000, update_timer)
    else:
        fetch_button.config(state="normal")
        timer_label.config(text="")

def filter_city_list():
    typed = city_box.get()
    matches = [c for c in city_list if typed.lower() in c.lower()]
    city_box["values"] = matches

def update_city_list(event=None):
    global city_list
    selected_country = country_box.get()
    country_name = country_code_map.get(selected_country)
    city_list = cities_by_country.get(country_name, [])
    city_box.set("")
    city_box["values"] = city_list

def on_enter_key(event):
    if city_box["values"]:
        city_box.set(city_box["values"][0])

def load_default_city():
    global unit_preference, dark_mode, search_history
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            settings = json.load(f)
            country_box.set(settings.get("country", ""))
            city_box.set(settings.get("city", ""))
            unit_preference = settings.get("unit", "metric")
            dark_mode = settings.get("dark_mode", False)
            search_history.extend(settings.get("search_history", []))

def change_default_city():
    new_country = simpledialog.askstring("Change Default", "Enter country (with emoji):")
    if new_country and new_country in countries:
        new_city = simpledialog.askstring("Change Default", "Enter city:")
        if new_city:
            country_box.set(new_country)
            city_box.set(new_city)
            save_default_city(new_country, new_city)
            messagebox.showinfo("Success", f"Default city set to {new_city}, {new_country}.")
    else:
        messagebox.showerror("Error", "Invalid country name.")

# --- GUI Setup ---
root = tk.Tk()
root.title("Weather App")
root.geometry("420x600")
root.resizable(False, False)

load_city_data()

menu_bar = tk.Menu(root)
settings_menu = tk.Menu(menu_bar, tearoff=0)
settings_menu.add_command(label="Change Default City", command=change_default_city)
settings_menu.add_command(label="Toggle °C/°F", command=toggle_units)
settings_menu.add_command(label="Toggle Dark Mode", command=toggle_theme)
menu_bar.add_cascade(label="Settings", menu=settings_menu)
root.config(menu=menu_bar)

country_label = tk.Label(root, text="Select Country:")
country_label.pack(pady=(10, 0))

country_box = ttk.Combobox(root, values=countries_with_flags)
country_box.pack(pady=5)
country_box.bind("<<ComboboxSelected>>", update_city_list)

city_label = tk.Label(root, text="Select or Enter City:")
city_label.pack(pady=(10, 0))

city_box = ttk.Combobox(root)
city_box.pack(pady=5)
city_box.bind("<KeyRelease>", lambda event: filter_city_list())
city_box.bind("<Return>", on_enter_key)

history_label = tk.Label(root, text="Search History:")
history_label.pack(pady=(10, 0))

history_box = ttk.Combobox(root, values=search_history)
history_box.pack(pady=5)
history_box.bind("<<ComboboxSelected>>", lambda e: city_box.set(history_box.get()))

fetch_button = tk.Button(root, text="Get Weather", command=fetch_weather)
fetch_button.pack(pady=10)

timer_label = tk.Label(root, text="", font=("Helvetica", 10))
timer_label.pack(pady=5)

icon_label = tk.Label(root)
icon_label.pack(pady=5)

weather_label = tk.Label(root, text="", font=("Helvetica", 14))
weather_label.pack(pady=20)

load_default_city()
if dark_mode:
    toggle_theme()

# --- Main ---
root.mainloop()
