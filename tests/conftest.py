import os
import sys

# Set required env vars before any app module is imported (config.py reads them at module level)
os.environ.update({
    "DEYE_APP_ID": "test_app_id",
    "DEYE_APP_SECRET": "test_app_secret",
    "DEYE_EMAIL": "test@example.com",
    "DEYE_PASSWORD": "test_password",
    "DEYE_DEVICE_SN": "test_device_sn",
    "LATITUDE": "50.45",
    "LONGITUDE": "30.52",
    "ANTHROPIC_API_KEY": "test_anthropic_key",
})

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
