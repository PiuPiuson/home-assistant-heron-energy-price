"""Platform for sensor integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Asynchronously set up the sensor platform."""
    sensor = HeronTariffPrice()
    async_add_entities([sensor], True)

    # Schedule the sensor to update every hour
    async_track_time_interval(hass, sensor.async_update, timedelta(seconds=10))


URL = "https://www.heron.gr/prices-generous-guarantee/"

TRANSPORT_SYSTEM = 0.00844
DISTRIBUTION_NETWORK = 0.01415
ETEMEAP = 0.017
YKO = 0.01824


class HeronTariffPrice(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Energy Price"
    _attr_native_unit_of_measurement = "€/kWh"
    _attr_device_class = SensorDeviceClass.MONETARY
    _attr_state_class = SensorStateClass.TOTAL
    _attr_native_value = 0

    async def async_update(self, now=None) -> None:
        """Asynchronously fetch new state data for the sensor.

        This method should fetch new data for Home Assistant.
        """
        # Example: asynchronously fetch new data and update the sensor value
        new_value = await self.fetch_new_data()
        self._attr_native_value = new_value

    async def fetch_new_data(self):
        """Fetch the latest energy price from the Heron website."""

        async with ClientSession() as session, session.get(URL) as response:
            html = await response.text()

        soup = BeautifulSoup(html, "html.parser")

        table = soup.find("table")
        if table:
            # Find all rows in the table
            rows = table.find_all("tr")
            if len(rows) > 1:
                # Assuming the value is in the second row and fourth column
                price_cell = rows[1].find_all("td")[3]
                if price_cell:
                    price = price_cell.text.strip()
                    price = price.replace(",", ".")
                    total = (
                        float(price)
                        + TRANSPORT_SYSTEM
                        + DISTRIBUTION_NETWORK
                        + ETEMEAP
                        + YKO
                    )
                    return total

        return None  # Return None or some default value if the price is not found
