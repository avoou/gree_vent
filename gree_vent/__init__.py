"""The component."""
import logging
import datetime
from .vent_device import FHBQDVentilation
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

_LOGGER = logging.getLogger(__name__)

DOMAIN = "gree_vent"

#COMPORT2 = "/dev/serial/by-id/usb-1a86_USB2.0-Ser_-if00-port0"                  #Floor2
#COMPORT1 = "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_A702W1GG-if00-port0"     #Floor4
COMPORT1 = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.2:1.0-port0'
COMPORT2 = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.4:1.0-port0'

PORTS = [COMPORT1, COMPORT2]

async def async_setup(hass, config):
    vent_device_1 = FHBQDVentilation(port=COMPORT1, name='floor4')
    vent_device_2 = FHBQDVentilation(port=COMPORT2, name='floor2')

    hass.data["gree_vent_list"] = [vent_device_1, vent_device_2]

    updateDelta = 30
    timeDelta = datetime.timedelta(seconds=updateDelta)

    coordinator1 = VentDeviceDataUpdateCoordinator(hass=hass, logger=_LOGGER, device=vent_device_1, name=COMPORT1, timeDelta=timeDelta)
    coordinator2 = VentDeviceDataUpdateCoordinator(hass=hass, logger=_LOGGER, device=vent_device_2, name=COMPORT2, timeDelta=timeDelta)
    hass.data["coord_list"] = [coordinator1, coordinator2]
    
    try:
        await coordinator1.async_config_entry_first_refresh()
        await coordinator2.async_config_entry_first_refresh()
        _LOGGER.warning("in __init__.py async_setup def, try block OK ")
    except:
        return False
    

    return True


class VentDeviceDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass, logger, device, name, timeDelta) -> None:
        """Initialize."""
        self.device = device
        self.hass = hass

        super().__init__(hass, logger=logger, name=name, update_interval=timeDelta)

    async def _async_update_data(self):
        await self.hass.async_add_executor_job(self.device.refresh_status)
        #next, async_update_listeners() will be run

