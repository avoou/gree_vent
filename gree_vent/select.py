import logging
import codecs
import serial
import asyncio
from homeassistant.components.select import SelectEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType


_LOGGER = logging.getLogger(__name__)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None
) -> None:

    fhbqd_vent_objects = hass.data["gree_vent_list"]
    coordinators = hass.data["coord_list"]
    
    select_entites = []

    def process(cl, vent_obj, coord):
        opt_obj = cl(vent_device=vent_obj, hass=hass)
        #select_entites.append(opt_obj)
        coord.async_add_listener(opt_obj.update_callback)
        return opt_obj

    for i in range(len(fhbqd_vent_objects)):
        mode_obj = process(SelectOptVentMode, fhbqd_vent_objects[i], coordinators[i])
        fan_speed_obj = process(SelectOptFanSpeed, fhbqd_vent_objects[i], coordinators[i])
        bypass_obj = process(SelectOptBypass, fhbqd_vent_objects[i], coordinators[i])
        select_entites.extend([mode_obj, fan_speed_obj, bypass_obj])

    add_entities(select_entites)

    _LOGGER.warning("in select.py setup_platform def, after add_entities def ")


class SelectOptBypass(SelectEntity):
    def __init__(self, vent_device, hass):
        self.hass = hass
        self._vent_device = vent_device
        self._end_name = self._vent_device.name
        self._select_options = ['on', 'off', 'auto']
        self._current_option = ''

    def update_callback(self):
        self._current_option = self._vent_device.bypass_mode
        self.async_schedule_update_ha_state()


    @property
    def name(self):
        return "SelectOptBypass_" + self._end_name


    @property
    def current_option(self):
        return self._current_option


    @property
    def options(self):
        if self._vent_device.vent_power != 'off':
            return self._select_options
        else:
            return []

    
    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        
        cm = [self._vent_device.vent_mode, self._vent_device.fan_speed, option]
        status_exec_cm = await self.hass.async_add_executor_job(self._vent_device.run_com, cm)

        if status_exec_cm == 'OK':
            self._current_option = option
            self._vent_device.bypass_mode = option
        
        self.async_schedule_update_ha_state()


    @property
    def should_poll(self):
        return False


    async def async_update(self):
        pass



class SelectOptFanSpeed(SelectEntity):
    def __init__(self, vent_device, hass):
        self.hass = hass
        self._vent_device = vent_device
        self._end_name = self._vent_device.name
        self._select_options = ['1', '2', '3']
        self._current_option = None


    def update_callback(self):
        self._current_option = self._vent_device.fan_speed
        self.async_schedule_update_ha_state()


    @property
    def name(self):
        return "SelectOptFanSpeed_" + self._end_name


    @property
    def current_option(self):
        return self._current_option


    @property
    def options(self):
        if self._vent_device.vent_power != 'off':
            return self._select_options
        else:
            return []

    
    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        
        cm = [self._vent_device.vent_mode, option, self._vent_device.bypass_mode]
        status_exec_cm = await self.hass.async_add_executor_job(self._vent_device.run_com, cm)
        
        if status_exec_cm == "OK":
            self._current_option = option
            self._vent_device.fan_speed = option

        self.async_schedule_update_ha_state()


    @property
    def should_poll(self):
        return False


    async def async_update(self):
        pass


class SelectOptVentMode(SelectEntity):
    def __init__(self, vent_device, hass):
        self.hass = hass
        self._vent_device = vent_device
        self._end_name = self._vent_device.name
        self._select_options = ['normal', 'normal supply', 'save', 'save supply']
        self._current_option = None



    def update_callback(self):
        self._current_option = self._vent_device.vent_mode
        self.async_schedule_update_ha_state()


    @property
    def name(self):
        return "SelectOptVentMode_" + self._end_name


    @property
    def current_option(self):
        return self._current_option


    @property
    def options(self):
        if self._vent_device.vent_power != 'off':
            return self._select_options
        else:
            return []

    
    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        
        cm = [option, self._vent_device.fan_speed, self._vent_device.bypass_mode]
        status_exec_cm = await self.hass.async_add_executor_job(self._vent_device.run_com, cm)
        
        if status_exec_cm == "OK":
            self._current_option = option
            self._vent_device.vent_mode = option
            
        self.async_schedule_update_ha_state()


    @property
    def should_poll(self):
        return False

        
    async def async_update(self):
        pass