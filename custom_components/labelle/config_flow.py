from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LabelleApiClient
from .const import CONF_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class CannotConnect(Exception):
    """Error to indicate we cannot connect to Labelle Web."""


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input by calling Labelle Web's health endpoint."""

    url = data[CONF_URL].strip().rstrip("/")

    session = async_get_clientsession(hass)
    client = LabelleApiClient(session, url)

    try:
        health_data = await client.health()
    except (aiohttp.ClientError, TimeoutError, asyncio.TimeoutError) as err:
        raise CannotConnect from err

    if health_data.get("status") != "ok":
        raise CannotConnect

    version = health_data.get("version", "unknown")

    return {
        "title": f"Labelle Web {version}",
        "url": url,
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Labelle Web."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ):
        """Handle the initial setup step."""

        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:
                _LOGGER.exception("Unexpected exception while connecting to Labelle Web")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info["url"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=info["title"],
                    data={
                        CONF_URL: info["url"],
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_URL,
                        default="http://localhost:5000",
                    ): str,
                }
            ),
            errors=errors,
        )