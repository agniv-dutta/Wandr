from backend.tools.destination_tool import get_destination_info
from backend.tools.weather_tool import get_weather_forecast

if __name__ == "__main__":
    print(get_destination_info.run("Tokyo"))
    print()
    print(get_weather_forecast.run("Paris"))
