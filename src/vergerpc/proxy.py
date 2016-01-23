"""
  Copyright (c) 2007 Jan-Klaas Kollhof
  Copyright (c) 2011-2013 Jeff Garzik
  Copyright (c) 2013 Nikolay Belikov (nikolay@belikov.me)


  jsonrpc is free software; you can redistribute it and/or modify
  it under the terms of the GNU Lesser General Public License as published by
  the Free Software Foundation; either version 2.1 of the License, or
  (at your option) any later version.

  This software is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU Lesser General Public License for more details.

  You should have received a copy of the GNU Lesser General Public License
  along with this software; if not, write to the Free Software
  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
"""

try:
    import http.client as httplib
except ImportError:
    import httplib
import base64
import json
import decimal
try:
    import urllib.parse as urlparse
except ImportError:
    import urlparse
from collections import defaultdict, deque
from vergerpc.exceptions import TransportException

USER_AGENT = "AuthServiceProxy/0.1"

HTTP_TIMEOUT = 30


class JSONRPCException(Exception):
    def __init__(self, rpc_error):
        Exception.__init__(self)
        self.error = rpc_error


class HTTPTransport(object):
    def __init__(self, service_url):
        self.service_url = service_url
        self.parsed_url = urlparse.urlparse(service_url)
        if self.parsed_url.port is None:
            port = 80
        else:
            port = self.parsed_url.port
        authpair = "%s:%s" % (self.parsed_url.username,
                              self.parsed_url.password)
        authpair = authpair.encode('utf8')
        self.auth_header = "Basic ".encode('utf8') + base64.b64encode(authpair)
        if self.parsed_url.scheme == 'https':
            self.connection = httplib.HTTPSConnection(self.parsed_url.hostname,
                                                      port, None, None, False,
                                                      HTTP_TIMEOUT)
        else:
            self.connection = httplib.HTTPConnection(self.parsed_url.hostname,
                                                     port, False, HTTP_TIMEOUT)

    def request(self, serialized_data):
        self.connection.request('POST', self.parsed_url.path, serialized_data,
                                {'Host': self.parsed_url.hostname,
                                 'User-Agent': USER_AGENT,
                                 'Authorization': self.auth_header,
                                 'Content-type': 'application/json'})

        httpresp = self.connection.getresponse()
        if httpresp is None:
            self._raise_exception({
                'code': -342, 'message': 'missing HTTP response from server'})
        elif httpresp.status == httplib.FORBIDDEN:
            msg = "verged returns 403 Forbidden. Is your IP allowed?"
            raise TransportException(msg, code=403,
                                     protocol=self.parsed_url.scheme,
                                     raw_detail=httpresp)

        resp = httpresp.read()
        return resp.decode('utf8')


class FakeTransport(object):
    """A simple testing facility."""
    def __init__(self):
        self._data = defaultdict(deque)

    def load_serialized(self, method_name, fixture):
        self._data[method_name].append(fixture)

    def load_raw(self, method_name, fixture):
        self._data[method_name].append(json.dumps(fixture))

    def request(self, serialized_data):
        data = json.loads(serialized_data, parse_float=decimal.Decimal)
        method_name = data['method']
        return self._data[method_name].popleft()


class RPCMethod(object):
    def __init__(self, name, service_proxy):
        self._method_name = name
        self._service_proxy = service_proxy

    def __getattr__(self, name):
        new_name = '{}.{}'.format(self._method_name, name)
        return RPCMethod(new_name, self._service_proxy)

    def __call__(self, *args):
        self._service_proxy._id_counter += 1
        data = {'version': '1.1',
                'method': self._method_name,
                'params': args,
                'id': self._service_proxy._id_counter}
        postdata = json.dumps(data)
        resp = self._service_proxy._transport.request(postdata)
        resp = json.loads(resp, parse_float=decimal.Decimal)

        if resp['error'] is not None:
            self._service_proxy._raise_exception(resp['error'])
        elif 'result' not in resp:
            self._service_proxy._raise_exception({
                'code': -343, 'message': 'missing JSON-RPC result'})
        else:
            return resp['result']

    def __repr__(self):
        return '<RPCMethod object "{name}">'.format(name=self._method_name)


class AuthServiceProxy(object):
    """
    You can use custom transport to test your app's behavior without calling
    the remote service.

    exception_wrapper is a callable accepting a dictionary containing error
    code and message and returning a suitable exception object.
    """
    def __init__(self, service_url, transport=None, exception_wrapper=None):
        self._service_url = service_url
        self._id_counter = 0
        self._transport = (HTTPTransport(service_url) if transport is None
                           else transport)
        self._exception_wrapper = exception_wrapper

    def __getattr__(self, name):
        return RPCMethod(name, self)

    def _get_method(self, name):
        """
        Get method instance when the name contains forbidden characters or
        already taken by internal attribute.
        """
        return RPCMethod(name, self)

    def _raise_exception(self, error):
        if self._exception_wrapper is None:
            raise JSONRPCException(error)
        else:
            raise self._exception_wrapper(error)
