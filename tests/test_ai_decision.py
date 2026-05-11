import pytest
from unittest.mock import patch, MagicMock
import ai_decision

FAKE_FORECAST = {
    "date": "2026-05-11",
    "sunrise": "2026-05-11T05:32",
    "sunset": "2026-05-11T20:45",
    "cloud_cover_mean_pct": 18,
    "precipitation_probability_max_pct": 5,
    "uv_index_max": 7.4,
    "hourly_cloud_cover": {"2026-05-11T10:00": 10, "2026-05-11T11:00": 25},
    "hourly_shortwave_radiation_wm2": {"2026-05-11T10:00": 680.0, "2026-05-11T11:00": 730.5},
}

SELL_DECISION = {
    "sell_today": True,
    "sell_from": "06:00",
    "sell_until": "18:30",
    "reasoning": "High irradiance and low cloud cover expected.",
}

NO_SELL_DECISION = {
    "sell_today": False,
    "sell_from": None,
    "sell_until": None,
    "reasoning": "Heavy cloud cover forecast, not worth switching.",
}


def _tool_use_block(input_data):
    block = MagicMock()
    block.type = "tool_use"
    block.name = "make_inverter_decision"
    block.input = input_data
    return block


def _api_response(decision):
    response = MagicMock()
    response.content = [_tool_use_block(decision)]
    return response


def test_decide_returns_sell_decision():
    with patch.object(ai_decision.client.messages, "create", return_value=_api_response(SELL_DECISION)):
        result = ai_decision.decide(FAKE_FORECAST)

    assert result["sell_today"] is True
    assert result["sell_from"] == "06:00"
    assert result["sell_until"] == "18:30"
    assert "reasoning" in result


def test_decide_returns_no_sell_decision():
    with patch.object(ai_decision.client.messages, "create", return_value=_api_response(NO_SELL_DECISION)):
        result = ai_decision.decide(FAKE_FORECAST)

    assert result["sell_today"] is False
    assert result["sell_from"] is None
    assert result["sell_until"] is None


def test_decide_uses_correct_model():
    with patch.object(ai_decision.client.messages, "create", return_value=_api_response(SELL_DECISION)) as mock_create:
        ai_decision.decide(FAKE_FORECAST)

    assert mock_create.call_args.kwargs["model"] == "claude-sonnet-4-6"


def test_decide_forces_tool_choice():
    with patch.object(ai_decision.client.messages, "create", return_value=_api_response(SELL_DECISION)) as mock_create:
        ai_decision.decide(FAKE_FORECAST)

    tool_choice = mock_create.call_args.kwargs["tool_choice"]
    assert tool_choice == {"type": "tool", "name": "make_inverter_decision"}


def test_decide_sends_forecast_in_user_message():
    with patch.object(ai_decision.client.messages, "create", return_value=_api_response(SELL_DECISION)) as mock_create:
        ai_decision.decide(FAKE_FORECAST)

    messages = mock_create.call_args.kwargs["messages"]
    assert len(messages) == 1
    assert messages[0]["role"] == "user"
    assert "2026-05-11" in messages[0]["content"]


def test_decide_applies_prompt_caching():
    with patch.object(ai_decision.client.messages, "create", return_value=_api_response(SELL_DECISION)) as mock_create:
        ai_decision.decide(FAKE_FORECAST)

    system = mock_create.call_args.kwargs["system"]
    assert any(
        block.get("cache_control", {}).get("type") == "ephemeral"
        for block in system
    )


def test_decide_raises_if_no_tool_use_block():
    text_block = MagicMock()
    text_block.type = "text"
    response = MagicMock()
    response.content = [text_block]

    with patch.object(ai_decision.client.messages, "create", return_value=response):
        with pytest.raises(RuntimeError, match="did not return a decision"):
            ai_decision.decide(FAKE_FORECAST)


def test_decide_ignores_non_matching_tool_use_blocks():
    wrong_block = MagicMock()
    wrong_block.type = "tool_use"
    wrong_block.name = "some_other_tool"
    response = MagicMock()
    response.content = [wrong_block]

    with patch.object(ai_decision.client.messages, "create", return_value=response):
        with pytest.raises(RuntimeError):
            ai_decision.decide(FAKE_FORECAST)
