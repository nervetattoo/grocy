"""Binary sensor platform for grocy."""
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.helpers.dispatcher import (
    async_dispatcher_connect,
    async_dispatcher_send,
)
from homeassistant.core import callback

from .const import (
    ATTRIBUTION,
    BINARY_SENSOR_TYPES,
    EXPIRING_PRODUCTS_NAME,
    EXPIRED_PRODUCTS_NAME,
    MISSING_PRODUCTS_NAME,
    DEFAULT_CONF_NAME,
    DOMAIN,
    LOGGER,
    STOCK_NAME,
    NEW_BINARY_SENSOR,
    NEW_SENSOR,
)


async def async_setup_platform(
    hass, config, async_add_entities, discovery_info=None
):  # pylint: disable=unused-argument
    """Setup binary_sensor platform."""
    # async_add_entities([GrocyBinarySensor(hass, discovery_info)], True)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Setup sensor platform."""
    instance = hass.data[DOMAIN]["instance"]

    @callback
    def async_add_binary_sensor(binary_sensors):
        LOGGER.debug("Adding binary sensors")
        LOGGER.debug(binary_sensors)
        for binary_sensor in binary_sensors:
            if instance.option_allow_stock and binary_sensor.startswith(
                EXPIRING_PRODUCTS_NAME
            ):
                device_name = STOCK_NAME
                async_add_entities(
                    [GrocyBinarySensor(hass, binary_sensor, device_name)], True
                )
            elif instance.option_allow_stock and binary_sensor.startswith(
                EXPIRED_PRODUCTS_NAME
            ):
                device_name = STOCK_NAME
                async_add_entities(
                    [GrocyBinarySensor(hass, binary_sensor, device_name)], True
                )
            elif instance.option_allow_stock and binary_sensor.startswith(
                MISSING_PRODUCTS_NAME
            ):
                device_name = STOCK_NAME
                async_add_entities(
                    [GrocyBinarySensor(hass, binary_sensor, device_name)], True
                )

    instance.listeners.append(
        async_dispatcher_connect(
            hass,
            instance.async_signal_new_entity(NEW_BINARY_SENSOR),
            async_add_binary_sensor,
        )
    )

    async_add_binary_sensor(BINARY_SENSOR_TYPES)


class GrocyBinarySensor(BinarySensorEntity):
    """grocy binary_sensor class."""

    def __init__(self, hass, sensor_type, device_name):
        self.hass = hass
        self.sensor_type = sensor_type
        self.device_name = device_name
        self.attr = {}
        self._status = False
        self._hash_key = self.hass.data[DOMAIN].get("hash_key")
        self._unique_id = "{}-{}".format(self._hash_key, self.sensor_type)
        self._name = "{}.{}".format(DEFAULT_CONF_NAME, self.sensor_type)
        self._client = self.hass.data[DOMAIN]["client"]

    async def async_update(self):
        """Update the binary_sensor."""
        # Send update "signal" to the component
        await self._client.async_update_data(self.sensor_type)

        self.attr["items"] = [
            x.as_dict() for x in self.hass.data[DOMAIN].get(self.sensor_type, [])
        ]
        self._status = len(self.attr["items"]) != 0
        # LOGGER.debug(self.attr)
        LOGGER.debug(self.device_info)

    @property
    def unique_id(self):
        """Return a unique ID to use for this binary_sensor."""
        return self._unique_id

    @property
    def device_info(self):
        return {
            "identifiers": {(DOMAIN, self.device_name)},
            "name": self.device_name,
            "manufacturer": "Grocy",
            "entry_type": "service",
        }

    @property
    def name(self):
        """Return the name of the binary_sensor."""
        return self._name

    @property
    def device_class(self):
        """Return the class of this binary_sensor."""
        return None

    @property
    def is_on(self):
        """Return true if the binary_sensor is on."""
        return self._status

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self.attr

