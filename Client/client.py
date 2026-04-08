"""Client for interacting with the WeatherRadar API."""

import os
from datetime import datetime
from datetime import timedelta
from urllib.parse import urljoin
import requests
from rich import print
from rich.align import Align

# --------------------------------------------------------
HOST_NAME = "http://localhost:5000/weatherradar/api/"
# --------------------------------------------------------

class APIDataSource:
    def __init__(self, host, ca_cert=None, api_key=None):
        assert host.startswith("http"), "No protocol in host address"
        self.host = host
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})
        if api_key:
            self.session.headers.update({"X-Api-Key": api_key})
        if ca_cert:
            self.session.verify = ca_cert

    def _get(self, uri):
        response = self.session.get(urljoin(self.host, uri))
        assert response.status_code == 200, f"GET {uri} -> {response.status_code}"
        return response.json()

    def _post(self, uri, data):
        response = self.session.post(urljoin(self.host, uri), json=data)
        assert response.status_code == 201, f"POST {uri} -> {response.status_code}: {response.text}"
        return response.headers.get("Location")

    def _put(self, uri, data):
        response = self.session.put(urljoin(self.host, uri), json=data)
        assert response.status_code == 204, f"PUT {uri} -> {response.status_code}: {response.text}"

    def _delete(self, uri):
        response = self.session.delete(urljoin(self.host, uri))
        assert response.status_code == 204, f"DELETE {uri} -> {response.status_code}: {response.text}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.session.close()

    # ----------------------------------------------------

    # GET METHODS
    def get_locations(self):
        """
        Retrieve all available locations.

        Returns:
            list: A list of location objects.
        """
        return self._get("locations/")

    def get_location(self, location):
        """
        Retrieve a specific location.

        Args:
            location (str): Location identifier.

        Returns:
            dict: Location data.
        """
        return self._get(f"locations/{location}/")

    def get_forecasts(self, location):
        """
        Retrieve all forecasts for a location.

        Args:
            location (str): Location identifier.

        Returns:
            list: A list of forecast entries.
        """
        return self._get(f"locations/{location}/forecasts/")

    def get_forecast(self, location, forecast):
        """
        Retrieve a specific forecast for a location.

        Args:
            location (str): Location identifier.
            forecast (str): Forecast identifier.

        Returns:
            dict: Forecast data.
        """
        return self._get(f"locations/{location}/forecasts/{forecast}/")

    def get_reports(self, location):
        """
        Retrieve all weather reports for a location.

        Args:
            location (str): Location identifier.

        Returns:
            list: A list of weather report entries.
        """
        return self._get(f"locations/{location}/reports/")

    def get_report(self, location, report):
        """
        Retrieve a specific weather report.

        Args:
            location (str): Location identifier.
            report (str): Report identifier.

        Returns:
            dict: Weather report data.
        """
        return self._get(f"locations/{location}/reports/{report}/")

    # POST METHODS
    def post_location(self, data):
        """
        Create a new location.

        Args:
            data (dict): Location data.

        Returns:
            str: URI of the created location.
        """
        return self._post("locations/", data)

    def post_forecast(self, location, data):
        """
        Create a new forecast for a location.

        Args:
            location (str): Location identifier.
            data (dict): Forecast data.

        Returns:
            str: URI of the created forecast.
        """
        return self._post(f"locations/{location}/forecasts/", data)

    def post_report(self, location, data):
        """
        Create a new weather report for a location.

        Args:
            location (str): Location identifier.
            data (dict): Report data.

        Returns:
            str: URI of the created report.
        """
        return self._post(f"locations/{location}/reports/", data)

    # PUT METHODS
    def update_location(self, location, data):
        """
        Update an existing location.

        Args:
            location (str): Location identifier.
            data (dict): Updated location data.
        """
        self._put(f"locations/{location}/", data)

    def update_forecast(self, location, forecast, data):
        """
        Update an existing forecast.

        Args:
            location (str): Location identifier.
            forecast (str): Forecast identifier.
            data (dict): Updated forecast data.
        """
        self._put(f"locations/{location}/forecasts/{forecast}/", data)

    def update_report(self, location, report, data):
        """
        Update an existing weather report.

        Args:
            location (str): Location identifier.
            report (str): Report identifier.
            data (dict): Updated report data.
        """
        self._put(f"locations/{location}/reports/{report}/", data)

    # DELETE METHODS
    def delete_location(self, location):
        """
        Delete a location.

        Args:
            location (str): Location identifier.
        """
        self._delete(f"locations/{location}/")

    def delete_forecast(self, location, forecast):
        """
        Delete a forecast.

        Args:
            location (str): Location identifier.
            forecast (str): Forecast identifier.
        """
        self._delete(f"locations/{location}/forecasts/{forecast}/")

    def delete_report(self, location, report):
        """
        Delete a weather report.

        Args:
            location (str): Location identifier.
            report (str): Report identifier.
        """
        return self._delete(f"locations/{location}/reports/{report}/")

    # ----------------------------------------------------

# PRINT HELPERS

def print_entry(entry):
    """
    Print a formatted weather entry.

    Displays report time, optional forecast time, and weather details such as
    temperature, humidity, wind speed, cloud cover, rain, and fog.

    Args:
        entry (dict): A dictionary containing weather data.
    """
    report_time = datetime.fromisoformat(entry["report_time"])
    print(f"Report time: {report_time.strftime('%d.%m.%Y %H:%M')}")

    if entry.get("forecast_time"):
        forecast_time = datetime.fromisoformat(entry["forecast_time"])
        print(f"Forecast time: {forecast_time.strftime('%d.%m.%Y %H:%M')}")

    print(f"Temperature: {entry['temperature']} °C")
    print(f"Humidity: {entry['humidity']} %")
    print(f"Wind speed: {entry['wind_speed']} m/s")
    print(f"Cloud cover: {entry['cloud_cover']} %")
    print(f"Rain: {entry['rain']}")
    print(f"Fog: {entry['fog']}")

def print_list(entries):
    """
    Print a list of weather entries.

    Iterates through a list of weather entries and prints each one using
    `print_entry`. If the list is empty, a message is displayed.

    Args:
        entries (list): A list of weather entry dictionaries.
    """
    if not entries:
        print("No entries found.")
        return
    for i, entry in enumerate(entries, start=1):
        print(f"{i}.")
        print_entry(entry)
        print("\n")

# ADDITIONAL HELPERS

def get_current_weather(api, location):
    """
    Retrieve the most recent weather report for a location.

    Args:
        api (APIDataSource): The API data source instance.
        location (str): The location identifier (e.g., "oulu").

    Returns:
        dict or None: The most recent weather report, or None if no reports exist.
    """
    reports = api.get_reports(location)
    if not reports:
        return None

    return max(
        reports,
        key=lambda report: datetime.fromisoformat(report["report_time"])
    )

def get_tomorrow_weather(api, location):
    """
    Retrieve the forecast closest to 24 hours from now for a location.

    Args:
        api (APIDataSource): The API data source instance.
        location (str): The location identifier (e.g., "oulu").

    Returns:
        dict or None: The closest forecast entry, or None if no valid forecasts exist.
    """
    forecasts = api.get_forecasts(location)
    if not forecasts:
        return None

    target_time = datetime.now() + timedelta(hours=24)

    tomorrow_forecasts = []
    for forecast in forecasts:
        if forecast.get("forecast_time"):
            tomorrow_forecasts.append(forecast)

    if not tomorrow_forecasts:
        return None

    return min(
        tomorrow_forecasts,
        key=lambda forecast: abs(datetime.fromisoformat(forecast["forecast_time"]) - target_time
        )
    )

# MAIN UI

def draw_map(selection):
    """
    Loads and prints a map file corresponding to the given selection.

    Args:
        selection (str or None): The selected location ("oulu", "washington", "moscow"),
                                 or None for the default map.
    """
    if selection == "oulu":
        with open("oulumap.txt", "r", encoding="utf-8") as map_file:
            print(Align.center(map_file.read()))
    elif selection == "washington":
        with open("washingtonmap.txt", "r", encoding="utf-8") as map_file:
            print(Align.center(map_file.read()))
    elif selection == "moscow":
        with open("moscowmap.txt", "r", encoding="utf-8") as map_file:
            print(Align.center(map_file.read()))
    else:
        with open("fullmap.txt", "r", encoding="utf-8") as map_file:
            print(Align.center(map_file.read()))

def update_graphics(menu_status, selection):
    """
    Update the terminal UI based on the current menu state.

    Args:
        menu_status (int): The current menu state (1 = world, 2 = city, 3 = list).
        selection (str or None): The currently selected location.
    """
    # WORLD MENU
    if menu_status == 1:
        os.system("cls" if os.name == "nt" else "clear")
        draw_map(selection)
        print("WeatherRadar ©2026\n")
        print("[red]SELECT TARGET:[/red]")
        print("1. Oulu, Finland")
        print("2. Washington, USA")
        print("3. Moscow, Russia\n")
        print("Q: Exit program\n")
    # CITY MENU
    if menu_status == 2:
        os.system("cls" if os.name == "nt" else "clear")
        draw_map(selection)
        print("WeatherRadar ©2026\n")
        print("[red]SELECT ACTION:[/red]")
        print("1. List all weather reports")
        print("2. List all weather forecasts")
        print("3. Get current weather")
        print("4. Get tomorrow's forecast\n")
    # LIST MODE
    if menu_status == 3:
        os.system("cls" if os.name == "nt" else "clear")

def main_ui_loop(api):
    """
    Handles user input, navigation between menus, and interaction with the API.

    Args:
        api (APIDataSource): The API data source instance.
    """
    while True:
        # WORLD MENU
        update_graphics(1, None)
        city_input = input().strip().lower()

        if city_input == "q":
            return
        if city_input in ("1","2","3"):
            if city_input == "1":
                city_input = "oulu"
            if city_input == "2":
                city_input = "washington"
            if city_input == "3":
                city_input = "moscow"

        if city_input not in ("oulu", "washington", "moscow", "1","2","3"):
            update_graphics(1, None)
            print("[red]That location is not available.[/red]")
            input("Press Enter to continue...")
            continue

        # CITY MENU
        update_graphics(2, city_input)
        option_input = input().strip().lower()

        # 1. LIST ALL WEATHER REPORTS FOR LOCATION
        if option_input == "1":
            data = api.get_reports(city_input)
            update_graphics(3, None)
            print_list(data)
            input("Press Enter to continue...")
            continue

        # 2. LIST ALL WEATHER FORECASTS FOR LOCATION
        if option_input == "2":
            data = api.get_forecasts(city_input)
            update_graphics(3, None)
            print_list(data)
            input("Press Enter to continue...")
            continue

        # 3. GET CURRENT WEATHER (IN REPORTS)
        if option_input == "3":
            data = get_current_weather(api, city_input)
            if data is None:
                update_graphics(2, city_input)
                print("[red]No weather reports found.[/red]")
                input("Press Enter to continue...")
                continue
            else:
                update_graphics(3, None)
                print_entry(data)
                input("\nPress Enter to continue...")
                continue

        # 4. GET FORECAST
        if option_input == "4":
            data = get_tomorrow_weather(api, city_input)
            if data is None:
                update_graphics(2, city_input)
                print("[red]No weather forecasts found.[/red]")
                input("Press Enter to continue...")
                continue
            else:
                update_graphics(3, None)
                print_entry(data)
                input("\nPress Enter to continue...")
                continue

        else:
            update_graphics(1, None)
            print("[red]Incorrect input![/red]")
            input("Press Enter to continue...")
            continue

if __name__ == "__main__":
    with APIDataSource(HOST_NAME) as api_data_source:
        main_ui_loop(api_data_source)
