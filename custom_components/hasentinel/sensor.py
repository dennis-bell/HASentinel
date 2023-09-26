import logging
from datetime import datetime, timezone
from homeassistant.helpers.entity import Entity

DOMAIN = 'hasentinel'
_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the HASentinel sensors."""
    if DOMAIN not in hass.data:
        return

    entities = []
    for entity_id, data in hass.data[DOMAIN].items():
        entities.append(HASentinelSensor(entity_id, data))
    
    add_entities(entities, True)

class HASentinelSensor(Entity):
    """Representation of a HASentinel Sensor."""

    def __init__(self, entity_id, data):
        """Initialize the sensor."""
        self._entity_id = entity_id
        self._data = data
        self._last_seen = data.get("last_seen")
        self._urgency = data.get("urgency_level")
        self._reported = data.get("reported")

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"HASentinel {self._entity_id}"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._last_seen

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"hasentinel_{self._entity_id}"

    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        return {
            'urgency_level': self._urgency,
            'reported': self._reported,
        }

    def update(self):
        """Fetch new data for this entity."""
        self._data = self.hass.data[DOMAIN].get(self._entity_id)
        self._last_seen = self._data.get("last_seen")
        self._urgency = self._data.get("urgency_level")
        self._reported = self._data.get("reported")
