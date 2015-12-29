import nmap
import time
import math
import hashlib
import socket
import ipaddress

import ftplib
import smb
from smb.SMBConnection import SMBConnection
from elasticsearch import Elasticsearch

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
        nmap_res = self._nm.scan(hosts=range_, ports='445', arguments='-Pn')
        for ip, data in nmap_res['scan'].items():
            print(ip)

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


class AbstractCrawler:

    def crawl(self):
        self._crawl()


class SmbCrawler(AbstractCrawler):
    def __init__(self, conn, proc):
        self._conn = conn
        self._proc = proc

    def _crawl(self):
        for share in self._shares():
            print(share)
            self._smbwalk(share, '/')

    def _smbwalk(self, share, path):
        try:
            for item in self._conn.listPath(share, path):
                if item.filename in ['.', '..', '']:
                    continue
                #print(path + item.filename)
                full_path = path + item.filename

                #TODO visitor
                #TODO index and doc_type to config
                self._proc.index(index='lase_alt',
                                 doc_type='file',
                                 id=self._path_hash(full_path),
                                 body={'filename':item.filename, 'path':path})

                if item.isDirectory:
                    self._smbwalk(share, path + item.filename + '/')
        except smb.smb_structs.OperationFailure as e:
            #TODO logger
            print(e)

    def _shares(self):
        return (share.name
                for share in self._conn.listShares()
                if not share.isSpecial)

    def _path_hash(self, path):
        return hashlib.sha1(path.encode('utf-8')).hexdigest()


class CrawlerFactory():

    def produce(self, host):
        crawlers = []

        es = Elasticsearch()
        if self._smb_open(host):
            crawlers.append(self._produce_smb(host, es))

        return crawlers

    def _produce_smb(host, es):
        conn = SMBConnection('', '', 'lase', host.host_name())

        if 445 in host.ports:
            conn.connect(host.ip, 445)
        else:
            conn.connect(host.ip)
        return SmbCrawler(conn, es)

    def _smb_open(host):
        return 445 in host.ports or 139 in host.ports

    def _ftp_open(host):
        return 21 in host.ports


#FTP
# ftp = ftplib.FTP('147.175.187.131')
# ftp.connect()
# ftp.login()
# ftp.set_pasv(True)
# level = traverse(ftp)
# print(level)

def traverse(ftp, depth=0):

    if depth > 10:
        return ['depth > 10']
    level = {}
    for entry in (path for path in ftp.nlst() if path not in ('.', '..')):
        try:
            print(entry)
            ftp.cwd(entry)
            traverse(ftp, depth+1)
            ftp.cwd('..')
        except ftplib.error_perm:
            pass



def _ranges_to_str(ranges):
    #return ' '.join(ranges)
    #DEBUG test range
    return ranges[0]

def scan(ranges):
    start = time.time()

    nm = nmap.PortScanner()
    #osc = OnlineScanner(nm)
    osc = OnlineScannerMock(nm)

    scanned = osc.scan_range(_ranges_to_str(ranges))

    cf = CrawlerFactory()

    crawlers = []
    for host in scanned:
        print(host.full_host_name())
        crawlers += cf.produce(host)

    try:
        for c in crawlers:
            c.crawl()
    except socket.timeout:
        #TODO logger
        print('timeout')
    except smb.base.NotReadyError as e:
        #TODO logger
        print(e)

    print(time.time() - start)
