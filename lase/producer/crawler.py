import socket
import datetime
import hashlib
import logging
from collections import namedtuple

import ftputil
import smb
from smb.SMBConnection import SMBConnection


logger = logging.getLogger(__name__)

LaseItem = namedtuple('LaseItem', ['id', 'filename', 'path', 'parent', 'host',
                                   'share_type', 'size', 'file_type',
                                   'extension', 'last_modified'])


class Crawler(object):

    def crawl(self):
        try:
            logger.info('starting to crawl host %s',
                        (self._host.full_host_name(),))
            self._crawl()
        except socket.timeout:
            logger.info('socket timeout')
        except socket.herror:
            logger.info('no hostname for ip')
        except smb.base.NotReadyError as e:
            logger.info('SMB connection is not ready (i.e. not authenticated '
                        'or authentication failed)')

    def _last_modified_str(self, timestamp):
        try:
            return datetime.datetime.fromtimestamp(timestamp).isoformat()
        except ValueError as e:
            return datetime.datetime.fromtimestamp(0).isoformat()

    def _special_filename(self, item):
        return item in ['.', '..', '']

    @staticmethod
    def produce(host, processor):
        """Factory method for crawler. Produces correct instance and creates
        neccessary connections."""

        if Crawler._smb_open(host):
            yield Crawler._produce_smb(host, processor)

        if _ftp_open(host):
            #TODO null object
            c = Crawler._produce_ftp(host, processor)
            if c:
                yield c

    @staticmethod
    def _produce_smb(host, es):
        conn = SMBConnection('', '', 'lase', host.host_name(),
                             use_ntlm_v2 = True)
        connected = False

        if 445 in host.ports:
            connected = Crawler._smb_connect(conn, host, 445)

        if not connected and 139 in host.ports:
            connected = Crawler._smb_connect(conn, host, 139)

        return SmbCrawler(host, conn, es)

    @staticmethod
    def _produce_ftp(host, es):
        try:
            ftp = ftputil.FTPHost(host.ip, 'anonymous', '@anonymous')
            return FtpCrawler(host, ftp, es)
        except ftputil.error.PermanentError as e:
            logger.info('FTP permanent error for host: %s', (host,))
        except ftputil.error.FTPOSError as e:
            logger.info('FTP OS error for host: %s', (host,))


    #TODO possible feature envy
    @staticmethod
    def _smb_open(host):
        return 445 in host.ports or 139 in host.ports

    @staticmethod
    def _ftp_open(host):
        return 21 in host.ports

    #TODO possible feature envy
    @staticmethod
    def _smb_connect(conn, host, port):
        try:
            conn.connect(host.ip, port)
        except socket.error:
            logger.info('socket error for host: %s', (host,))
            return False
        except smb.base.NotConnectedError:
            logger.info('SMB not connected error for host: %s', (host,))
            return False
        except smb.base.SMBTimeout as e:
            logger.info('SMB timeout for host: %s', (host,))
            return False

        return True


class SmbCrawler(Crawler):
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
                if self._special_filename(item.filename):
                    continue

                full_path = (self._schema + self._host.full_host_name() +
                             '/' + share + path + item.filename)

                #TODO refactoring
                file_type = 'dir' if item.isDirectory else 'file'
                extension = (None if item.isDirectory or '.' not in item.filename
                                  else item.filename.split('.')[-1])

                lase_item = LaseItem(_hash_id(full_path),
                                     item.filename,
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
                    self._smbwalk(share, lase_item.id,
                                  path + item.filename + '/')

        except smb.smb_structs.OperationFailure as e:
            logger.info('SMB operation failure for host %s: %s',
                        (self._host, e,))
        except smb.base.SMBTimeout:
            logger.info('SMB timeout for host: %s',
                        (self._host,))
        except smb.base.NotConnectedError:
            logger.info('SMB not connected error for host: %s',
                        (self._host,))


    def _shares(self):
        try:
            return (share.name
                    for share in self._conn.listShares()
                    if not share.isSpecial)
        except smb.base.SMBTimeout as e:
            logger.info('SMB timeout for host: %s' % (self._host,))
            return []
        except smb.smb_structs.OperationFailure as e:
            logger.info('SMB operation failure for host %s: %s',
                        (self._host, e,))
            return []



class FtpCrawler(Crawler):

    def __init__(self, host, conn, proc):
        self._host = host
        self._ftp = conn
        self._proc = proc

        self._schema = 'ftp://'

    def _crawl(self):
        try:
            self._ftpwalk(None)
        except ftputil.error.InaccessibleLoginDirError as e:
            logger.info('FTP inaccessible login dir for host: %s',
                        (self._host,))

    def _ftpwalk(self, parent_id):
        for root, dirs, files in self._ftp.walk('/'):

            parent_id = _hash_id(self._schema + self._host.full_host_name() + root)

            for item in dirs:
                self._process_item(root, item, 'dir', parent_id)
            for item in files:
                self._process_item(root, item, 'file', parent_id)

    def _process_item(self, root, item, file_type, parent_id):
        path = self._ftp.path.join(root, item)

        size = 0
        last_modified = 0
        try:
            size = self._ftp.path.getsize(path)
            last_modified = self._ftp.path.getmtime(path)
        except ftputil.error.PermanentError as e:
            logger.info('FTP permanent error for host: %s' % (self._host,))

        extension = (None if file_type == 'dir' or '.' not in item
                          else item.split('.')[-1])

        full_path = self._schema + self._host.full_host_name() + path

        lase_item = LaseItem(_hash_id(full_path),
                             item,
                             full_path,
                             parent_id,
                             self._host.ip,
                             'ftp',
                             size,
                             file_type,
                             extension,
                             self._last_modified_str(last_modified))

        self._proc.process(lase_item)


def _hash_id(path):
    return hashlib.sha1(path).hexdigest()
