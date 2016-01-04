import socket
import datetime
import hashlib

import ftplib
import smb
from smb.SMBConnection import SMBConnection


class LaseItem():

    def __init__(self, filename, path, parent, host,
                 share_type, size, file_type, extension, last_modified):
        self.filename = filename
        self.path = path
        self.parent = parent
        self.host = host
        self.share_type = share_type
        self.size = size
        self.file_type = file_type
        self.extension = extension
        self.last_modified = last_modified

    def id(self):
        return hashlib.sha1(self.path).hexdigest()


class AbstractCrawler:

    def crawl(self):
        try:
            self._crawl()
        except socket.timeout:
            #TODO logger
            print('socket timeout')
        except socket.herror:
            #TODO logger
            print('no hostname for ip')
        except smb.base.NotReadyError as e:
            #TODO logger
            #print(e)
            pass


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
                #TODO condition to superclass
                if item.filename in ['.', '..', '']:
                    continue

                full_path = self._schema + self._host.full_host_name() + '/' + share + path + item.filename

                #TODO refactoring
                file_type = 'dir' if item.isDirectory else 'file'
                extension = None if item.isDirectory or '.' not in item.filename else item.filename.split('.')[-1]

                lase_item = LaseItem(item.filename,
                                     full_path,
                                     parent_id,
                                     self._host.ip,
                                     'smb',
                                     item.file_size,
                                     file_type,
                                     extension,
                                     self._last_modified_str(item.last_write_time))

                self._proc.process(lase_item)

                if item.isDirectory:
                    self._smbwalk(share, lase_item.id(), path + item.filename + '/')

        except smb.smb_structs.OperationFailure as e:
            #TODO logger
            pass
            #print(e)

    def _last_modified_str(self, timestamp):
        try:
            return datetime.datetime.fromtimestamp(timestamp).isoformat()
        except ValueError as e:
            return datetime.datetime.fromtimestamp(0).isoformat()

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
                #self._process(self._path_hash(full_path), {'filename':entry, 'path':full_path, 'parent':parent_id, 'host':self._host.ip, 'share_type':'ftp', 'size':self._ftp.size(entry)})

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
            #pass
            print(body)
            #print('encoding...')
            #TODO fucking encoding

    def _list_path(self):
        return (path
                for path in self._ftp.nlst()
                if path not in ('.', '..'))

    def _move_up(self):
        self._ftp.cwd('..')


class CrawlerFactory():

    def produce(self, host, processor):
        crawlers = []

        if self._smb_open(host):
            crawlers.append(self._produce_smb(host, processor))

        if self._ftp_open(host):
            #TODO null object
            c = self._produce_ftp(host, processor)
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


