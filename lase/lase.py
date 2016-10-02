import sys
import getopt
import logging

import config
import producer
import api

logger = logging.getLogger(__name__)


def help():
    print('Usage: $LASE_HOME/env/bin/python lase.py [ -c | -C HOST | -s | -S HOST ]')
    print('Try \'$LASE_HOME/env/bin/python lase.py --help\' for more information.')


def help_long():
    print('Usage: $LASE_HOME/env/bin/python lase.py [OPTION]')
    print('LASE options:')
    print('')
    print('  -s, --scan                scans everything specified in config file')
    print('  -S, --scan-host=HOST      scans specified HOST')
    print('  -c, --crawl               scans and crawls everything specified in config file')
    print('  -C, --crawl-host=HOST     scans and crawls specified HOST')
    print('      --serve               starts default Flask Werkzeug web server; only for DEVELOPMENT')
    print('      --help                display this help text and exit')


def logger_config():
    if  config.LOG_FILE:
        logging.basicConfig(stream=sys.stdout, level=logging.WARN)
    else:
        logging.basicConfig(filename=config.LOG_FILE, level=logging.WARN)


def main(argv):
    if not argv:
        help()

    try:
        opts, args = getopt.getopt(argv, 'sS:cC:', ['help', 'scan', 'crawl', 'crawl-host=', 'scan-host=', 'serve'])
    except getopt.GetoptError:
        help()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            help()
        if opt == '--help':
            help_long()
        elif opt == '--serve':
            api.run_api()
        elif opt in ('-c', '--crawl'):
            producer.crawl_seq(config.ranges)
        elif opt in ('-s', '--scan'):
            producer.scan(config.ranges)
        elif opt in ('-C', '--crawl-host'):
            producer.crawl_seq([arg])
        elif opt in ('-S', '--scan-host'):
            producer.scan([arg])


if __name__ == '__main__':
    # init mainly because of python 2
    reload(sys)
    sys.setdefaultencoding('utf-8')

    logger_config()

    main(sys.argv[1:])
