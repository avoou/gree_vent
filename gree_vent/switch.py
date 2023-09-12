

import logging
import codecs
import serial
import asyncio
from homeassistant.components.switch import (SwitchEntity)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity


_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:

    fhbqd_vent_objects = hass.data["gree_vent_list"]
    coordinators = hass.data["coord_list"]

    switch_entites = []

    def process(cl, vent_obj, coord):
        switch_obj = cl(vent_device=vent_obj, hass=hass)
        coord.async_add_listener(switch_obj.update_callback)
        return switch_obj

    for i in range(len(fhbqd_vent_objects)):
        switch_obj = process(FHBQDOnOffSwitch, fhbqd_vent_objects[i], coordinators[i])
        switch_entites.append(switch_obj)

    add_entities(switch_entites)

    _LOGGER.warning("in switch.py setup_platform def, after add_entities def ")



class FHBQDOnOffSwitch(SwitchEntity):

    def __init__(self, vent_device, hass):
        self.hass = hass
        self._vent_device = vent_device
        self._end_name = self._vent_device.name
        self._state = None


    
    @property
    def should_poll(self):
        return False


    @property
    def name(self):
        return "FHBQDOnOffSwitch_" + self._end_name


    @property
    def is_on(self) -> bool | None:
        return self._state


    def update_callback(self):
        self._state = self._vent_device.vent_power != 'off'
        self.async_schedule_update_ha_state()


    async def async_turn_on(self, **kwargs) -> None:
        status = await self.hass.async_add_executor_job(self._vent_device.run_com, ['on', ' ', ' '])

        if status == 'OK':
            self._vent_device.vent_power = 'on'
            self._state = True

        self.async_schedule_update_ha_state()


    async def async_turn_off(self, **kwargs) -> None:
        status = await self.hass.async_add_executor_job(self._vent_device.run_com, ['off', ' ', ' '])

        if status == 'OK':
            self._vent_device.vent_power = 'off'
            self._state = False

        self.async_schedule_update_ha_state()


    async def async_update(self):
        pass