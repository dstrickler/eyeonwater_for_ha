"""DataUpdateCoordinator for EyeOnWater."""
from __future__ import annotations

from datetime import timedelta
import logging

import aiohttp
from pyonwater import Account, Client

from homeassistant.core import HomeAssistant
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_HOSTNAME, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class EyeOnWaterData:
    """Parsed data from EyeOnWater API."""

    def __init__(self):
        self.meter_id: str = "unknown"
        self.current_reading: float | None = None
        self.reading_timestamp: str | None = None
        self.unit: str = "gal"
        self.usage_period: float = 0.0
        self.data_points: int = 0
        self.historical_data: list[dict] = []
        self.alert_active: bool = False


class EyeOnWaterCoordinator(DataUpdateCoordinator[EyeOnWaterData]):
    """Coordinator to fetch data from EyeOnWater API."""

    config_entry: ConfigEntry

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="EyeOnWater",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self._username = entry.data[CONF_USERNAME]
        self._password = entry.data[CONF_PASSWORD]
        self._hostname = entry.data.get(CONF_HOSTNAME, "eyeonwater.com")

    async def _async_update_data(self) -> EyeOnWaterData:
        """Fetch data from EyeOnWater."""
        try:
            account = Account(
                eow_hostname=self._hostname,
                username=self._username,
                password=self._password,
            )

            async with aiohttp.ClientSession() as session:
                client = Client(session, account)
                await client.authenticate()
                meters = await account.fetch_meters(client)

                if not meters:
                    raise UpdateFailed("No meters found on account")

                meter = meters[0]
                await meter.read_meter_info(client=client)
                historical_data = await meter.read_historical_data(
                    client=client, days_to_load=3
                )

            data = EyeOnWaterData()
            data.meter_id = str(meter.meter_id) if hasattr(meter, "meter_id") else "unknown"

            # Determine unit
            if historical_data and len(historical_data) > 0:
                data.unit = str(historical_data[0].unit).replace("NativeUnits.", "")

            # Current reading
            if hasattr(meter, "current_read") and meter.current_read:
                data.current_reading = float(meter.current_read.reading)
                data.reading_timestamp = meter.current_read.dt.isoformat()

            # Historical data
            data.historical_data = [
                {
                    "timestamp": dp.dt.isoformat(),
                    "reading": float(dp.reading),
                    "unit": data.unit,
                }
                for dp in historical_data
            ]

            # Usage over period
            if len(data.historical_data) >= 2:
                data.usage_period = round(
                    data.historical_data[-1]["reading"]
                    - data.historical_data[0]["reading"],
                    2,
                )

            data.data_points = len(data.historical_data)
            data.alert_active = hasattr(meter, "alert") and meter.alert is not None

            return data

        except UpdateFailed:
            raise
        except Exception as err:
            raise UpdateFailed(f"Error communicating with EyeOnWater: {err}") from err
