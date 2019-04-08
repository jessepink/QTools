import configargparse
import os, sys
import logging
from glmonitor.glmonitor import glmonitor
from support.support import connect_quantum, update_config
# import cx_Oracle


# Create a custom logger
logger = logging.getLogger(__name__)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('qtools.log')
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.WARNING)

# Create formatters and add it to the handlers
f_format = logging.Formatter('[%(asctime)s] %(levelname)s | %(module)s | %(process)d | %(lineno)d | %(exc_info)s | %(message)s')
c_format = logging.Formatter('[%(asctime)s] %(levelname)s | %(lineno)d | %(message)s')
f_handler.setFormatter(f_format)
c_handler.setFormatter(c_format)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)
logger.setLevel(logging.DEBUG)

# def get_config(args):
#     config = configparser.ConfigParser(allow_no_value=True)
#
#     try:
#         if not args.configfile:
#             config_file = 'qtools.cfg'
#         if not args.configpath:
#             config_path = os.path.dirname(os.path.abspath(__file__))
#         config.read(os.path.join(config_path, config_file))
#     except Exception as e:
#         print('\n' + '-' * 60)
#         msg = f'Exception reading config file at {os.path.join(config_path, config_file)}\nType: {type(e)}'
#         logging.warning(msg, exc_info=True)
#         print('-' * 60)




def main():
    if getattr(sys, 'frozen', False):
        # The application is frozen
        datadir = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        datadir = os.path.dirname(os.path.abspath(__file__))

    parser = configargparse.ArgumentParser(default_config_files=['qtools.cfg'])
    parser.add_argument("-q", "--quiet", type=str, help="Suppress all output")
    parser.add_argument("-v", "--verbose", type=str, help="Additional information printed to screen")
    parser.add_argument("-d", "--emaildest", type=str,
                        help="Email address(es) to send to, separated by a comma (,)")
    parser.add_argument("-f", "--emailfrom", type=str, help="Originating email address (from), also login name if necessary for emails")
    parser.add_argument("-p", "--smtppassword", type=str, help="SMTP (email) password", default='None')
    parser.add_argument("-s", "--smtpserver", type=str, help="SMTP (email) server (i.e. smtp.gmail.com)")
    parser.add_argument("-c", "--configfile", type=str, help="config file name (default: qtools.cfg)", default='qtools.cfg')
    parser.add_argument("--configpath", type=str, help="Part to configuration file (default: script location)", default=datadir)
    parser.add_argument("--smtpport", type=int, help="SMTP (email) server port, default is 25", default=25)
    parser.add_argument("--tls", help="If your mail server requires a TLS connection", action='store_true')
    parser.add_argument("--nologin", help="If your SMTP server does NOT require you to login to send emails", action='store_true')
    parser.add_argument("--silencealert", type=int, help="Length in minutes to silence notifications that don't contain new information (default: 180)", default=180)
    parser.add_argument("--qhost", type=str, help="Quantum server hostname")
    parser.add_argument("--qport", type=str, help="Quantum server port (default: 1521)", default='1521')
    parser.add_argument('--qsid', type=str, help="Quantum server SID (default: CCTL)", default="CCTL")
    parser.add_argument('--qdbuser', type=str, help="Quantum DB username", default='None')
    parser.add_argument('--qdbpassword', type=str, help="Quantum DB password", default='None' )

    parser.add_argument('--glmonitor', action='store_true', help="Run the GL Monitor")
    parser.add_argument('--updateconfig', action='store_true', help='Update config file only (qtools.cfg unless specified by -c flag)')

    args = parser.parse_args()

    if args.updateconfig:
        update_config(emaildest=args.emaildest, emailfrom=args.emailfrom, smtppassword=args.smtppassword,
                      smtpserver=args.smtpserver, smtpport=args.smtpport, silencealert=args.silencealert,
                      qhost=args.qhost, qport=args.qport, qsid=args.qsid, qdbuser=args.qdbuser,
                      qdbpassword=args.qdbpassword, config_file=args.configfile, config_path=args.configpath,
                      tls=args.tls, nologin=args.nologin)
    elif args.glmonitor:
        glmonitor(args)
    else:
        print("Use \"qtools -h\" to see all available commands. If using for the first time, try \"qtools --updateconfig\" to do initial configuration and then \"qtools --glmonitor\" to run the GL Monitor.")


if __name__ == '__main__':
    main()