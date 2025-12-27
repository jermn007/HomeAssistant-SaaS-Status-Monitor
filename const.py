DOMAIN = "status_monitor"
CONF_PROVIDER = "provider"
CONF_ENDPOINT = "endpoint"
CONF_COMPONENTS_ENDPOINT = "components_endpoint"
CONF_INTERVAL = "interval"
CONF_HEADERS = "headers"
CONF_VERIFY_SSL = "verify_ssl"
CONF_STATUS_PATH = "status_path"
CONF_COMPONENTS_PATH = "components_path"
CONF_COMPONENT_NAME_PATH = "component_name_path"
CONF_COMPONENT_STATUS_PATH = "component_status_path"
CONF_STATUS_MAP = "status_map"

DEFAULT_INTERVAL = 300  # 5 minutes
MIN_INTERVAL = 300
MAX_INTERVAL = 900  # 15 minutes

PROVIDERS = {
    "statuspage": {
        "name": "Atlassian Statuspage",
        "status_endpoint": "/api/v2/status.json",
        "components_endpoint": "/api/v2/components.json",
        "status_path": "status.indicator",
        "component_list_path": "components",
        "component_name_path": "name",
        "component_status_path": "status",
        "status_map": {
            "none": "operational",
            "operational": "operational",
            "under_maintenance": "maintenance",
            "degraded_performance": "degraded",
            "partial_outage": "partial_outage",
            "major_outage": "major_outage"
        }
    }
}

SEVERITY_ORDER = ["operational", "maintenance", "degraded", "partial_outage", "major_outage", "unknown"]
