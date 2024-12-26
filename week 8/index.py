import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime, timezone

# Function to fetch weather data
def get_weather_data(city, api_key):
    base_url = "http://api.openweathermap.org/data/2.5/forecast?"
    complete_url = f"{base_url}q={city}&appid={api_key}&units=metric"

    try:
        response = requests.get(complete_url)
        response.raise_for_status()

        # Parse JSON data
        data = response.json()

        if data["cod"] != "200":
            raise ValueError("City not found or invalid data returned")

        # Extracting current weather info (first entry)
        current_weather = data['list'][0]
        temp = current_weather['main']['temp']
        weather_description = current_weather['weather'][0]['description']
        weather_icon_code = current_weather['weather'][0]['icon']  # Get icon code
        wind_speed = current_weather['wind']['speed']
        city_name = data['city']['name']

        # Extract 5-day forecast
        forecast_data = []
        for i in range(0, 40, 8):  # Get the forecast every 8th entry (every 24 hours)
            forecast = data['list'][i]
            date_time = datetime.fromtimestamp(forecast['dt'], tz=timezone.utc)
            forecast_date = date_time.strftime('%Y-%m-%d %H:%M:%S')
            forecast_temp = forecast['main']['temp']
            forecast_description = forecast['weather'][0]['description']
            forecast_data.append(f"{forecast_date}: {forecast_temp}°C, {forecast_description}")

        return {
            "city_name": city_name,
            "current_temp": temp,
            "weather_description": weather_description,
            "weather_icon_code": weather_icon_code,  # Return the weather icon code
            "wind_speed": wind_speed,
            "forecast": forecast_data,
        }

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error while fetching weather data: {e}")
    except ValueError as e:
        raise e

# Function to fetch world news
def get_world_news(api_key):
    news_url = f"https://newsdata.io/api/1/news?apikey={api_key}&language=en&category=world"

    try:
        response = requests.get(news_url)
        response.raise_for_status()

        # Parse JSON data
        news_data = response.json()

        # Extract top news articles
        news_articles = []
        for article in news_data.get("results", []):
            news_articles.append(f"• {article['title']} ({article['source_id']})")

        if not news_articles:
            return "No recent world news found."

        return "\n".join(news_articles[:3])  # Limit to 10 articles for display

    except requests.exceptions.RequestException as e:
        return "Error fetching world news."

# Function to display weather results in GUI
def show_weather():
    city = city_entry.get()
    if city == "":
        messagebox.showerror("Error", "Please enter a city name!")
        return

    weather_api_key = "81d8c8b803f0f16cf5dcd08217db787d"
    try:
        weather_data = get_weather_data(city, weather_api_key)

        # Update the GUI with the weather data
        result_label.config(text=f"Weather in {weather_data['city_name']}:")
        temp_label.config(text=f"Temperature: {weather_data['current_temp']}°C")
        description_label.config(text=f"Description: {weather_data['weather_description']}")
        wind_label.config(text=f"Wind Speed: {weather_data['wind_speed']} m/s")

        # Display the forecast
        forecast_text = "\n".join(weather_data["forecast"])
        forecast_label.config(text=f"5-Day Forecast:\n{forecast_text}")

        # Fetch and display the weather icon
        icon_url = f"http://openweathermap.org/img/wn/{weather_data['weather_icon_code']}@2x.png"
        icon_response = requests.get(icon_url)
        icon_image = Image.open(BytesIO(icon_response.content))
        icon_image = icon_image.resize((50, 50), Image.Resampling.LANCZOS)
        icon_tk = ImageTk.PhotoImage(icon_image)
        icon_label.config(image=icon_tk)
        icon_label.image = icon_tk 

    except ValueError as e:
        messagebox.showerror("Error", str(e))

# Function to refresh news
def refresh_news():
    news_api_key = "pub_63363715998645ee864b980ce664e34647a7e"
    news = get_world_news(news_api_key)
    news_label.config(text=news)
    root.after(60000, refresh_news)

# GUI Setup
root = tk.Tk()
root.title("Weather App ")
root.geometry("600x800")
root.resizable(False, False)

# Set background image
bg_image = Image.open("background.jpg") 
bg_image = bg_image.resize((600, 800), Image.Resampling.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

canvas = tk.Canvas(root, width=600, height=800)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=bg_photo, anchor="nw")

# Input Section
city_label = tk.Label(root, text="Enter City:", bg="#ffffff", font=("Arial", 16, "bold"))
city_label.place(x=200, y=20)

city_entry = tk.Entry(root, font=("Arial", 14), width=30)
city_entry.place(x=200, y=60)

search_button = tk.Button(
    root, text="Get Weather", command=show_weather, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), relief="flat"
)
search_button.place(x=200, y=100)

# Weather info labels
result_label = tk.Label(root, text="", bg="#ffffff", font=("Arial", 12, "bold"))
result_label.place(x=100, y=150)

temp_label = tk.Label(root, text="", bg="#ffffff", font=("Arial", 12))
temp_label.place(x=100, y=200)

description_label = tk.Label(root, text="", bg="#ffffff", font=("Arial", 12))
description_label.place(x=100, y=250)

wind_label = tk.Label(root, text="", bg="#ffffff", font=("Arial", 12))
wind_label.place(x=100, y=300)

# 5-Day Forecast label
forecast_label = tk.Label(root, text="", bg="#ffffff", font=("Arial", 12, "bold"), justify="left", wraplength=400)
forecast_label.place(x=100, y=300)

# Weather Icon label
icon_label = tk.Label(root, bg="#ffffff")
icon_label.place(x=410, y=150)

# News Section
news_title_label = tk.Label(root, text="World News & Updates:", bg="#ffffff", font=("Arial", 13, "bold"))
news_title_label.place(x=150, y=550)

news_label = tk.Label(root, text="", bg="#ffffff", font=("Arial", 12), justify="left", wraplength=400)
news_label.place(x=150, y=600)

# Start refreshing news
refresh_news()

# Start the GUI loop
root.mainloop()
