"""Config flow for EyeOnWater integration."""
from __future__ import annotations

import logging

import aiohttp
import voluptuous as vol
from pyonwater import Account, Client

from homeassistant import config_entries
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN, CONF_HOSTNAME, DEFAULT_HOSTNAME

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_HOSTNAME, default=DEFAULT_HOSTNAME): str,
    }
)


class EyeOnWaterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EyeOnWater."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Test the credentials
            try:
                account = Account(
                    eow_hostname=user_input[CONF_HOSTNAME],
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
                async with aiohttp.ClientSession() as session:
                    client = Client(session, account)
                    await client.authenticate()
                    meters = await account.fetch_meters(client)

                if not meters:
                    errors["base"] = "no_meters"
                else:
                    # Use username as unique ID to prevent duplicate entries
                    await self.async_set_unique_id(user_input[CONF_USERNAME])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"EyeOnWater ({user_input[CONF_USERNAME]})",
                        data=user_input,
                    )
            except Exception:
                _LOGGER.exception("Error connecting to EyeOnWater")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=DATA_SCHEMA,
            errors=errors,
        )
