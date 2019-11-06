#!/usr/bin/python

import os

import json
import requests as requests
import sys
import time
import urllib.parse
from datetime import datetime, date
from os.path import join

MILES_TO_KILOMETER = 1.609


def print_stats(vehicle_data=None):
    if vehicle_data is None:
        vehicle_data = {}

    car_name = vehicle_data.get("display_name")

    charge_state = vehicle_data.get("charge_state", {})
    current_battery_level = charge_state.get("battery_level")
    current_battery_range = round(charge_state.get("battery_range", 0) * MILES_TO_KILOMETER, 2)

    climate_state = vehicle_data.get("climate_state", {})
    inside_temperature = climate_state.get("inside_temp", {})
    outside_temperature = climate_state.get("outside_temp", {})

    vehicle_state = vehicle_data.get("vehicle_state", {})
    car_version = vehicle_state.get("car_version")
    is_locked = vehicle_state.get("locked")
    odometer = round(vehicle_state.get("odometer", 0) * MILES_TO_KILOMETER, 2)

    drive_state = vehicle_data.get("drive_state", {})
    location = lat_lon_to_address(drive_state.get("latitude"), drive_state.get("longitude"))

    allowed_pro_rata_kilometers_reached_percentage = None
    allowed_pro_rata_kilometers = 0
    if os.environ.get('DATE_OF_OWNERSHIP') and os.environ.get('ALLOWED_KILOMETERS_PER_YEAR'):
        date_of_ownership = datetime.strptime(os.environ.get('DATE_OF_OWNERSHIP'), "%Y-%m-%d").date()
        days_of_ownership = (date.today() - date_of_ownership).days
        allowed_kilometers_per_year = float(os.environ.get('ALLOWED_KILOMETERS_PER_YEAR'))
        allowed_pro_rata_kilometers = round(allowed_kilometers_per_year / 365 * days_of_ownership, 2)
        allowed_pro_rata_kilometers_reached_percentage = round(100 / allowed_pro_rata_kilometers * odometer, 2)

    additional_kilometer_info = (
        f' ({allowed_pro_rata_kilometers_reached_percentage}% of max. {allowed_pro_rata_kilometers} km)'
        if allowed_pro_rata_kilometers_reached_percentage
        else ''
    )

    print(f'🚀 {car_name} stats')
    print(f'🔋 SoC: {current_battery_level}% ({current_battery_range} km range)')
    print(f'🌡  Temp: {inside_temperature}˚ ({outside_temperature}˚ outside)')
    print(f'💻 Version: {car_version}')
    print(f'📌 Location: {location}')
    print(f'🗺  Google Maps: https://www.google.ch/maps/search/{urllib.parse.quote(location)}')
    print(f'🛣  Odometer: {odometer} km' + additional_kilometer_info)
    print('🔒 Car locked' if is_locked else '🚗 Car unlocked')


def lat_lon_to_address(latitude, longitude):
    result = json.loads(
        requests.get(
            f'https://nominatim.openstreetmap.org/reverse'
            f'?format=json'
            f'&lat={latitude}'
            f'&lon={longitude}'
        ).content
    )

    address = result.get('address', {})

    house_number = address.get("house_number", "").upper()
    road = address.get("road", "")
    street = f'{road} {house_number}' if house_number else road

    return f'{street}, {address.get("postcode", "")} {address.get("city", "")}'


def load_vehicle_data():
    tesla_token = os.environ.get('TESLA_TOKEN')
    vehicle_id = os.environ.get('VEHICLE_ID')

    if not tesla_token:
        print('You need to provide valid tesla credentials in the .env file!', file=sys.stderr)
        exit(1)

    if os.environ.get('ENV', 'prod') == 'prod':
        headers = {'Authorization': f'Bearer {tesla_token}'}

        vehicle_data_response = get_vehicle_data(vehicle_id, headers)

        if vehicle_data_response.status_code in (408, 504):
            post_wake_up(vehicle_id, headers)
        while vehicle_data_response.status_code in (408, 504):
            time.sleep(1)
            vehicle_data_response = get_vehicle_data(vehicle_id, headers)

        if not vehicle_data_response.ok:
            print(f'An error occurred, status: {vehicle_data_response.status_code}')

        return json.loads(vehicle_data_response.content).get('response', {})
    return json.loads(open(join('..', 'data', 'vehicle_data.json'), 'r+').read())


def get_vehicle_data(vehicle_id, headers):
    return requests.get(
        url=f'https://owner-api.teslamotors.com/api/1/vehicles/{vehicle_id}/vehicle_data',
        headers=headers
    )


def post_wake_up(vehicle_id, headers):
    return requests.post(
        url=f'https://owner-api.teslamotors.com/api/1/vehicles/{vehicle_id}/wake_up',
        headers=headers
    )


if __name__ == '__main__':
    print_stats(load_vehicle_data())
