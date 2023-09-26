import logging
import datetime
import sqlite3
import voluptuous as vol
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'hasentinel'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        'entities': vol.All(cv.ensure_list, [{
            vol.Required('entity_id'): cv.entity_id,
            vol.Required('urgency'): cv.string
        }])
    })
}, extra=vol.ALLOW_EXTRA)

def setup(hass, config):
    """Set up the HASentinel component."""
    conf = config[DOMAIN]
    entities = conf.get('entities')

    urgency_to_minutes = {
        'low': 7*24*60,   # 1 week
        'medium': 48*60,  # 48 hours
        'high': 60        # 1 hour (For testing purposes, change this back to 24*60 for production)
    }

    conn = sqlite3.connect('/config/hasentinel.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS entity_states (
            entity_id TEXT PRIMARY KEY,
            device_id TEXT,
            last_seen TEXT,
            urgency_level TEXT,
            reported INTEGER
        )
    ''')

    def check_entities(now):
        """Routine to check entities' availability."""
        for entity in entities:
            entity_id = entity['entity_id']
            urgency = entity['urgency']

            state = hass.states.get(entity_id)

            if not state:
                _LOGGER.error(f"Error fetching state for {entity_id}")
                continue

            last_seen_attribute = state.attributes.get("last_seen")
            current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute("SELECT last_seen, reported FROM entity_states WHERE entity_id = ?", (entity_id,))
            record = cursor.fetchone()

            if last_seen_attribute:
                last_seen_dt = datetime.datetime.fromisoformat(last_seen_attribute.replace('Z', '+00:00'))
            elif record:
                last_seen_dt = datetime.datetime.strptime(record[0], '%Y-%m-%d %H:%M:%S')
            else:
                last_seen_dt = datetime.datetime.now()

            delta = datetime.datetime.now() - last_seen_dt

            if state.state != "unavailable" or (last_seen_attribute and delta.total_seconds() <= urgency_to_minutes[urgency] * 60):
                if record:
                    cursor.execute("UPDATE entity_states SET last_seen = ?, reported = 0 WHERE entity_id = ?", (current_time, entity_id))
                else:
                    cursor.execute("INSERT INTO entity_states (entity_id, device_id, last_seen, urgency_level, reported) VALUES (?, ?, ?, ?, 0)", 
                                (entity_id, state.attributes.get("device_id", ""), current_time, urgency))
            else:
                if record and delta.total_seconds() > urgency_to_minutes[urgency] * 60 and record[1] == 0:
                    cursor.execute("UPDATE entity_states SET reported = 1 WHERE entity_id = ?", (entity_id,))
            conn.commit()

    # Set up the routine to run every minute
    async_track_time_interval(hass, check_entities, datetime.timedelta(minutes=1))

    return True
