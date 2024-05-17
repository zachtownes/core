"""Support for the Tandoor Meal Plan Integration."""

from __future__ import annotations

import datetime
import logging

import requests
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA, SensorEntity
from homeassistant.const import CONF_API_KEY, CONF_TIME_ZONE, CONF_URL
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .tandoor import Tandoor

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = datetime.timedelta(hours=1)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_URL): cv.string,
        vol.Required(CONF_API_KEY): cv.string,
        vol.Optional(CONF_TIME_ZONE, default="US/Mountain"): cv.string,
    }
)

SENSOR_TYPE = "recipe_id"
SENSOR_ROUNDING_PRECISION = 1
SENSOR_ATTRS = [
    "recipe_name",
    "note",
    "recipe_id",
    "recipe_image",
    "servings",
    "recipe_url",
]


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the Tandoor Mealplan sensor."""

    url = config[CONF_URL]
    api_key = config[CONF_API_KEY]
    time_zone = config[CONF_TIME_ZONE]
    _LOGGER.debug(time_zone)

    try:
        test = Tandoor.tandoor_test(url, api_key)
    except requests.exceptions.HTTPError as http_error:
        if http_error.response.status_code in (requests.codes.unauthorized,):
            _LOGGER.error("Bad API Key for Tandoor")
        elif http_error.response.status_code in (requests.codes.not_found,):
            _LOGGER.error("Unable to get to Tandoor")
        else:
            raise

    all_sensors = []
    if test:
        all_sensors.append(MealPlanSensor(url, api_key, time_zone))
    add_entities(all_sensors, True)


class MealPlanSensor(SensorEntity):
    """Representation of a Tandoor MealPlan sensor."""

    def __init__(self, url, api_key, time_zone) -> None:
        """Initialize the sensor."""
        self._url = url
        self._api_key = api_key
        self._time_zone = time_zone
        self._name = f"Tandoor_{self._url}"
        self._state = None
        self._attributes = None

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def attributes(self):
        """Return the meal plan identifier."""
        return self._attributes

    def get_data(self, url, api_key, time_zone):
        """Get data from the meal plan.

        Flatten dictionary to map meal plan to map of meal plan data.

        """
        _LOGGER.debug(url)
        _LOGGER.debug(api_key)
        try:
            data = Tandoor.get_today_meal_plan(url, api_key, time_zone)
        except requests.exceptions.HTTPError as http_error:
            if http_error.response.status_code in (requests.codes.unauthorized,):
                _LOGGER.error("Bad API Key for Tandoor")
            elif http_error.response.status_code in (requests.codes.not_found,):
                _LOGGER.error("Unable to get to Tandoor")
            else:
                raise
        _LOGGER.debug(data)
        return data

    def update(self) -> None:
        """Set the device state and attributes."""
        _LOGGER.debug(self._url)
        _LOGGER.debug(self._api_key)
        data = self.get_data(self._url, self._api_key, self._time_zone)
        _LOGGER.debug(data[SENSOR_TYPE])
        self._state = round(data[SENSOR_TYPE], SENSOR_ROUNDING_PRECISION)
        # self._attributes = {k: v for k, v in data.items() if k in SENSOR_ATTRS}
