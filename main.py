from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, ListProperty
from kivy.core.window import Window
from kivy.uix.widget import Widget
import requests
import os
import math
from datetime import datetime, timedelta

class ForecastItem(BoxLayout):
    day = StringProperty()
    icon_source = StringProperty()
    min_temp = StringProperty()
    max_temp = StringProperty()

class WeatherLayout(FloatLayout):
    city = StringProperty("Toluca")
    country = StringProperty("")
    temperature = StringProperty("--°C")
    description = StringProperty("Buscando clima...")
    humidity = StringProperty("--%")
    wind_speed = StringProperty("-- m/s")
    feels_like = StringProperty("--°C")
    temp_min_max = StringProperty("Máx: --°C | Mín: --°C")
    forecast_data = ListProperty([])
    icon_path = StringProperty("")
    background_path = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(base_path, "assets/icons/clear.png")
        self.background_path = os.path.join(base_path, "assets/backgrounds/clear.jpg")
        self.api_key = "6c16aeb436be40e12a94291943434e0e"  # <<--- TU API KEY
        self.get_weather()

    def update_city(self, new_city):
        self.city = new_city
        self.get_weather()

    def get_weather(self):
        ciudad = self.city.strip()
        if not self.api_key:
            self.description = "Falta API Key"
            return
        try:
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={ciudad}&limit=1&appid={self.api_key}"
            geo_response = requests.get(geo_url, timeout=10).json()
            if not geo_response:
                self.temperature = "--°C"
                self.description = "Ciudad no encontrada"
                self.set_default_assets()
                return
            lat = geo_response[0]['lat']
            lon = geo_response[0]['lon']
            self.country = geo_response[0].get('country', '')

            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric&lang=es"
            data = requests.get(weather_url, timeout=10).json()

            temp = math.floor(data.get("main", {}).get("temp", 0))
            desc = data.get("weather", [{}])[0].get("description", "")
            main_condition = data.get("weather", [{}])[0].get("main", "")

            humidity_val = data.get("main", {}).get("humidity", 0)
            wind_val = data.get("wind", {}).get("speed", 0)
            feels_like_val = math.floor(data.get("main", {}).get("feels_like", 0))
            temp_min = math.floor(data.get("main", {}).get("temp_min", 0))
            temp_max = math.floor(data.get("main", {}).get("temp_max", 0))

            self.temperature = f"{temp}°C"
            self.description = desc.capitalize()
            self.humidity = f"{humidity_val}%"
            self.wind_speed = f"{wind_val:.1f} m/s"
            self.feels_like = f"{feels_like_val}°C"
            self.temp_min_max = f"Máx: {temp_max}°C | Mín: {temp_min}°C"

            self.set_assets(main_condition)
            self.get_forecast(lat, lon)

        except Exception as e:
            print(f"Error al obtener clima: {e}")
            self.temperature = "--°C"
            self.description = "Sin conexión o error de API"
            self.set_default_assets()
            self.forecast_data = []

    def get_forecast(self, lat, lon):
        forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={self.api_key}&units=metric&lang=es"
        forecast_response = requests.get(forecast_url, timeout=10).json()

        if 'list' not in forecast_response:
            self.forecast_data = []
            return

        forecast_list = forecast_response['list']
        daily_forecasts = {}
        for item in forecast_list:
            dt_obj = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
            date_str = dt_obj.strftime('%Y-%m-%d')
            temp = item['main']['temp']
            condition_main = item['weather'][0]['main'].lower()

            if date_str not in daily_forecasts:
                daily_forecasts[date_str] = {
                    'min_temp': temp,
                    'max_temp': temp,
                    'date_obj': dt_obj,
                    'main_icon_condition': condition_main
                }
            else:
                daily_forecasts[date_str]['min_temp'] = min(daily_forecasts[date_str]['min_temp'], temp)
                daily_forecasts[date_str]['max_temp'] = max(daily_forecasts[date_str]['max_temp'], temp)
                if condition_main in ["rain", "storm", "snow", "thunderstorm"]:
                    daily_forecasts[date_str]['main_icon_condition'] = condition_main

        processed = []
        today = datetime.now().date()
        for date_str, data in daily_forecasts.items():
            date_obj = data['date_obj'].date()
            if date_obj < today or len(processed) >= 5:
                continue
            if date_obj == today:
                day_name = "Hoy"
            elif date_obj == today + timedelta(days=1):
                day_name = "Mañana"
            else:
                day_name = data['date_obj'].strftime('%A')
                # Traducir a español
                dias = {
                    "Monday":"Lunes","Tuesday":"Martes","Wednesday":"Miércoles",
                    "Thursday":"Jueves","Friday":"Viernes","Saturday":"Sábado","Sunday":"Domingo"
                }
                day_name = dias.get(day_name, day_name)
            processed.append({
                'day': day_name,
                'icon_source': self._get_icon_file_path(data['main_icon_condition']),
                'min_temp': f"{math.floor(data['min_temp'])}°",
                'max_temp': f"{math.floor(data['max_temp'])}°"
            })

        self.forecast_data = processed
        self.update_forecast_widgets()

    def _get_icon_file_path(self, condition):
        base_path = os.path.dirname(os.path.abspath(__file__))
        condition = condition.lower()
        icon_mapping = {
            "clear": "clear.png", "sun": "clear.png",
            "cloud": "clouds.png", "mist": "clouds.png", "fog": "clouds.png",
            "rain": "rain.png", "drizzle": "rain.png",
            "storm": "storm.png", "thunderstorm": "storm.png",
            "snow": "snow.png"
        }
        icon_file_name = next((v for k, v in icon_mapping.items() if k in condition), "clear.png")
        return os.path.join(base_path, "assets/icons", icon_file_name)

    def set_assets(self, condition):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = self._get_icon_file_path(condition)
        bg_mapping = {
            "clear": "clear.jpg",
            "cloud": "clouds.jpg",
            "rain": "rain.jpg",
            "storm": "storm.jpg",
            "snow": "snow.jpg"
        }
        bg_file = next((v for k, v in bg_mapping.items() if k in condition), "clear.jpg")
        self.background_path = os.path.join(base_path, "assets/backgrounds", bg_file)

    def set_default_assets(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.icon_path = os.path.join(base_path, "assets/icons/clear.png")
        self.background_path = os.path.join(base_path, "assets/backgrounds/clear.jpg")

    def update_forecast_widgets(self):
        container = self.ids.forecast_container
        container.clear_widgets()
        for day in self.forecast_data:
            item = ForecastItem(
                day=day["day"],
                icon_source=day["icon_source"],
                min_temp=day["min_temp"],
                max_temp=day["max_temp"]
            )
            container.add_widget(item)


class WeatherApp(App):
    def build(self):
        Window.clearcolor = (0.95, 0.95, 0.95, 1)
        return WeatherLayout()


if __name__ == "__main__":
    WeatherApp().run()