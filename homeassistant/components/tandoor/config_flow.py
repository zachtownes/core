"""Config flow for Tandoor Meal Plan Integration integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_API_KEY, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN
from .tandoor import Tandoor

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {vol.Required(CONF_URL): str, vol.Required(CONF_API_KEY): str}
)


class PlaceholderHub:
    """Placeholder class to test authentication."""

    def __init__(self, url: str, api_key: str) -> None:
        """Initialize."""
        self.url = url
        self.api_key = api_key

    async def authenticate(self, url, api_key) -> bool:
        """Test if we can authenticate with the host."""
        tandoor = Tandoor(url, api_key)
        return await tandoor.tandoor_test(url, api_key)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    hub = PlaceholderHub(data[CONF_URL], data[CONF_API_KEY])

    if not await hub.authenticate(data[CONF_URL], data[CONF_API_KEY]):
        raise InvalidAuth

    # If you cannot connect:
    # throw CannotConnect
    # If the authentication is wrong:
    # InvalidAuth

    # Return info that you want to store in the config entry.
    return {"title": f"Tandoor_{hub.url}"}


class TandoorConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tandoor Meal Plan Integration."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
