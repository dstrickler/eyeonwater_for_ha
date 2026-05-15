"""Sensor platform for EyeOnWater."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import EyeOnWaterCoordinator, EyeOnWaterData


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EyeOnWater sensors from a config entry."""
    coordinator: EyeOnWaterCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            EyeOnWaterCurrentReading(coordinator, entry),
            EyeOnWaterUsage(coordinator, entry),
        ]
    )


class EyeOnWaterSensorBase(CoordinatorEntity[EyeOnWaterCoordinator], SensorEntity):
    """Base class for EyeOnWater sensors."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: EyeOnWaterCoordinator, entry: ConfigEntry
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "EyeOnWater Meter",
            "manufacturer": "EyeOnWater",
            "model": "Water Meter",
        }

    @property
    def _data(self) -> EyeOnWaterData | None:
        return self.coordinator.data


class EyeOnWaterCurrentReading(EyeOnWaterSensorBase):
    """Current meter reading sensor."""

    _attr_name = "Current Reading"
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.TOTAL_INCREASING
    _attr_native_unit_of_measurement = UnitOfVolume.GALLONS
    _attr_icon = "mdi:water"

    def __init__(
        self, coordinator: EyeOnWaterCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_current_reading"

    @property
    def native_value(self) -> float | None:
        if self._data is None:
            return None
        return self._data.current_reading

    @property
    def extra_state_attributes(self) -> dict:
        if self._data is None:
            return {}
        return {
            "meter_id": self._data.meter_id,
            "reading_timestamp": self._data.reading_timestamp,
            "unit": self._data.unit,
            "alert_active": self._data.alert_active,
        }


class EyeOnWaterUsage(EyeOnWaterSensorBase):
    """Water usage over the fetched period."""

    _attr_name = "Usage (3 day)"
    _attr_device_class = SensorDeviceClass.WATER
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfVolume.GALLONS
    _attr_icon = "mdi:water-pump"

    def __init__(
        self, coordinator: EyeOnWaterCoordinator, entry: ConfigEntry
    ) -> None:
        super().__init__(coordinator, entry)
        self._attr_unique_id = f"{entry.entry_id}_usage"

    @property
    def native_value(self) -> float | None:
        if self._data is None:
            return None
        return self._data.usage_period

    @property
    def extra_state_attributes(self) -> dict:
        if self._data is None:
            return {}
        return {
            "data_points": self._data.data_points,
            "historical_data": self._data.historical_data[-24:],
        }
