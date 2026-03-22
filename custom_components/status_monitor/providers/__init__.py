from __future__ import annotations

import abc
from typing import Any, Dict, List, Optional

import aiohttp
import jmespath

from homeassistant.const import CONF_TIMEOUT, CONF_VERIFY_SSL
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from ..const import (
    CONF_COMPONENTS_ENDPOINT,
    CONF_COMPONENTS_PATH,
    CONF_COMPONENT_NAME_PATH,
    CONF_COMPONENT_STATUS_PATH,
    CONF_ENDPOINT,
    CONF_HEADERS,
    CONF_PROVIDER,
    CONF_STATUS_MAP,
    CONF_STATUS_PATH,
    SEVERITY_ORDER,
    PROVIDERS,
)

class BaseProvider(abc.ABC):
    def __init__(self, name: str, session: aiohttp.ClientSession, config: Dict[str, Any]):
        self.name = name
        self.session = session
        self.config = config

    @abc.abstractmethod
    async def async_fetch(self) -> Dict[str, Any]:
        ...

    def _normalize_status(self, raw: str, status_map: Dict[str, str]) -> str:
        return status_map.get(raw, raw if raw in SEVERITY_ORDER else "unknown")

    def _severity(self, status: str) -> int:
        return SEVERITY_ORDER.index(status) if status in SEVERITY_ORDER else len(SEVERITY_ORDER)

class StatuspageProvider(BaseProvider):
    async def async_fetch(self) -> Dict[str, Any]:
        base = self.config[CONF_ENDPOINT].rstrip("/")
        headers = self.config.get(CONF_HEADERS) or {}
        verify_ssl = self.config.get(CONF_VERIFY_SSL, True)

        async with self.session.get(base, headers=headers, ssl=verify_ssl) as resp:
            resp.raise_for_status()
            status_json = await resp.json()

        # optional components endpoint
        components_endpoint = self.config.get(CONF_COMPONENTS_ENDPOINT)
        components = []
        if components_endpoint:
            async with self.session.get(components_endpoint, headers=headers, ssl=verify_ssl) as resp2:
                resp2.raise_for_status()
                comp_json = await resp2.json()
                components = comp_json.get("components", [])

        default_map = PROVIDERS.get("statuspage", {}).get("status_map", {})
        map_cfg = {**default_map, **(self.config.get(CONF_STATUS_MAP) or {})}
        overall_raw = jmespath.search("status.indicator", status_json)
        overall = self._normalize_status(overall_raw, map_cfg)

        normalized_components = []
        for c in components:
            normalized_components.append(
                {
                    "id": c.get("id"),
                    "name": c.get("name"),
                    "raw_status": c.get("status"),
                    "status": self._normalize_status(c.get("status"), map_cfg),
                }
            )

        return {
            "overall": overall,
            "overall_raw": overall_raw,
            "severity": self._severity(overall),
            "components": normalized_components,
            "raw": status_json,
        }

class GenericProvider(BaseProvider):
    async def async_fetch(self) -> Dict[str, Any]:
        headers = self.config.get(CONF_HEADERS) or {}
        verify_ssl = self.config.get(CONF_VERIFY_SSL, True)
        async with self.session.get(self.config[CONF_ENDPOINT], headers=headers, ssl=verify_ssl) as resp:
            resp.raise_for_status()
            data = await resp.json()

        status_path = self.config[CONF_STATUS_PATH]
        components_path = self.config.get(CONF_COMPONENTS_PATH)
        name_path = self.config.get(CONF_COMPONENT_NAME_PATH)
        status_field_path = self.config.get(CONF_COMPONENT_STATUS_PATH)
        map_cfg = self.config.get(CONF_STATUS_MAP, {})

        overall_raw = jmespath.search(status_path, data)
        overall = self._normalize_status(overall_raw, map_cfg)

        normalized_components = []
        if components_path and name_path and status_field_path:
            for comp in jmespath.search(components_path, data) or []:
                raw_status = jmespath.search(status_field_path, comp)
                normalized_components.append(
                    {
                        "id": comp.get("id"),
                        "name": jmespath.search(name_path, comp),
                        "raw_status": raw_status,
                        "status": self._normalize_status(raw_status, map_cfg),
                    }
                )

        return {
            "overall": overall,
            "overall_raw": overall_raw,
            "severity": self._severity(overall),
            "components": normalized_components,
            "raw": data,
        }

def get_provider(provider_key: str, config: Dict[str, Any], session: aiohttp.ClientSession) -> BaseProvider:
    if provider_key == "statuspage":
        return StatuspageProvider("statuspage", session, config)
    return GenericProvider("generic", session, config)
