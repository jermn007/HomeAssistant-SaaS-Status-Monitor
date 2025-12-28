# SaaS Status Monitor

SaaS Status Monitor is a custom Home Assistant integration that polls SaaS status pages (Statuspage.io or any JSON endpoint) and exposes normalized status entities for automations.

## Features
- Polls status endpoints every 5-15 minutes (configurable).
- Supports Atlassian Statuspage (status + components) and generic JSON with JMESPath extraction.
- Creates an overall status sensor, component sensors, and a degraded binary sensor.
- Adds debug logging and last refresh attributes for verification.
- Optional automation blueprint for light/voice alerts.

## Installation
1. Copy `custom_components/status_monitor` into `/config/custom_components/status_monitor`.
2. Restart Home Assistant.
3. Add "SaaS Status Monitor" from Settings > Devices & Services.

## Configuration (UI)
- Provider: `statuspage` or `generic`.
- Status endpoint URL (and optional components endpoint).
- Optional headers (JSON), verify SSL, polling interval.
- For generic provider, provide JMESPath expressions for status and components fields.
- Optional status map (JSON) to normalize values.

## Entities
- `sensor.<platform>_status_overall` - normalized overall status.
- `sensor.status_<component>` - status per component (if components are available).
- `binary_sensor.<entry_name>_degraded` - on when overall status is degraded/partial/major/maintenance/unknown.

Attributes include `last_refresh`, `last_update_success`, and `last_update_success_time`.

## Blueprint
The repo includes `blueprint/notify_on_degrade.yaml` for light/voice alerts. Import it into HA (Settings > Automations & Scenes > Blueprints) or copy it into `/config/blueprints/automation/`.

## Troubleshooting
- Enable debug logging for `custom_components.status_monitor` to see polling logs.
- If sensors are unavailable, check endpoint reachability and JSON path settings.

## Limitations
This integration requires JSON endpoints reachable by Home Assistant and currently supports auth via headers only.

## Tested with
- `https://status.xyleme.com` (Statuspage)
- `https://status.kaltura.com` (Statuspage)
