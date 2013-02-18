#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Almost exact copy of transifex-client except for one line, reasons:
Use our own tx command for now (copy of transifex-client tx), because
buildout 2.0 places the # -*- coding: utf-8 -*- under the sys.path
declaration and therfore causes it to fail because of an utf single quote
in the comment line under the if __name__ == '__main__:' line, i.e.:
# sys.argv[0] is the name of the script that we’re running.
this issue has been reported as an issue on buildout/buildout on github.
Our own txx command (this file) has the problematic line removed.
Change TX_CMD im commands.py to 'tx' when buildout has this solved.

NB: buildout >= 2.0.1 fixes this. SO this file is not needed anymore. Keeping
it for documentation, but can be deleted after the package has proven itself
in real circumstances.

"""

from optparse import OptionParser, OptionValueError
import os
import sys

from txclib import utils
from txclib import get_version
from txclib.log import set_log_level, logger

reload(sys) # WTF? Otherwise setdefaultencoding doesn't work

# This block ensures that ^C interrupts are handled quietly.
try:
    import signal

    def exithandler(signum,frame):
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        sys.exit(1)

    signal.signal(signal.SIGINT, exithandler)
    signal.signal(signal.SIGTERM, exithandler)
    if hasattr(signal, 'SIGPIPE'):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)

except KeyboardInterrupt:
    sys.exit(1)

# When we open file with f = codecs.open we specifi FROM what encoding to read
# This sets the encoding for the strings which are created with f.read()
sys.setdefaultencoding('utf-8')


def main():
    """
    Here we parse the flags (short, long) and we instantiate the classes.
    """
    usage = "usage: %prog [options] command [cmd_options]"
    description = "This is the Transifex command line client which"\
                  " allows you to manage your translations locally and sync"\
                  " them with the master Transifex server.\nIf you'd like to"\
                  " check the available commands issue `%prog help` or if you"\
                  " just want help with a specific command issue `%prog help"\
                  " command`"
    argv = sys.argv[1:]
    parser = OptionParser(
        usage=usage, version=get_version(), description=description
    )
    parser.disable_interspersed_args()
    parser.add_option(
        "-d", "--debug", action="store_true", dest="debug",
        default=False, help=("enable debug messages")
    )
    parser.add_option(
        "-q", "--quiet", action="store_true", dest="quiet",
        default=False, help="don't print status messages to stdout"
    )
    parser.add_option(
        "-r", "--root", action="store", dest="root_dir", type="string",
        default=None, help="change root directory (default is cwd)"
    )
    parser.add_option(
        "--traceback", action="store_true", dest="trace", default=False,
        help="print full traceback on exceptions"
    )
    parser.add_option(
        "--disable-colors", action="store_true", dest="color_disable",
        default=(os.name == 'nt' or not sys.stdout.isatty()),
        help="disable colors in the output of commands"
    )
    (options, args) = parser.parse_args()

    if len(args) < 1:
        parser.error("No command was given")

    utils.DISABLE_COLORS = options.color_disable

    # set log level
    if options.quiet:
        set_log_level('WARNING')
    elif options.debug:
        set_log_level('DEBUG')

    # find .tx
    path_to_tx = options.root_dir or utils.find_dot_tx()


    cmd = args[0]
    try:
        utils.exec_command(cmd, args[1:], path_to_tx)
    except utils.UnknownCommandError:
        logger.error("tx: Command %s not found" % cmd)
    except SystemExit:
        sys.exit()
    except:
        import traceback
        if options.trace:
            traceback.print_exc()
        else:
            formatted_lines = traceback.format_exc().splitlines()
            logger.error(formatted_lines[-1])
        sys.exit(1)

# Run baby :) ... run
if __name__ == "__main__":
    main()
