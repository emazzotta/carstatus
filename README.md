# Car Status

Get your Tesla's current status. 

## Getting started

### Prerequisites

* Docker 18 or later

### Bootstrap

```bash
# Get the code, cd to carstatus, setup carstatus in Docker
git clone git@github.com:emazzotta/carstatus.git && \
    cd carstatus && \
    make bootstrap
```

### Configuration/Authorization

* Get your tesla token, [see instructions](https://tesla-api.timdorr.com/api-basics/authentication)
* Adapt the `.env`-file with your token 

|.env variable name|Use|Default|
|---|---|---|
|TESLA_TOKEN|The Tesla API Token|None|
|VEHICLE_ID|Your car's id (see Tesla API)|None|

### Run

```bash
make run
```

## Example Output

```text
🚀 MyVehicleName stats
🔋 SoC: 75% (372.39 km range)
🌡 Temp: 23.7˚ (22.5˚ outside)
💻 Version: 2019.32.2.2 da05838
📌 Location: Müllerstrasse 16, 8004 Zürich
🛣 Odometer: 10000.00 km
🔒 Car locked
```

## Author

[Emanuele Mazzotta](mailto:hello@mazzotta.me)
