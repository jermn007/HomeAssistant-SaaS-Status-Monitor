from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Dict, List, Optional

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util

from .providers import BaseProvider

_LOGGER = logging.getLogger(__name__)

class StatusCoordinator(DataUpdateCoordinator[Dict[str, Any]]):
    def __init__(self, hass: HomeAssistant, provider: BaseProvider, name: str, update_interval: timedelta):
        super().__init__(hass, _LOGGER, name=name, update_interval=update_interval)
        self.provider = provider
        self.last_update_success_time = None

    async def _async_update_data(self) -> Dict[str, Any]:
        try:
            data = await self.provider.async_fetch()
            self.last_update_success_time = dt_util.utcnow()
            _LOGGER.debug(
                "Status update succeeded for %s: overall=%s components=%s",
                self.name,
                data.get("overall"),
                len(data.get("components", [])),
            )
            return data
        except Exception as err:
            _LOGGER.debug("Status update failed for %s", self.name, exc_info=err)
            raise UpdateFailed(str(err)) from err
