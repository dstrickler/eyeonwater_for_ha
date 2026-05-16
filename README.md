# EyeOnWater for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

A Home Assistant integration for [EyeOnWater](https://eyeonwater.com) water meters by Dave Strickler. Fetches your water meter readings and usage data directly from the EyeOnWater API.

## Features

- **Current meter reading** sensor (total increasing, compatible with the Energy dashboard)
- **3-day usage** sensor
- Hourly polling
- UI-based setup via Home Assistant config flow (no YAML needed)
- Falls back to latest historical reading when live meter data is unavailable

## Installation

### HACS (recommended)

1. Open HACS in Home Assistant
2. Click the three-dot menu (top right) and select **Custom repositories**
3. Add `https://github.com/dstrickler/eyeonwater_for_ha` with category **Integration**
4. Click **Install**
5. Restart Home Assistant

### Manual

1. Copy the `custom_components/eyeonwater` folder to your Home Assistant `config/custom_components/` directory
2. Restart Home Assistant

## Setup

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **EyeOnWater**
3. Enter your EyeOnWater email and password (same credentials as the [EyeOnWater](https://eyeonwater.com/) website or mobile app)
4. The integration will create a device with two sensors

## Energy Dashboard

To track water usage on the Energy dashboard:

1. Go to **Settings > Dashboards > Energy > Water consumption**
2. Click **Add water source**
3. Select `sensor.eyeonwater_meter_current_reading`
4. It may take up to 2 hours for data to appear

## Notes

- When you first install this app, it might not show water usage under "Energy" in the dashboard. Wait an hour and it should update with real usage.
- It's common for a tiny amount of water to be used when you're not in the house, such as 0.06 gallons per day.

## Requirements

- An [EyeOnWater](https://eyeonwater.com) account with at least one water meter
- Home Assistant 2024.1 or later
