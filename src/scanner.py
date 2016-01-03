import nmap
import time
import math
import hashlib
import socket
import multiprocessing
import datetime

#in python3 stdlib
import ipaddress

import ftplib
import smb
from smb.SMBConnection import SMBConnection
import elasticsearch

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


class AbstractCrawler:

    def crawl(self):
        self._crawl()

    def _path_hash(self, path):
        return hashlib.sha1(path).hexdigest()


class SmbCrawler(AbstractCrawler):
    def __init__(self, host, conn, proc):
        self._host = host
        self._conn = conn
        self._proc = proc

        self._schema = 'smb://'

    def _crawl(self):
        for share in self._shares():
            self._smbwalk(share, None, '/')

    def _smbwalk(self, share, parent_id, path):
        try:
            for item in self._conn.listPath(share, path):
                if item.filename in ['.', '..', '']:
                    continue
                print(path + item.filename)
                full_path = self._schema + self._host.full_host_name() + '/' + share + path + item.filename

                #TODO visitor
                #TODO index and doc_type to config
                #TODO extension filetype


                file_type = 'dir' if item.isDirectory else 'file'
                extension = None if item.isDirectory or '.' not in item.filename else item.filename.split('.')[-1]

                self._proc.index(index='lase_alt',
                                 doc_type='file',
                                 id=self._path_hash(full_path),
                                 body={'filename':item.filename,
                                       'path':full_path,
                                       'parent':parent_id,
                                       'host':self._host.ip,
                                       'share_type':'ftp',
                                       'size':item.file_size,
                                       'file_type':file_type,
                                       'extension':extension,
                                       'last_modified':self._last_modified_str(item.last_write_time)})
                #print(full_path)

                if item.isDirectory:
                    self._smbwalk(share, self._path_hash(full_path), path + item.filename + '/')
        except smb.smb_structs.OperationFailure as e:
            #TODO logger
            pass
            #print(e)

    def _last_modified_str(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp).isoformat()

    def _shares(self):
        return (share.name
                for share in self._conn.listShares()
                if not share.isSpecial)


class FtpCrawler(AbstractCrawler):

    def __init__(self, host, conn, proc):
        self._host = host
        self._ftp = conn
        self._proc = proc

        self._schema = 'ftp://'

    def _crawl(self):
        self._ftpwalk(None, '')

    def _ftpwalk(self, parent_id, path):
        try:
            for entry in self._list_path():
                full_path = self._schema + self._host.full_host_name() + '/' + path + entry

                #TODO extension filetype date modified/created
                self._process(self._path_hash(full_path), {'filename':entry, 'path':full_path, 'parent':parent_id, 'host':self._host.ip, 'share_type':'ftp', 'size':self._ftp.size(entry)})

                self._ftp.cwd(entry)
                self._ftpwalk(path + entry + '/')
                self._move_up()
        except ftplib.error_perm:
            pass
        except socket.error:
            print('socket error')

    def _process(self, id_, body):
        try:
            self._proc.index(index='lase_alt',
                             doc_type='file',
                             id=id_,
                             body=body)
        except elasticsearch.exceptions.SerializationError:
            pass
            #print(body)
            #print('encoding...')
            #TODO fucking encoding

    def _list_path(self):
        return (path
                for path in self._ftp.nlst()
                if path not in ('.', '..'))

    def _move_up(self):
        self._ftp.cwd('..')


class CrawlerFactory():

    def produce(self, host):
        crawlers = []

        es = elasticsearch.Elasticsearch()
        if self._smb_open(host):
            crawlers.append(self._produce_smb(host, es))

        if self._ftp_open(host):
            #TODO null object
            c = self._produce_ftp(host, es)
            if c:
                crawlers.append(c)

        return crawlers

    def _produce_smb(self, host, es):
        conn = SMBConnection('', '', 'lase', host.host_name(), use_ntlm_v2 = True)
        connected = False

        if 445 in host.ports:
            connected = self._smb_connect(conn, host, 445)

        if not connected and 139 in host.ports:
            connected = self._smb_connect(conn, host, 139)

        return SmbCrawler(host, conn, es)

    def _produce_ftp(self, host, es):
        try:
            ftp = ftplib.FTP(host.ip)
      #      ftp.connect()
            ftp.login()
            ftp.set_pasv(True)
            return FtpCrawler(host, ftp, es)
        except ftplib.error_perm:
            #TODO logger
            print('ftp permission denied')
            #TODO return null object

    #TODO possible feature envy
    def _smb_open(self, host):
        return 445 in host.ports or 139 in host.ports

    def _ftp_open(self, host):
        return 21 in host.ports

    #TODO possible feature envy
    def _smb_connect(self, conn, host, port):
        try:
            conn.connect(host.ip, port)
        except socket.error:
            #TODO logger
            print('socket error')
            return False
        except smb.base.NotConnectedError:
            return False
        return True


def _ranges_to_str(ranges):
    return ' '.join(ranges)


def _scan_host(host):
    print(host.full_host_name())

    cf = CrawlerFactory()
    try:
        for crawler in cf.produce(host):
            crawler.crawl()
    except socket.timeout:
        #TODO logger
        print('socket timeout')
    except smb.base.NotReadyError as e:
        #TODO logger
        #print(e)
        pass

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
