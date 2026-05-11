import pytest
from unittest.mock import patch, MagicMock
import weather

FAKE_API_RESPONSE = {
    "daily": {
        "time": ["2026-05-11"],
        "sunrise": ["2026-05-11T05:32"],
        "sunset": ["2026-05-11T20:45"],
        "cloud_cover_mean": [18],
        "precipitation_probability_max": [5],
        "uv_index_max": [7.4],
    },
    "hourly": {
        "time": ["2026-05-11T10:00", "2026-05-11T11:00"],
        "cloud_cover": [10, 25],
        "shortwave_radiation": [680.0, 730.5],
    },
}


def _mock_response(data):
    mock = MagicMock()
    mock.json.return_value = data
    return mock


def test_get_forecast_returns_all_expected_keys():
    with patch("httpx.get", return_value=_mock_response(FAKE_API_RESPONSE)):
        result = weather.get_forecast()

    assert set(result.keys()) == {
        "date", "sunrise", "sunset",
        "cloud_cover_mean_pct", "precipitation_probability_max_pct", "uv_index_max",
        "hourly_cloud_cover", "hourly_shortwave_radiation_wm2",
    }


def test_get_forecast_maps_daily_scalars():
    with patch("httpx.get", return_value=_mock_response(FAKE_API_RESPONSE)):
        result = weather.get_forecast()

    assert result["date"] == "2026-05-11"
    assert result["sunrise"] == "2026-05-11T05:32"
    assert result["sunset"] == "2026-05-11T20:45"
    assert result["cloud_cover_mean_pct"] == 18
    assert result["precipitation_probability_max_pct"] == 5
    assert result["uv_index_max"] == 7.4


def test_get_forecast_zips_hourly_data():
    with patch("httpx.get", return_value=_mock_response(FAKE_API_RESPONSE)):
        result = weather.get_forecast()

    assert result["hourly_cloud_cover"] == {
        "2026-05-11T10:00": 10,
        "2026-05-11T11:00": 25,
    }
    assert result["hourly_shortwave_radiation_wm2"] == {
        "2026-05-11T10:00": 680.0,
        "2026-05-11T11:00": 730.5,
    }


def test_get_forecast_calls_open_meteo():
    with patch("httpx.get", return_value=_mock_response(FAKE_API_RESPONSE)) as mock_get:
        weather.get_forecast()

    url = mock_get.call_args.args[0]
    assert "open-meteo.com" in url


def test_get_forecast_includes_required_params():
    with patch("httpx.get", return_value=_mock_response(FAKE_API_RESPONSE)) as mock_get:
        weather.get_forecast()

    params = mock_get.call_args.kwargs["params"]
    assert "latitude" in params
    assert "longitude" in params
    assert "forecast_days" in params
    assert params["forecast_days"] == 1


def test_get_forecast_raises_on_http_error():
    mock = MagicMock()
    mock.raise_for_status.side_effect = Exception("404 Not Found")
    with patch("httpx.get", return_value=mock):
        with pytest.raises(Exception, match="404 Not Found"):
            weather.get_forecast()
