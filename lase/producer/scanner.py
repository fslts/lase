import nmap
import math
import socket

#in python3 stdlib
import ipaddress

from utils.cache import LaseRedisCache
import crawler

class ScannedHost(object):

    def __init__(self, ip, ports):
        self.ip = ip
        self.ports = ports
        self._host_name = None

    def full_host_name(self):
        if not self._host_name:
            (self._host_name, _, _) = socket.gethostbyaddr(self.ip)
        return self._host_name

    def host_name(self):
        return self.full_host_name().split('.')[0]


class OnlineScanner(object):
    """Checks if FTP and SMB are available in IPs specified in config. Nmap is
    used for online scanning."""

    def __init__(self, nmap, cache):
        self._nm = nmap
        self._cache = cache

    def scan_range(self, range_):
        res = []
        nmap_res = self._nm.scan(hosts=range_, ports='21,139,445', arguments=' --max-retries 0 -Pn')

        for ip, data in nmap_res['scan'].items():
            ports = self._open_ports(data)

            self._cache.store_host(ip, ports)

            if ports:
                res.append(ScannedHost(ip, ports))
        return res

    def _open_ports(self, data):
        return [ port for port, port_data in data['tcp'].items() if port_data['state'] == 'open' ]


    @staticmethod
    def produce():
        nm = nmap.PortScanner()
        cache = LaseRedisCache()
        return OnlineScanner(nm, cache)
