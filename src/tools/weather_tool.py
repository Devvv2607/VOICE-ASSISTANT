"""
Weather information tool for getting current weather data.
"""

import requests
from typing import Optional
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun


class WeatherTool(BaseTool):
    """LangChain tool for weather information."""
    
    name = "weather_checker"
    description = "Get weather information for a location. Input should be the location name."
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """Get weather information."""
        try:
            location = query.strip() or "current location"
            url = f"http://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                current = data['current_condition'][0]
                
                temp_c = current['temp_C']
                temp_f = current['temp_F']
                desc = current['weatherDesc'][0]['value']
                humidity = current['humidity']
                feels_like_c = current['FeelsLikeC']
                wind_speed = current['windspeedKmph']
                
                return f"Weather in {location}: {desc}, {temp_c}°C ({temp_f}°F), feels like {feels_like_c}°C, humidity {humidity}%, wind {wind_speed} km/h"
            else:
                return f"Could not get weather for {location}"
                
        except Exception as e:
            return f"Weather check failed: {str(e)}"