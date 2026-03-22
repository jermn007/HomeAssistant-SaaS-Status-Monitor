from __future__ import annotations

import asyncio
import logging
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_COMPONENTS_ENDPOINT,
    CONF_ENDPOINT,
    CONF_INTERVAL,
    CONF_PROVIDER,
    CONF_STATUS_MAP,
    DOMAIN,
    MIN_INTERVAL,
)
from .coordinator import StatusCoordinator
from .providers import get_provider

PLATFORMS = ["sensor", "binary_sensor"]
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    provider = get_provider(entry.data[CONF_PROVIDER], entry.data, async_get_clientsession(hass))
    coordinator = StatusCoordinator(
        hass,
        provider=provider,
        name=entry.title,
        update_interval=timedelta(seconds=max(MIN_INTERVAL, entry.options.get(CONF_INTERVAL, entry.data.get(CONF_INTERVAL)))),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(_async_options_updated))
    return True

async def _async_options_updated(hass: HomeAssistant, entry: ConfigEntry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok
