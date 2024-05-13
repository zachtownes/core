"""Test the Tandoor Meal Plan Integration config flow."""

from unittest.mock import AsyncMock, patch

from homeassistant import config_entries
from homeassistant.components.tandoor.config_flow import CannotConnect, InvalidAuth
from homeassistant.components.tandoor.const import DOMAIN
from homeassistant.const import CONF_API_KEY, CONF_URL
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType


async def test_form(hass: HomeAssistant, mock_setup_entry: AsyncMock) -> None:
    """Test we get the form."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    with patch(
        "homeassistant.components.tandoor.config_flow.PlaceholderHub.authenticate",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_URL: "https://recipes.mysticturtles.com",
                CONF_API_KEY: "tda_063614b3_af4f_4be5_83e4_56e0d1fa869d",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Tandoor_https://recipes.mysticturtles.com"
    assert result["data"] == {
        CONF_URL: "https://recipes.mysticturtles.com",
        CONF_API_KEY: "tda_063614b3_af4f_4be5_83e4_56e0d1fa869d",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.tandoor.config_flow.PlaceholderHub.authenticate",
        side_effect=InvalidAuth,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_URL: "https://recipes.mysticturtles.com",
                CONF_API_KEY: "tda",
            },
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "invalid_auth"}

    # Make sure the config flow tests finish with either an
    # FlowResultType.CREATE_ENTRY or FlowResultType.ABORT so
    # we can show the config flow is able to recover from an error.
    with patch(
        "homeassistant.components.tandoor.config_flow.PlaceholderHub.authenticate",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_URL: "https://recipes.mysticturtles.com",
                CONF_API_KEY: "tda_063614b3_af4f_4be5_83e4_56e0d1fa869d",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Tandoor_https://recipes.mysticturtles.com"
    assert result["data"] == {
        CONF_URL: "https://recipes.mysticturtles.com",
        CONF_API_KEY: "tda_063614b3_af4f_4be5_83e4_56e0d1fa869d",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_cannot_connect(
    hass: HomeAssistant, mock_setup_entry: AsyncMock
) -> None:
    """Test we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    with patch(
        "homeassistant.components.tandoor.config_flow.PlaceholderHub.authenticate",
        side_effect=CannotConnect,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_URL: "https://recipes.mysticturtles.co",
                CONF_API_KEY: "tda",
            },
        )

    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    # Make sure the config flow tests finish with either an
    # FlowResultType.CREATE_ENTRY or FlowResultType.ABORT so
    # we can show the config flow is able to recover from an error.

    with patch(
        "homeassistant.components.tandoor.config_flow.PlaceholderHub.authenticate",
        return_value=True,
    ):
        result = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_URL: "https://recipes.mysticturtles.com",
                CONF_API_KEY: "tda_063614b3_af4f_4be5_83e4_56e0d1fa869d",
            },
        )
        await hass.async_block_till_done()

    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Tandoor_https://recipes.mysticturtles.com"
    assert result["data"] == {
        CONF_URL: "https://recipes.mysticturtles.com",
        CONF_API_KEY: "tda_063614b3_af4f_4be5_83e4_56e0d1fa869d",
    }
    assert len(mock_setup_entry.mock_calls) == 1
