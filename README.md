# ha-itra — ITRA Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A HACS-compatible custom integration for [Home Assistant](https://www.home-assistant.io/) that periodically scrapes the public **ITRA RunnerSpace** profile page of a runner and exposes two sensors:

| Entity | State | Example |
|---|---|---|
| `sensor.itra_level_count` | ITRA index (integer) | `388` |
| `sensor.itra_performance_level` | Performance level (string) | `"Intermediate 4"` |

---

## ⚠️ Legal / Ethical Notice

This integration **scrapes HTML** from `itra.run`.  Please review the ITRA
[Terms of Service](https://itra.run) and their `robots.txt` before using it.
Scraping may violate ToS.  If ITRA ever provides an official public API, prefer
that over HTML scraping.

The default polling interval is **4 hours** (minimum enforced: 3 hours) to
avoid putting unnecessary load on their servers.  Please be a polite consumer.

---

## Installation

### Via HACS (recommended)

1. Open HACS → Integrations → **⋮ → Custom repositories**.
2. Add `https://github.com/CrunkA3/ha-itra` as an **Integration** repository.
3. Search for **ITRA** and click *Download*.
4. Restart Home Assistant.

### Manual

1. Copy the `custom_components/itra/` folder into your HA
   `config/custom_components/` directory.
2. Restart Home Assistant.

---

## Configuration

### Via the UI (recommended)

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **ITRA**.
3. Enter the fields:

| Field | Description | Example |
|---|---|---|
| Runner URL | Full ITRA RunnerSpace URL | `https://itra.run/RunnerSpace/rohrhirsch.michael.5685748` |
| Update interval | Polling interval in seconds (min 10 800 = 3 h) | `14400` |
| User-Agent | Custom HTTP User-Agent (optional) | _(leave empty for default)_ |

### Via YAML

YAML-based setup is not supported for this integration. Please use the UI (Config Flow) to configure the runner URL and polling interval.

---

## Entities

After a successful setup, the following entities are created:

```
sensor.itra_level_count          → 388      (ITRA index integer)
sensor.itra_performance_level    → "Intermediate 4"   (performance level string)
```

The `sensor.itra_performance_level` entity exposes these extra attributes:

| Attribute | Description |
|---|---|
| `raw_html_snippet` | The raw HTML fragment containing the parsed elements |
| `last_updated_by_coordinator` | ISO-8601 timestamp of the last successful update |

---

## Automation Example

```yaml
automation:
  - alias: "Notify on new ITRA level"
    trigger:
      - platform: state
        entity_id: sensor.itra_performance_level
    action:
      - service: notify.mobile_app_my_phone
        data:
          message: "Your ITRA level changed to {{ states('sensor.itra_performance_level') }}!"
```

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Sensors show `unavailable` | Check HA logs for network errors; verify the runner URL is accessible |
| `level_count` is `None` | ITRA may have changed their page layout; open a GitHub issue |
| `level` shows `unknown` | Same as above |
| Integration not loading | Ensure `beautifulsoup4` is installed (HA installs it automatically via `manifest.json`) |

### Logs

Enable debug logging in `configuration.yaml`:

```yaml
logger:
  default: warning
  logs:
    custom_components.itra: debug
```

---

## Development

```bash
# Install dependencies
pip install beautifulsoup4 pytest

# Run tests
pytest tests/
```

---

## License

MIT — see [LICENSE](LICENSE).