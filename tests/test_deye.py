import pytest
from unittest.mock import patch, MagicMock, call
import deye


@pytest.fixture(autouse=True)
def reset_dry_run():
    deye.DRY_RUN = False
    yield
    deye.DRY_RUN = False


def _token_response(token="test_token_abc"):
    mock = MagicMock()
    mock.json.return_value = {"data": {"accessToken": token}}
    return mock


def _ok_response():
    return MagicMock()


# --- get_token ---

def test_get_token_returns_access_token():
    with patch("httpx.post", return_value=_token_response("my_token_123")):
        token = deye.get_token()
    assert token == "my_token_123"


def test_get_token_calls_token_endpoint():
    with patch("httpx.post", return_value=_token_response()) as mock_post:
        deye.get_token()
    url = mock_post.call_args.args[0]
    assert "/v1.0/account/token" in url


def test_get_token_includes_app_id_in_url():
    with patch("httpx.post", return_value=_token_response()) as mock_post:
        deye.get_token()
    url = mock_post.call_args.args[0]
    assert "appId=" in url


def test_get_token_sends_credentials_in_body():
    with patch("httpx.post", return_value=_token_response()) as mock_post:
        deye.get_token()
    payload = mock_post.call_args.kwargs["json"]
    assert "appSecret" in payload
    assert "email" in payload
    assert "password" in payload


def test_get_token_raises_on_http_error():
    mock = MagicMock()
    mock.raise_for_status.side_effect = Exception("401 Unauthorized")
    with patch("httpx.post", return_value=mock):
        with pytest.raises(Exception, match="401 Unauthorized"):
            deye.get_token()


# --- set_mode ---

def test_set_mode_calls_power_update_endpoint():
    with patch("httpx.post", side_effect=[_token_response(), _ok_response()]) as mock_post:
        deye.set_mode(deye.WORK_MODE_SELLING_FIRST)
    url = mock_post.call_args_list[1].args[0]
    assert "/v1.0/order/sys/power/update" in url


def test_set_mode_sends_work_mode_power_type():
    with patch("httpx.post", side_effect=[_token_response(), _ok_response()]) as mock_post:
        deye.set_mode(deye.WORK_MODE_SELLING_FIRST)
    payload = mock_post.call_args_list[1].kwargs["json"]
    assert payload["powerType"] == "WORK_MODE"


def test_set_mode_sends_correct_value():
    with patch("httpx.post", side_effect=[_token_response(), _ok_response()]) as mock_post:
        deye.set_mode(deye.WORK_MODE_ZERO_EXPORT_CT)
    payload = mock_post.call_args_list[1].kwargs["json"]
    assert payload["value"] == deye.WORK_MODE_ZERO_EXPORT_CT


def test_set_mode_includes_bearer_token_header():
    with patch("httpx.post", side_effect=[_token_response("tok999"), _ok_response()]) as mock_post:
        deye.set_mode(deye.WORK_MODE_SELLING_FIRST)
    headers = mock_post.call_args_list[1].kwargs["headers"]
    assert headers["Authorization"] == "Bearer tok999"


def test_set_mode_includes_device_sn():
    with patch("httpx.post", side_effect=[_token_response(), _ok_response()]) as mock_post:
        deye.set_mode(deye.WORK_MODE_SELLING_FIRST)
    payload = mock_post.call_args_list[1].kwargs["json"]
    assert "deviceSn" in payload


# --- convenience wrappers ---

def test_set_selling_first_passes_correct_mode():
    with patch("deye.set_mode") as mock_set_mode:
        deye.set_selling_first()
    mock_set_mode.assert_called_once_with(deye.WORK_MODE_SELLING_FIRST)


def test_set_zero_export_ct_passes_correct_mode():
    with patch("deye.set_mode") as mock_set_mode:
        deye.set_zero_export_ct()
    mock_set_mode.assert_called_once_with(deye.WORK_MODE_ZERO_EXPORT_CT)


def test_selling_first_mode_value_is_zero():
    assert deye.WORK_MODE_SELLING_FIRST == 0


def test_zero_export_ct_mode_value_is_two():
    assert deye.WORK_MODE_ZERO_EXPORT_CT == 2


# --- dry run ---

def test_dry_run_skips_http_calls():
    deye.DRY_RUN = True
    with patch("httpx.post") as mock_post:
        deye.set_mode(deye.WORK_MODE_SELLING_FIRST)
    mock_post.assert_not_called()


def test_dry_run_skips_http_calls_for_zero_export():
    deye.DRY_RUN = True
    with patch("httpx.post") as mock_post:
        deye.set_mode(deye.WORK_MODE_ZERO_EXPORT_CT)
    mock_post.assert_not_called()


def test_normal_mode_still_calls_api():
    with patch("httpx.post", side_effect=[_token_response(), _ok_response()]) as mock_post:
        deye.set_mode(deye.WORK_MODE_SELLING_FIRST)
    assert mock_post.call_count == 2
