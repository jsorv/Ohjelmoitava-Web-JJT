
import json
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import main
from main import (
    build_alerts,
    check_alerts,
    fetch_forecasts_for_city,
    fetch_locations,
    handle_client,
    normalize_forecasts,
    pretty_print_alerts,
)


class FakeConnection:
    def __init__(self, incoming_text):
        self.incoming_text = incoming_text
        self.sent_data = b""
        self.closed = False

    def recv(self, _size):
        return self.incoming_text.encode()

    def send(self, data):
        self.sent_data = data

    def close(self):
        self.closed = True


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_hot_alert():
    forecast = {
        "temperature": 30,
        "wind_speed": 2,
        "humidity": 50,
        "cloud_cover": 20,
        "rain": False,
        "fog": False,
    }
    alerts = check_alerts(forecast)
    assert "Hot!" in alerts


def test_cold_alert():
    forecast = {
        "temperature": -25,
        "wind_speed": 2,
        "humidity": 50,
        "cloud_cover": 20,
        "rain": False,
        "fog": False,
    }
    alerts = check_alerts(forecast)
    assert "Cold!" in alerts


def test_wind_alert():
    forecast = {
        "temperature": 10,
        "wind_speed": 15,
        "humidity": 50,
        "cloud_cover": 20,
        "rain": False,
        "fog": False,
    }
    alerts = check_alerts(forecast)
    assert "Strong wind!" in alerts


def test_rain_and_fog_alerts():
    forecast = {
        "temperature": 5,
        "wind_speed": 2,
        "humidity": 50,
        "cloud_cover": 20,
        "rain": True,
        "fog": True,
    }
    alerts = check_alerts(forecast)
    assert "Rain!" in alerts
    assert "Fog!" in alerts


def test_no_alerts():
    forecast = {
        "temperature": 10,
        "wind_speed": 2,
        "humidity": 50,
        "cloud_cover": 20,
        "rain": False,
        "fog": False,
    }
    alerts = check_alerts(forecast)
    assert alerts == []


def test_multiple_alerts():
    forecast = {
        "temperature": 30,
        "wind_speed": 15,
        "humidity": 95,
        "cloud_cover": 95,
        "rain": True,
        "fog": True,
    }
    alerts = check_alerts(forecast)

    assert "Hot!" in alerts
    assert "Strong wind!" in alerts
    assert "Very humid!" in alerts
    assert "Very cloudy!" in alerts
    assert "Rain!" in alerts
    assert "Fog!" in alerts


def test_pretty_print_empty(capsys):
    pretty_print_alerts([])
    captured = capsys.readouterr()
    assert "No alerts" in captured.out


def test_pretty_print_grouping(capsys):
    alerts = [
        {"city": "Oulu", "alert": "Rain!"},
        {"city": "Oulu", "alert": "Rain!"},
        {"city": "Oulu", "alert": "Fog!"},
        {"city": "Washington", "alert": "Rain!"},
    ]

    pretty_print_alerts(alerts)
    captured = capsys.readouterr()

    assert "Oulu" in captured.out
    assert "Washington" in captured.out
    assert "Rain!" in captured.out
    assert "Fog!" in captured.out


def test_normalize_forecasts_with_dict():
    forecast = {"temperature": 10}
    result = normalize_forecasts(forecast)
    assert result == [forecast]


def test_normalize_forecasts_with_list():
    forecast_list = [{"temperature": 10}, {"temperature": 20}]
    result = normalize_forecasts(forecast_list)
    assert result == forecast_list


def test_handle_client_get_alerts():
    main.alerts = [{"city": "Oulu", "alert": "Rain!"}]
    conn = FakeConnection("get_alerts")

    handle_client(conn)

    parsed = json.loads(conn.sent_data.decode())
    assert parsed == [{"city": "Oulu", "alert": "Rain!"}]
    assert conn.closed is True


def test_handle_client_ping():
    conn = FakeConnection("ping")

    handle_client(conn)

    parsed = json.loads(conn.sent_data.decode())
    assert parsed == {"status": "ok"}
    assert conn.closed is True


def test_handle_client_unknown_command():
    conn = FakeConnection("something_else")

    handle_client(conn)

    parsed = json.loads(conn.sent_data.decode())
    assert parsed == {"error": "unknown command"}
    assert conn.closed is True


def test_fetch_locations(monkeypatch):
    def fake_get(url, timeout):
        assert url.endswith("/locations/")
        assert timeout == 5
        return FakeResponse([{"city": "Oulu"}])

    monkeypatch.setattr(main.requests, "get", fake_get)

    result = fetch_locations()
    assert result == [{"city": "Oulu"}]


def test_fetch_forecasts_for_city(monkeypatch):
    def fake_get(url, timeout):
        assert url.endswith("/locations/oulu/forecasts/")
        assert timeout == 5
        return FakeResponse([{"temperature": 5}])

    monkeypatch.setattr(main.requests, "get", fake_get)

    result = fetch_forecasts_for_city("Oulu")
    assert result == [{"temperature": 5}]


def test_build_alerts(monkeypatch):
    monkeypatch.setattr(
        main,
        "fetch_locations",
        lambda: [{"city": "Oulu"}, {"city": "Washington"}],
    )

    def fake_fetch_forecasts(city):
        if city == "Oulu":
            return [
                {
                    "temperature": 5,
                    "wind_speed": 2,
                    "humidity": 95,
                    "cloud_cover": 20,
                    "rain": True,
                    "fog": False,
                    "forecast_time": "2026-04-24T04:00:00",
                }
            ]
        return [
            {
                "temperature": 10,
                "wind_speed": 12,
                "humidity": 50,
                "cloud_cover": 20,
                "rain": False,
                "fog": False,
                "forecast_time": "2026-04-24T10:00:00",
            }
        ]

    monkeypatch.setattr(main, "fetch_forecasts_for_city", fake_fetch_forecasts)

    result = build_alerts()

    assert {"city": "Oulu", "alert": "Very humid!", "forecast_time": "2026-04-24T04:00:00"} in result
    assert {"city": "Oulu", "alert": "Rain!", "forecast_time": "2026-04-24T04:00:00"} in result
    assert {"city": "Washington", "alert": "Strong wind!", "forecast_time": "2026-04-24T10:00:00"} in result
