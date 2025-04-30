# weather_app_gui.py

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, Toplevel
from PIL import Image, ImageTk
import requests
import json
import os
from io import BytesIO
from dotenv import load_dotenv
from difflib import get_close_matches

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
countries_list = []
country_code_map = {}
cities_by_country = {}
city_list = []
cooldown_seconds_left = 0
unit_preference = "metric"
search_history = []
dark_mode = False
icon_image = None
favorites = []
language = "en"

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

translations = {
    "en": {
        "select_country": "Select Country:",
        "select_city": "Select or Enter City:",
        "get_weather": "Get Weather",
        "search_history": "Search History:",
        "change_default_city": "Change Default City",
        "toggle_temp": "Toggle °C/°F",
        "toggle_dark_mode": "Toggle Dark Mode",
        "language_changed": "Language set to English",
        "refresh_available": "Refresh available in",
        "no_forecast": "No forecast data available.",
    },
    "nl": {
        "select_country": "Kies een land:",
        "select_city": "Selecteer of voer een stad in:",
        "get_weather": "Weer ophalen",
        "search_history": "Zoekgeschiedenis:",
        "change_default_city": "Standaardstad wijzigen",
        "toggle_temp": "Schakel °C/°F",
        "toggle_dark_mode": "Schakel donkere modus",
        "language_changed": "Taal ingesteld op Nederlands",
        "refresh_available": "Vernieuwen beschikbaar over",
        "no_forecast": "Geen weersvoorspelling beschikbaar.",
    },
}

# --- Load City List ---
def load_city_data():
    global countries, countries_list, cities_by_country, country_code_map

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
            countries_list.append(country)
            countries[country] = code
            country_code_map[country] = country
            cities_by_country[country] = sorted(set(cities))

# --- Enhanced Fuzzy Filtering ---
def filter_city_list(event=None):
    typed = city_box.get()
    matches = get_close_matches(typed, city_list, n=10, cutoff=0.3)
    city_box["values"] = matches

def filter_country_list(event=None):
    typed = country_box.get()
    matches = get_close_matches(typed, countries_list, n=10, cutoff=0.3)
    country_box["values"] = matches

# --- Default City Dialog ---
def change_default_city():
    def save_new_default():
        selected_country = country_dropdown.get()
        selected_city = city_dropdown.get()
        if selected_country and selected_city:
            country_box.set(selected_country)
            city_box.set(selected_city)
            save_default_city(selected_country, selected_city)
            top.destroy()

    top = Toplevel(root)
    top.title("Change Default City")
    top.geometry("350x200")

    tk.Label(top, text="Select Country:").pack(pady=(10, 0))
    country_dropdown = ttk.Combobox(top, values=countries_list)
    country_dropdown.pack(pady=5)
    country_dropdown.set(country_box.get())

    tk.Label(top, text="Select or Enter City:").pack(pady=(10, 0))
    city_dropdown = ttk.Combobox(top)
    city_dropdown.pack(pady=5)
    city_dropdown.set(city_box.get())

    def update_dropdown(event=None):
        selected = country_dropdown.get()
        if selected:
            country_name = country_code_map.get(selected)
            options = cities_by_country.get(country_name, [])
            city_dropdown["values"] = options

    def filter_dropdown(event=None):
        typed = city_dropdown.get()
        all_values = city_dropdown["values"] if city_dropdown["values"] else []
        city_dropdown["values"] = get_close_matches(typed, all_values, n=10, cutoff=0.3)

    def filter_country_dropdown(event=None):
        typed = country_dropdown.get()
        country_dropdown["values"] = get_close_matches(typed, countries_list, n=10, cutoff=0.3)

    def select_match(event):
        if event.keysym == "Down":
            event.widget.event_generate("<Down>")
        elif event.keysym == "Return":
            if event.widget["values"]:
                event.widget.set(event.widget["values"][0])

    country_dropdown.bind("<<ComboboxSelected>>", update_dropdown)
    country_dropdown.bind("<KeyRelease>", filter_country_dropdown)
    city_dropdown.bind("<KeyRelease>", filter_dropdown)
    country_dropdown.bind("<KeyPress>", select_match)
    city_dropdown.bind("<KeyPress>", select_match)

    tk.Button(top, text="Save Default", command=save_new_default).pack(pady=10)

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
    params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": unit_preference, "lang": language}
    try:
        response = requests.get(ONECALL_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Failed to fetch data: {e}")

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

def display_forecast(data):
    if "daily" in data:
        forecast_text = "7-Day Forecast:\n" if language == "en" else "7-daagse voorspelling:\n"
        for day in data["daily"][:7]:
            temp = round(day["temp"]["day"])
            desc = day["weather"][0]["description"].capitalize()
            forecast_text += f"- {desc}, {temp}°{'C' if unit_preference == 'metric' else 'F'}\n"
        forecast_label.config(text=forecast_text)
    else:
        forecast_label.config(text=translations[language]["no_forecast"])

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
    new_unit = "imperial" if unit_preference == "metric" else "metric"
    
    # Update the global unit preference first
    unit_preference = new_unit

    # Check if cached data is available
    cached_data = load_weather_cache()
    if cached_data:
        # Check if the cached data is in the current unit
        if cached_data.get("unit") != new_unit:
            # Convert temperatures in cached data to the new unit
            cached_data = convert_units(cached_data, new_unit)
            save_weather_cache(cached_data)  # Save the updated data
        display_weather(cached_data)  # Use cached data to update the display
    else:
        # Fetch new data if no cache exists
        fetch_weather()

def convert_units(data, target_unit):
    """Convert temperature values in the weather data to the target unit."""
    if "current" in data:
        data["current"]["temp"] = convert_temperature(data["current"]["temp"], target_unit)
        data["current"]["feels_like"] = convert_temperature(data["current"]["feels_like"], target_unit)
    if "daily" in data:
        for day in data["daily"]:
            day["temp"]["day"] = convert_temperature(day["temp"]["day"], target_unit)
            day["temp"]["min"] = convert_temperature(day["temp"]["min"], target_unit)
            day["temp"]["max"] = convert_temperature(day["temp"]["max"], target_unit)
    data["unit"] = target_unit  # Update the unit in the data
    return data

def convert_temperature(temp, target_unit):
    """Convert a temperature value to the target unit."""
    if target_unit == "imperial":  # Convert Celsius to Fahrenheit
        return round((temp * 9/5) + 32, 1)
    elif target_unit == "metric":  # Convert Fahrenheit to Celsius
        return round((temp - 32) * 5/9, 1)
    return temp  # Return the original value if no conversion is needed

def toggle_theme():
    global dark_mode
    dark_mode = not dark_mode
    bg = "#2e2e2e" if dark_mode else "#f0f0f0"
    fg = "#ffffff" if dark_mode else "#000000"
    root.config(bg=bg)
    for widget in root.winfo_children():
        try:
            widget.config(bg=bg, fg=fg)
            if isinstance(widget, ttk.Combobox):
                widget.config(background=bg, foreground=fg)
        except:
            pass

def fetch_weather():
    global cooldown_seconds_left
    weather_label.config(text="Fetching weather data...")
    root.update_idletasks()
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
        timer_label.config(
            text=f"{translations[language]['refresh_available']} {mins:02}:{secs:02}"
        )
        cooldown_seconds_left -= 1
        root.after(1000, update_timer)
    else:
        fetch_button.config(state="normal")
        timer_label.config(text="")

def filter_city_list():
    typed = city_box.get()
    matches = get_close_matches(typed, city_list, n=10, cutoff=0.3)
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
    new_country = simpledialog.askstring("Change Default", "Enter country:")
    if new_country and new_country in countries:
        new_city = simpledialog.askstring("Change Default", "Enter city:")
        if new_city:
            country_box.set(new_country)
            city_box.set(new_city)
            save_default_city(new_country, new_city)
            messagebox.showinfo("Success", f"Default city set to {new_city}, {new_country}.")
    else:
        messagebox.showerror("Error", "Invalid country name.")

def fetch_location_weather():
    try:
        response = requests.get("http://ip-api.com/json/")
        response.raise_for_status()
        location = response.json()
        city = location.get("city")
        country_code = location.get("countryCode")
        lat, lon = get_coordinates(city, country_code)
        if lat and lon:
            data = get_weather(lat, lon)
            display_weather(data)
    except:
        messagebox.showerror("Error", "Could not fetch location-based weather.")

def add_to_favorites():
    city = city_box.get()
    if city and city not in favorites:
        favorites.append(city)
        messagebox.showinfo("Favorites", f"{city} added to favorites!")

def set_language(lang_code):
    global language
    language = lang_code

    # Update all UI elements
    country_label.config(text=translations[language]["select_country"])
    city_label.config(text=translations[language]["select_city"])
    fetch_button.config(text=translations[language]["get_weather"])
    history_label.config(text=translations[language]["search_history"])
    settings_menu.entryconfig(0, label=translations[language]["toggle_temp"])
    settings_menu.entryconfig(1, label=translations[language]["toggle_dark_mode"])
    messagebox.showinfo("Language Changed", translations[language]["language_changed"])

    # Refresh weather data without clearing it
    cached_data = load_weather_cache()
    if cached_data:
        display_weather(cached_data)  # Keep the current weather data displayed
    else:
        fetch_weather()  # Fetch new data if no cache exists

def update_default_button_state(*args):
    """Enable or disable the 'Set Default' button based on the input fields."""
    print(f"Country: {country_box.get()}, City: {city_box.get()}")  # Debugging
    if country_box.get() and city_box.get():
        set_default_button.config(state="normal")
    else:
        set_default_button.config(state="disabled")

# --- GUI Setup ---
root = tk.Tk()
root.title("Weather App")
root.geometry("420x600")
root.resizable(False, False)

load_city_data()

menu_bar = tk.Menu(root)
settings_menu = tk.Menu(menu_bar, tearoff=0)
settings_menu.add_command(label=translations[language]["toggle_temp"], command=toggle_units)
settings_menu.add_command(label=translations[language]["toggle_dark_mode"], command=toggle_theme)
menu_bar.add_cascade(label="Settings", menu=settings_menu)

language_menu = tk.Menu(menu_bar, tearoff=0)
language_menu.add_command(label="English", command=lambda: set_language("en"))
language_menu.add_command(label="Nederlands", command=lambda: set_language("nl"))
menu_bar.add_cascade(label="Language", menu=language_menu)

root.config(menu=menu_bar)

# Define the country, city, and history boxes first
country_label = tk.Label(root, text=translations[language]["select_country"])
country_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

history_label = tk.Label(root, text=translations[language]["search_history"])
history_label.grid(row=7, column=0, padx=10, pady=5, sticky="w")
history_box = ttk.Combobox(root, values=search_history, state="readonly")
history_box.grid(row=7, column=1, padx=10, pady=5, sticky="ew")
country_box = ttk.Combobox(root, values=countries_list)
country_box.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
country_box.bind("<<ComboboxSelected>>", update_city_list)

city_label = tk.Label(root, text=translations[language]["select_city"])
city_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
city_box = ttk.Combobox(root)
city_box.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
city_box.bind("<KeyRelease>", lambda event: filter_city_list())
city_box.bind("<Return>", on_enter_key)

fetch_button = tk.Button(root, text=translations[language]["get_weather"], command=fetch_weather)
fetch_button.grid(row=2, column=0, columnspan=2, pady=10)

set_default_button = tk.Button(root, text="Set Default", command=change_default_city)
set_default_button.grid(row=2, column=1, padx=10, pady=10, sticky="e")

timer_label = tk.Label(root, text="", font=("Helvetica", 10))
timer_label.grid(row=3, column=0, columnspan=2, pady=5)

icon_label = tk.Label(root)
icon_label.grid(row=4, column=0, columnspan=2, pady=5)

weather_label = tk.Label(root, text="", font=("Helvetica", 14))
weather_label.grid(row=5, column=0, columnspan=2, pady=20)

forecast_label = tk.Label(root, text="", font=("Helvetica", 10), justify="left")
forecast_label.grid(row=6, column=0, columnspan=2, pady=10)

load_default_city()
if dark_mode:
    toggle_theme()

root.columnconfigure(1, weight=1)

# --- Main ---
root.mainloop()
