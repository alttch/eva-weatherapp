__author__ = "Altertech Group, https://www.altertech.com/"
__copyright__ = "Copyright (C) 2012-2018 Altertech Group"
__license__ = "Apache-2.0"
__version__ = "1.1.1"
__description__ = "Weather Broker"

__id__ = 'weatherapp'
__equipment__ = 'cloud'
__api__ = 4
__required__ = ['port_get', 'value']
__mods_required__ = ['weatherbroker']
__lpi_default__ = 'sensor'
__features__ = ['aao_get', 'cache']
__config_help__ = [{
    'name': 'p',
    'help': 'weather provider',
    'type': 'str',
    'required': True
}, {
    'name': 'k',
    'help': 'API key',
    'type': 'str',
    'required': True
}, {
    'name': 'lat',
    'help': 'Latitude',
    'type': 'float',
    'required': False
}, {
    'name': 'lon',
    'help': 'Latitude',
    'type': 'longitude',
    'required': False
}, {
    'name': 'city_id',
    'help': 'City ID',
    'type': 'int',
    'required': False
}, {
    'name': 'city',
    'help': 'City name',
    'type': 'str',
    'required': False
}, {
    'name': 'country',
    'help': 'Country name',
    'type': 'str',
    'required': False
}, {
    'name': 'units',
    'help': 'Units (si or us)',
    'type': 'enum:str:si,us',
    'required': False
}, {
    'name': 'lang',
    'help': 'Language code (provider specific)',
    'type': 'str',
    'required': False
}]
__get_help__ = []
__set_help__ = []
__help__ = """
Weather broker, collects data from services:

* openweathermap: https://openweathermap.org/
* weatherbit: https://www.weatherbit.io/
* darksky: https://darksky.net/

Requires weatherbroker package (https://pypi.org/project/weatherbroker/)

Specify either lat/lon or city id or city/country. Port names are equal to dict
key names (see weatherbroker package help).
"""

import importlib

from eva.uc.drivers.phi.generic_phi import PHI as GenericPHI
from eva.uc.driverapi import log_traceback
from eva.uc.driverapi import get_timeout

from eva.uc.driverapi import phi_constructor


class PHI(GenericPHI):

    @phi_constructor
    def __init__(self, **kwargs):
        try:
            wb = importlib.import_module('weatherbroker')
        except:
            self.log_error('weatherbroker python module not found')
            self.ready = False
            return
        self.engine = wb.WeatherEngine()
        try:
            self.engine.set_provider(self.phi_cfg.get('p'))
        except:
            self.log_error('provider set error: {}'.format(
                self.phi_cfg.get('o')))
            self.ready = False
            return
        lat = self.phi_cfg.get('lat')
        lon = self.phi_cfg.get('lon')
        city_id = self.phi_cfg.get('city_id')
        city = self.phi_cfg.get('city')
        country = self.phi_cfg.get('country')
        if lat and lon:
            try:
                lat = float(lat)
                lon = float(lon)
            except:
                self.log_error('invalid lat/lon values')
                self.ready = False
                return
            self.engine.set_location(lat=lat, lon=lon)
        elif city_id:
            try:
                city_id = int(city_id)
            except:
                self.log_error('invalid city_id value')
                self.ready = False
                return
            self.engine.set_location(city_id=city_id)
        elif city and country:
            self.engine.set_location(city=city, country=country)
        else:
            self.log_error('specify at least one location type')
            self.ready = False
            return
        self.engine.key = self.phi_cfg.get('k')
        self.engine.lang = self.phi_cfg.get('lang')
        self.engine.units = self.phi_cfg.get('units')

    def get(self, port=None, cfg=None, timeout=0):
        data = self.get_cached_state()
        if data is None:
            try:
                data = self.engine.get_current(timeout=timeout)
                if not data: return None
                self.set_cached_state(data)
            except:
                log_traceback()
                return None
        if port is None: return data
        return data.get(port)

    def test(self, cmd=None):
        if cmd == 'self':
            return 'OK' if self.get(timeout=get_timeout()) else 'FAILED'
        if cmd == 'get':
            return self.get(timeout=get_timeout())
        return {
            'get': 'get provider data',
        }
