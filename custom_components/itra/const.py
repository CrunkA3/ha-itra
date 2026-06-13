"""Constants for the ITRA integration."""

DOMAIN = "itra"

# Configuration keys
CONF_RUNNER_URL = "runner_url"
CONF_UPDATE_INTERVAL = "update_interval"
CONF_USER_AGENT = "user_agent"

# Defaults
DEFAULT_UPDATE_INTERVAL = 14400  # 4 hours in seconds
MIN_UPDATE_INTERVAL = 10800  # 3 hours in seconds — polite minimum
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (compatible; ha-itra/1.0; +https://github.com/CrunkA3/ha-itra)"
)

# ITRA URL pattern
ITRA_RUNNER_URL_PREFIX = "https://itra.run/RunnerSpace/"

# HTML selectors
SELECTOR_LEVEL_COUNT = "span.level-count"
SELECTOR_LEVEL = "span.level"

# Sensor names / unique-id suffixes
SENSOR_LEVEL_COUNT = "level_count"
SENSOR_PERFORMANCE_LEVEL = "performance_level"

# Attribute keys for the performance-level sensor
ATTR_RAW_HTML_SNIPPET = "raw_html_snippet"
ATTR_LAST_UPDATED_BY_COORDINATOR = "last_updated_by_coordinator"
