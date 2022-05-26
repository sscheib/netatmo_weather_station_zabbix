# -*- coding: UTF-8 -*-

"""
This module is a representation of the Netatmo Weather Station
"""

# imports
from __future__ import print_function
import logging
import requests
import json
from enum import Enum
from pprint import pprint, pformat  # pylint: disable=unused-import
from urllib.parse import urlparse


# get the logger
LOG = logging.getLogger('satellite_patch_management')


class NetatmoWeatherStation:
    @property
    def api_url(self) -> str:
        """The full URL for the Netatmo Weather Station API"""
        return self._api_url

    @api_url.setter
    def api_url(self, value: str) -> None:
        if not value or value is None:
            raise ValueError('Empty value for {} not allowed.'
                             .format('api_url'))
        elif not isinstance(value, str):
            raise TypeError('Given value for {} is not a string. Type of the value: {}.'
                            .format('api_url', str(type(value))))
        # validate the URL
        try:
            parsed_url = urlparse(value)
            if not parsed_url.scheme or not parsed_url.netloc:
                LOG.error(f'Given URL {value} has no protocol included in its URL (http/https).')
                raise ValueError
        except ValueError:
            raise ValueError(f'Given URL {value} is not valid')

        self._api_url = value

    @api_url.deleter
    def api_url(self) -> None:
        del self._api_url

    @property
    def api_timeout(self) -> float:
        """Time a request to the API will time out if no data received within"""
        return self._api_timeout

    @api_timeout.setter
    def api_timeout(self, value: float) -> None:
        if not value or value is None:
            raise ValueError('Empty value for {} not allowed.'
                             .format('api_timeout'))
        elif not isinstance(value, float):
            raise TypeError('Given value for {} is not a float. Type of the value: {}.'
                            .format('api_timeout', str(type(value))))
        self._api_timeout = value

    @api_timeout.deleter
    def api_timeout(self) -> None:
        del self._api_timeout

    @property
    def verify_ssl(self) -> bool:
        """Determines whether the SSL certificate is being verified while connecting to API"""
        return self._verify_ssl

    @verify_ssl.setter
    def verify_ssl(self, value: bool) -> None:
        if value is None:
            raise ValueError('Empty value for {} not allowed.'
                             .format('verify_ssl'))
        elif not isinstance(value, bool):
            raise TypeError('Given value for {} is not a boolean. Type of the value: {}.'
                            .format('verify_ssl', str(type(value))))
        self._verify_ssl = value

    @verify_ssl.deleter
    def verify_ssl(self) -> None:
        del self._verify_ssl

    @property
    def enable_debug(self) -> str:
        """Enables debugging log output"""
        return self._enable_http_debug

    @enable_debug.setter
    def enable_debug(self, value: str) -> None:
        if not value or value is None:
            raise ValueError('Empty value for {} not allowed.'
                             .format('enable_debug'))
        elif not isinstance(value, str):
            raise TypeError('Given value for {} is not a string. Type of the value: {}.'
                            .format('enable_debug', str(type(value))))
        self._enable_http_debug = value

    @enable_debug.deleter
    def enable_debug(self) -> None:
        del self._enable_http_debug

    @property
    def enable_http_trace(self) -> bool:
        """Determines whether to print the JSON result returned from the Satellite API"""
        return self._enable_http_trace

    @enable_http_trace.setter
    def enable_http_trace(self, value: bool) -> None:
        if value is None:
            self._enable_http_trace = False
        elif not isinstance(value, bool):
            raise TypeError('Given value for property {} is not a boolean. Type of the value: {}.'
                            .format('enable_http_trace', str(type(value))))
        else:
            self._enable_http_trace = value
        LOG.debug('Property %s set to %s',
                  'enable_http_trace', str(self._enable_http_trace))

    @enable_http_trace.deleter
    def enable_http_trace(self) -> None:
        del self._enable_http_trace

    class HttpRequestType(Enum):
        """Representation of the different HTTP request types"""
        GET = 1
        POST = 2
        PUT = 3
        DELETE = 4

    """Checks if a string is valid json"""
    @staticmethod
    def _is_json(string: str) -> bool:
        try:
            json.loads(string)
        except ValueError:
            LOG.debug(f'Given string is not a valid JSON formatted string. Following the given string: {string}')
            return False

        return True

    def __init__(self, **kwargs) -> None:
        self._api_url = None
        self._api_timeout = None
        self._verify_ssl = None

        self._enable_http_trace = None
        self._enable_http_debug = None

        if kwargs.get('api_url'):
            self.api_url = kwargs.get('api_url')

        if kwargs.get('api_timeout'):
            self.api_url = kwargs.get('api_timeout')

        if kwargs.get('verify_ssl'):
            self.verify_ssl = kwargs.get('verify_ssl')

        if kwargs.get('enable_http_trace'):
            self.enable_http_trace = kwargs.get('enable_http_trace')

        if kwargs.get('_enable_http_debug'):
            self._enable_http_debug = kwargs.get('_enable_http_debug')

    def query_api(self, http_request_type: HttpRequestType, location: str, data: str = None) -> dict:
        """Queries the Netatmo Weather Station API
        Queries the Netatmo Weather Station API and returns the result as JSON formatted string.
        HTTP types supported are: GET, POST, PUT, DELETE.

        Args:
            http_request_type (str): The HTTP request type to use. Supported are GET, POST, PUT, DELETE
            location (str): Location to query (Example: content_views/1)
            data (str, optional): The optional payload to deliver with the HTTP request

        Returns:
            dict: The resulting response from the HTTP requests as JSON formatted string (=dict)

        Raises:
            ValueError: If the first argument is None or not given
            TypeError: If the first argument is not an instance of HttpRequestType
            ValueError: If the second argument is None or not given
            TypeError: If the second argument is not an instance of ApiType
            ValueError: If the third argument is None or not given
            TypeError: If the third argument is not a string
            TypeError: If the fourth argument is not a boolean
            TypeError: If the optional fifth argument is given, but is not a string
            ValueError: If the optional fifth argument is given, but is not a JSON formatted string
            ValueError: If the given HTTP request type is not supported
            HTTPError: If the request returns with an unsuccessful status code
            ConnectionError: If a connection to the Satellite API cannot be established (DNS failure, connection
                             refused, etc)
            Timeout: If the request exceeds the maximum time in which it didn't receive any data
            RequestException: If the HTTP request fails for another reason
            RuntimeError: If the HTTP request fails for some reason
        """
        # check existence and type of the first argument
        if not http_request_type or http_request_type is None:
            raise ValueError(f'Given value for the first argument (\'http_request_type\') is empty (or None).')
        elif not isinstance(http_request_type, self.HttpRequestType):
            raise TypeError(f'Given value for the first argument (\'http_request_type\') is not an instance '
                            f'of HttpRequestType. Type of value is {type(http_request_type)}.')

        # check existence and type of the second argument
        if not location or location is None:
            raise ValueError(f'Given value for the second argument (\'location\') is empty (or None).')
        elif not isinstance(location, str):
            raise TypeError(f'Given value for the second argument (\'location\') is not a string. Type of value '
                            f'is {type(location)}.')

        # check type of the third argument (if given)
        if data is not None:
            if not isinstance(data, str):
                raise TypeError(f'Given value for the third argument (\'data\') is not a string. Type of value '
                                f'is {type(data)}.')
            elif not self._is_json(data):
                raise ValueError(f'Given value for the fifth argument (\'data\') is not a JSON formatted string. '
                                 f'Following the given value: {data}')

        if data is not None:
            if self.enable_debug:
                LOG.debug(f'Using HTTP {http_request_type.name} on {self.api_url + location} with '
                          f'payload {pformat(data)}')
        else:
            if self.enable_debug:
                LOG.debug(f'Using HTTP {http_request_type.name} on {self.api_url + location}')

        # do the HTTP request
        auth = (self.api_username, self.api_password)
        try:
            if http_request_type is self.HttpRequestType.GET:
                response = requests.get(self.api_url + location,
                                        data=data,
                                        auth=auth,
                                        verify=self.verify_ssl,
                                        timeout=self.api_timeout,
                                        headers={'content-type': 'application/json'})
            elif http_request_type is self.HttpRequestType.POST:
                response = requests.post(self.api_url + location,
                                         data=data,
                                         auth=auth,
                                         verify=self.verify_ssl,
                                         timeout=self.api_timeout,
                                         headers={'content-type': 'application/json'})
            elif http_request_type is self.HttpRequestType.PUT:
                response = requests.put(self.api_url + location,
                                        data=data,
                                        auth=auth,
                                        verify=self.verify_ssl,
                                        timeout=self.api_timeout,
                                        headers={'content-type': 'application/json'})
            elif http_request_type is self.HttpRequestType.DELETE:
                response = requests.delete(self.api_url + location,
                                           data=data,
                                           auth=auth,
                                           verify=self.verify_ssl,
                                           timeout=self.api_timeout,
                                           headers={'content-type': 'application/json'})
            else:
                raise ValueError(f'Given HTTP request type is not supported! Given is {http_request_type.name}.')

            if self.enable_http_trace:
                LOG.debug(pprint(response.json()))

            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            raise requests.exceptions.HTTPError(f'The HTTP {http_request_type.name} request failed with an HTTPError. '
                                                f'Following the complete error:'
                                                f' {http_error}')
        except requests.exceptions.ConnectionError as connection_error:
            raise requests.exceptions.ConnectionError(f'Unable to connect to the configured API {self.api_url}. '
                                                      f'Following the complete error: '
                                                      f'{connection_error}')
        except requests.exceptions.ReadTimeout as read_timeout_error:
            raise requests.exceptions.ReadTimeout(f'The HTTP {http_request_type.name} request timed out. No data was '
                                                  f'retrieved for {self.api_timeout} seconds from the Satellite '
                                                  f'server. Following the complete error: '
                                                  f'{read_timeout_error}')
        except requests.exceptions.Timeout as timeout_error:
            raise requests.exceptions.Timeout(f'Timeout of the HTTP {http_request_type.name} request has been reached. '
                                              f'Following the complete error: '
                                              f'{timeout_error}')
        except requests.exceptions.RequestException as request_exception:
            raise requests.exceptions.RequestException(f'The HTTP {http_request_type.name} request failed. Following '
                                                       f'the complete error: '
                                                       f'{request_exception}')

        if self.enable_debug:
            LOG.debug(f'Status code of the {http_request_type.name} request: {response.status_code}')

        if not response.ok:
            raise RuntimeError(f'Last {http_request_type.name} request failed. Request returned with '
                               f'HTTP code {response.status_code}')

        # return the response as JSON
        return response.json()
