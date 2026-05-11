import httpx
from config import LATITUDE, LONGITUDE


def get_forecast() -> dict:
    """Return today's weather forecast from Open-Meteo (no API key required)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "daily": "sunrise,sunset,cloud_cover_mean,precipitation_probability_max,uv_index_max",
        "hourly": "cloud_cover,shortwave_radiation",
        "timezone": "auto",
        "forecast_days": 1,
    }
    response = httpx.get(url, params=params, timeout=15)
    response.raise_for_status()
    data = response.json()

    daily = data["daily"]
    hourly = data["hourly"]

    return {
        "date": daily["time"][0],
        "sunrise": daily["sunrise"][0],
        "sunset": daily["sunset"][0],
        "cloud_cover_mean_pct": daily["cloud_cover_mean"][0],
        "precipitation_probability_max_pct": daily["precipitation_probability_max"][0],
        "uv_index_max": daily["uv_index_max"][0],
        "hourly_cloud_cover": dict(zip(hourly["time"], hourly["cloud_cover"])),
        "hourly_shortwave_radiation_wm2": dict(zip(hourly["time"], hourly["shortwave_radiation"])),
    }
