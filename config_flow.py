from __future__ import annotations

import json

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_VERIFY_SSL
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_COMPONENTS_ENDPOINT,
    CONF_COMPONENTS_PATH,
    CONF_COMPONENT_NAME_PATH,
    CONF_COMPONENT_STATUS_PATH,
    CONF_ENDPOINT,
    CONF_HEADERS,
    CONF_INTERVAL,
    CONF_PROVIDER,
    CONF_STATUS_MAP,
    CONF_STATUS_PATH,
    DEFAULT_INTERVAL,
    DOMAIN,
    MAX_INTERVAL,
    MIN_INTERVAL,
)


def _parse_json_dict(value: str | dict | None) -> dict:
    if value in (None, ""):
        return {}
    if isinstance(value, dict):
        return value
    data = json.loads(value)
    if not isinstance(data, dict):
        raise ValueError("JSON must be an object")
    return data


def _to_json_text(value: str | dict | None) -> str:
    if value in (None, ""):
        return "{}"
    if isinstance(value, dict):
        return json.dumps(value)
    return value


class StatusMonitorConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        return StatusMonitorOptionsFlow(config_entry)

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input:
            try:
                headers = _parse_json_dict(user_input.get(CONF_HEADERS))
            except (ValueError, json.JSONDecodeError):
                errors[CONF_HEADERS] = "invalid_json"

            try:
                status_map = _parse_json_dict(user_input.get(CONF_STATUS_MAP))
            except (ValueError, json.JSONDecodeError):
                errors[CONF_STATUS_MAP] = "invalid_json"

            if not errors:
                return self.async_create_entry(
                    title=user_input[CONF_NAME],
                    data={
                        CONF_NAME: user_input[CONF_NAME],
                        CONF_PROVIDER: user_input[CONF_PROVIDER],
                        CONF_ENDPOINT: user_input[CONF_ENDPOINT],
                        CONF_COMPONENTS_ENDPOINT: user_input.get(CONF_COMPONENTS_ENDPOINT),
                        CONF_HEADERS: headers,
                        CONF_VERIFY_SSL: user_input.get(CONF_VERIFY_SSL, True),
                        CONF_INTERVAL: user_input.get(CONF_INTERVAL, DEFAULT_INTERVAL),
                        CONF_STATUS_PATH: user_input.get(CONF_STATUS_PATH),
                        CONF_COMPONENTS_PATH: user_input.get(CONF_COMPONENTS_PATH),
                        CONF_COMPONENT_NAME_PATH: user_input.get(CONF_COMPONENT_NAME_PATH),
                        CONF_COMPONENT_STATUS_PATH: user_input.get(CONF_COMPONENT_STATUS_PATH),
                        CONF_STATUS_MAP: status_map,
                    },
                )

        provider_options = ["statuspage", "generic"]
        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=user_input.get(CONF_NAME, "Service Status") if user_input else "Service Status"): str,
                vol.Required(CONF_PROVIDER, default=user_input.get(CONF_PROVIDER, "statuspage") if user_input else "statuspage"): vol.In(provider_options),
                vol.Required(
                    CONF_ENDPOINT,
                    default=user_input.get(CONF_ENDPOINT, "https://status.xyleme.com/api/v2/status.json") if user_input else "https://status.xyleme.com/api/v2/status.json",
                ): str,
                vol.Optional(
                    CONF_COMPONENTS_ENDPOINT,
                    default=user_input.get(CONF_COMPONENTS_ENDPOINT, "https://status.xyleme.com/api/v2/components.json") if user_input else "https://status.xyleme.com/api/v2/components.json",
                ): str,
                vol.Optional(
                    CONF_HEADERS,
                    default=_to_json_text(user_input.get(CONF_HEADERS)) if user_input else "{}",
                ): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
                vol.Optional(CONF_VERIFY_SSL, default=user_input.get(CONF_VERIFY_SSL, True) if user_input else True): bool,
                vol.Optional(CONF_INTERVAL, default=user_input.get(CONF_INTERVAL, DEFAULT_INTERVAL) if user_input else DEFAULT_INTERVAL): vol.All(
                    int, vol.Clamp(min=MIN_INTERVAL, max=MAX_INTERVAL)
                ),
                # Generic extraction paths
                vol.Optional(CONF_STATUS_PATH, default=user_input.get(CONF_STATUS_PATH, "status.indicator") if user_input else "status.indicator"): str,
                vol.Optional(CONF_COMPONENTS_PATH, default=user_input.get(CONF_COMPONENTS_PATH, "components") if user_input else "components"): str,
                vol.Optional(CONF_COMPONENT_NAME_PATH, default=user_input.get(CONF_COMPONENT_NAME_PATH, "name") if user_input else "name"): str,
                vol.Optional(CONF_COMPONENT_STATUS_PATH, default=user_input.get(CONF_COMPONENT_STATUS_PATH, "status") if user_input else "status"): str,
                vol.Optional(
                    CONF_STATUS_MAP,
                    default=_to_json_text(user_input.get(CONF_STATUS_MAP)) if user_input else "{}",
                ): selector.TextSelector(selector.TextSelectorConfig(multiline=True)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def async_step_import(self, user_input) -> FlowResult:
        return await self.async_step_user(user_input)


class StatusMonitorOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema(
            {
                vol.Optional(
                    CONF_INTERVAL,
                    default=self.config_entry.options.get(CONF_INTERVAL, DEFAULT_INTERVAL),
                ): vol.All(int, vol.Clamp(min=MIN_INTERVAL, max=MAX_INTERVAL)),
                vol.Optional(
                    CONF_VERIFY_SSL,
                    default=self.config_entry.options.get(CONF_VERIFY_SSL, True),
                ): bool,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
