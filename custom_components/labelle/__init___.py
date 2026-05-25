from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import LabelleApiClient
from .const import CONF_URL, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Labelle Web from a config entry."""

    url = entry.data[CONF_URL]

    session = async_get_clientsession(hass)
    client = LabelleApiClient(session, url)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = client

    _LOGGER.debug("Loaded Labelle Web integration for %s", url)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Labelle Web config entry."""

    if DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    _LOGGER.debug("Unloaded Labelle Web integration")

    return True