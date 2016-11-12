
from txweb import choosereactor
choosereactor.install_optimal_reactor(False)
from txweb import web
from txweb import logger
from txweb import permit
from txweb.storage import Storage
from txweb.config import find_config
from cyclone.options import options,define,parse_command_line
from twisted.internet import reactor
from twisted.internet import defer
import sys,os
import importlib
import signal

'''
simple :  txappctl --dir=simple
'''

define("port", 0, type=int, help="application listen http port")
define("pnum", 0, type=int, help="application proc number")
define("app", '',help="application name")
define("dir", '.',help="application dir")
define("conf", 'txweb.json',help="json config file ")
define('debug', type=bool, default=True)


def main():
    parse_command_line()
    gdata = Storage()
    gdata.port = options.port
    gdata.pnum = options.pnum
    gdata.debug = options.debug
    gdata.app_dir = os.path.abspath(options.dir)
    if not os.path.exists(options.dir):
        print 'app dir not exists'
        sys.exit(0)

    sys.path.insert(0, gdata.app_dir)

    try:
        if r'/' in options.conf:
            gdata.config_file = os.path.abspath(options.conf)
        else:
            gdata.config_file = os.path.abspath(os.path.join(options.dir,options.conf))

        gdata.config = find_config(gdata.config_file)

        appmdl = importlib.import_module(options.app)
        print "import startup module %s"%appmdl
        startd = appmdl.start(gdata)

        def initerr(err):
            print repr(err)
            reactor.stop()

        if isinstance(startd, defer.Deferred):
            startd.addCallbacks(logger.info,initerr)

        def exit_handler(signum, stackframe): 
            reactor.callFromThread(reactor.stop)
        signal.signal(signal.SIGTERM, exit_handler)
        reactor.run()
    except:
        import traceback
        traceback.print_exc()


