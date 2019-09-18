#!/usr/bin/python

import os

import json
import requests as requests
import sys
import time
import urllib.parse
from os.path import join

MILES_TO_KILOMETER = 1.609


def print_stats(vehicle_data=None):
    if vehicle_data is None:
        vehicle_data = {}

    car_name = vehicle_data.get("display_name")

    charge_state = vehicle_data.get("charge_state", {})
    current_battery_level = charge_state.get("battery_level")
    current_battery_range = round(charge_state.get("battery_range") * MILES_TO_KILOMETER, 2)

    climate_state = vehicle_data.get("climate_state", {})
    inside_temperature = climate_state.get("inside_temp", {})
    outside_temperature = climate_state.get("outside_temp", {})

    vehicle_state = vehicle_data.get("vehicle_state", {})
    car_version = vehicle_state.get("car_version")
    is_locked = vehicle_state.get("locked")
    odometer = round(vehicle_state.get("odometer") * MILES_TO_KILOMETER, 2)

    drive_state = vehicle_data.get("drive_state", {})
    location = lat_lon_to_address(drive_state.get("latitude"), drive_state.get("longitude"))

    print(f'🚀 {car_name} stats')
    print(f'🔋 SoC: {current_battery_level}% ({current_battery_range} km range)')
    print(f'🌡  Temp: {inside_temperature}˚ ({outside_temperature}˚ outside)')
    print(f'💻 Version: {car_version}')
    print(f'📌 Location: {location}')
    print(f'🗺  Google Maps: https://www.google.ch/maps/search/{urllib.parse.quote(location)}')
    print(f'🛣  Odometer: {odometer} km')
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

        if vehicle_data_response.status_code == 408:
            post_wake_up(vehicle_id, headers)
        while vehicle_data_response.status_code == 408:
            time.sleep(2)
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
