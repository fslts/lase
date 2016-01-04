import nmap
import time
import math
import multiprocessing
import socket

#in python3 stdlib
import ipaddress

import crawler
import processor

class ScannedHost:
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


class OnlineScanner:

    def __init__(self, nmap):
        self._nm = nmap
        self.online = []

    def scan_range(self, range_):
        res = []
        nmap_res = self._nm.scan(hosts=range_, ports='21,139,445', arguments=' --max-retries 0 -Pn')
        for ip, data in nmap_res['scan'].items():
            #TODO to method
            ports = [ port for port, port_data in data['tcp'].items() if port_data['state'] == 'open' ]

            if ports:
                res.append(ScannedHost(ip, ports))
        return res
#TODO remove after main debugging phase finishes
class OnlineScannerMock(OnlineScanner):
    def __init__(self, nmap):
        self._nm = nmap

    def scan_range(self, range_):
        return [ScannedHost('147.175.187.8', [445])]


def _ranges_to_str(ranges):
    return ' '.join(ranges)


def _scan_host(host):

    cf = crawler.CrawlerFactory()
    proc = processor.LaseElasticProcessor()

    print(host.full_host_name())
    for crwl in cf.produce(host, proc):
        crwl.crawl()


def scan(ranges):
    start = time.time()

    nm = nmap.PortScanner()
    osc = OnlineScannerMock(nm)
    scanned = osc.scan_range(_ranges_to_str(ranges))

    print(time.time() - start)
    print(len(scanned))

    #pool = multiprocessing.Pool(4)
    #pool.map(_scan_host, scanned)

    for host in scanned:
        _scan_host(host)

    print(time.time() - start)
