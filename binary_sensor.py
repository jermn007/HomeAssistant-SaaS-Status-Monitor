from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

DEGRADED_STATES = {"degraded", "partial_outage", "major_outage", "maintenance", "unknown"}

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([StatusDegradedBinarySensor(coordinator, entry)])

class StatusDegradedBinarySensor(CoordinatorEntity, BinarySensorEntity):
    _attr_device_class = BinarySensorDeviceClass.PROBLEM
    _attr_icon = "mdi:alert-circle"

    def __init__(self, coordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_name = "Status Degraded"
        self._attr_unique_id = f"{entry.entry_id}_degraded"

    @property
    def is_on(self):
        return (self.coordinator.data.get("overall") or "unknown") in DEGRADED_STATES

    @property
    def extra_state_attributes(self):
        return {
            "overall": self.coordinator.data.get("overall"),
            "raw_status": self.coordinator.data.get("overall_raw"),
        }
