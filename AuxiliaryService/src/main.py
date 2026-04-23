import json
import socket
import threading
import time
from collections import defaultdict

import requests

API_URL = "http://localhost:5000/weatherradar/api"
POLL_INTERVAL_SECONDS = 10
SERVER_HOST = "localhost"
SERVER_PORT = 6000

alerts = []


def check_alerts(forecast):
    found_alerts = []

    temperature = forecast.get("temperature")
    wind_speed = forecast.get("wind_speed", 0)
    humidity = forecast.get("humidity", 0)
    cloud_cover = forecast.get("cloud_cover", 0)
    rain = forecast.get("rain", False)
    fog = forecast.get("fog", False)

    if temperature is not None:
        if temperature > 25:
            found_alerts.append("Hot!")
        if temperature < -20:
            found_alerts.append("Cold!")

    if wind_speed > 10:
        found_alerts.append("Strong wind!")

    if humidity > 90:
        found_alerts.append("Very humid!")

    if cloud_cover > 90:
        found_alerts.append("Very cloudy!")

    if rain:
        found_alerts.append("Rain!")

    if fog:
        found_alerts.append("Fog!")

    return found_alerts


def pretty_print_alerts(current_alerts):
    print("\n=== ALERTS ===")

    if not current_alerts:
        print("No alerts")
        print("-" * 30)
        return

    grouped = defaultdict(set)

    for item in current_alerts:
        city = item.get("city", "Unknown")
        alert = item.get("alert", "Unknown alert")
        grouped[city].add(alert)

    for city, city_alerts in grouped.items():
        print(f"{city}: {', '.join(sorted(city_alerts))}")

    print("-" * 30)


def fetch_locations():
    response = requests.get(f"{API_URL}/locations/", timeout=5)
    response.raise_for_status()
    return response.json()


def fetch_forecasts_for_city(city):
    city_slug = city.lower()
    response = requests.get(
        f"{API_URL}/locations/{city_slug}/forecasts/",
        timeout=5,
    )
    response.raise_for_status()
    return response.json()


def normalize_forecasts(forecast_data):
    if isinstance(forecast_data, dict):
        return [forecast_data]
    return forecast_data


def build_alerts():
    locations = fetch_locations()
    print("Checked locations:", locations)

    new_alerts = []

    for location in locations:
        city = location.get("city")
        if not city:
            continue

        forecast_data = fetch_forecasts_for_city(city)
        forecast_list = normalize_forecasts(forecast_data)

        for forecast in forecast_list:
            location_alerts = check_alerts(forecast)

            for alert in location_alerts:
                new_alerts.append(
                    {
                        "city": city,
                        "alert": alert,
                        "forecast_time": forecast.get("forecast_time"),
                    }
                )

    return new_alerts


def run():
    global alerts

    while True:
        try:
            alerts = build_alerts()
            pretty_print_alerts(alerts)
        except Exception as e:
            print("Error:", e)

        time.sleep(POLL_INTERVAL_SECONDS)


def handle_client(conn):
    try:
        data = conn.recv(1024).decode().strip()

        if data == "get_alerts":
            conn.send(json.dumps(alerts).encode())
        elif data == "ping":
            conn.send(json.dumps({"status": "ok"}).encode())
        else:
            conn.send(json.dumps({"error": "unknown command"}).encode())
    finally:
        conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SERVER_HOST, SERVER_PORT))
    server.listen(5)

    print(f"Auxiliary service listening on {SERVER_HOST}:{SERVER_PORT}")

    while True:
        conn, _ = server.accept()
        handle_client(conn)


if __name__ == "__main__":
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    start_server()
    