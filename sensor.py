from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import StatusCoordinator

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    coordinator: StatusCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [OverallStatusSensor(coordinator, entry)]
    for comp in coordinator.data.get("components", []):
        entities.append(ComponentStatusSensor(coordinator, entry, comp["name"]))
    async_add_entities(entities)

class OverallStatusSensor(CoordinatorEntity[StatusCoordinator], SensorEntity):
    _attr_name = "Status Overall"
    _attr_icon = "mdi:cloud-check-variant"

    def __init__(self, coordinator: StatusCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_overall"

    @property
    def native_value(self):
        return self.coordinator.data.get("overall")

    @property
    def extra_state_attributes(self):
        last_refresh = getattr(self.coordinator, "last_update_success_time", None)
        last_success = getattr(self.coordinator, "last_update_success", None)
        return {
            "raw_status": self.coordinator.data.get("overall_raw"),
            "severity": self.coordinator.data.get("severity"),
            "components": len(self.coordinator.data.get("components", [])),
            "last_refresh": last_refresh.isoformat() if last_refresh else None,
            "last_update_success": last_success,
            "last_update_success_time": last_refresh.isoformat() if last_refresh else None,
        }

class ComponentStatusSensor(CoordinatorEntity[StatusCoordinator], SensorEntity):
    _attr_icon = "mdi:checkbox-blank-circle-outline"

    def __init__(self, coordinator: StatusCoordinator, entry: ConfigEntry, comp_name: str):
        super().__init__(coordinator)
        self._comp_name = comp_name
        self._attr_name = f"Status {comp_name}"
        self._attr_unique_id = f"{entry.entry_id}_comp_{comp_name}"

    @property
    def native_value(self):
        comp = self._find()
        return comp.get("status") if comp else None

    @property
    def extra_state_attributes(self):
        comp = self._find()
        last_refresh = getattr(self.coordinator, "last_update_success_time", None)
        last_success = getattr(self.coordinator, "last_update_success", None)
        return {
            **(comp or {}),
            "last_refresh": last_refresh.isoformat() if last_refresh else None,
            "last_update_success": last_success,
            "last_update_success_time": last_refresh.isoformat() if last_refresh else None,
        }

    def _find(self):
        for comp in self.coordinator.data.get("components", []):
            if comp.get("name") == self._comp_name:
                return comp
        return None
