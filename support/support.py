import sys, os, logging
import cx_Oracle
import configparser


logger = logging.getLogger(__name__)

def connect_quantum(args):

    if args.qhost:
        host = args.qhost
    else:
        sys.exit \
            (f'Quantum server hostname required, use --qhost [host] command line argument or --updateconfig to configure it in your configuration file.')

    if args.qport:
        port = args.qport
    else:
        sys.exit(
            f'Quantum server hostname required, use --qport [port] command line argument or --updateconfig to configure it in your configuration file.')


    if args.qsid:
        sid = args.qsid
    else:
        sys.exit(
            f'Quantum server hostname required, use --qsid [sid] command line argument or --updateconfig to configure it in your configuration file.')

    if args.qdbuser:
        qdbuser = args.qdbuser
    else:
        sys.exit(
            f'Quantum server hostname required, use --qdbuser [dbuser] command line argument or --updateconfig to configure it in your configuration file.')

    if args.qdbpassword:
        qdbpassword = args.qdbpassword
    else:
        sys.exit(
            f'Quantum server hostname required, use --qdbpassword [dbpassword] command line argument or --updateconfig to configure it in your configuration file.')

    dsn_tns = cx_Oracle.makedsn(host, port, sid)
    try:
        quantum_con = cx_Oracle.connect(qdbuser, qdbpassword, dsn_tns)
    except Exception as e:
        print('\n' + '-' * 60)
        msg = f'Failure connecting to Quantum database\nType: {type(e)}'
        logger.warning(msg, exc_info=True)
        print('-' * 60)
        sys.exit('Connection to Quantum failed, check configuration files.')

    return quantum_con

def update_config(emaildest=None, emailfrom=None, smtppassword=None, smtpserver=None, smtpport=None, silencealert=None,\
                  qhost=None, qport=None, qsid=None, qdbuser=None,\
                  qdbpassword=None, config_file=None, config_path=None, tls=False, nologin=False):

    config = configparser.ConfigParser(allow_no_value=True)

    try:
        if not config_file:
            config_file = 'qtools.cfg'
        if not config_path:
            config_path = os.path.dirname(os.path.abspath(__name__))
        config.read(os.path.join(config_path, config_file))
    except Exception as e:
        print('\n' + '-' * 60)
        msg = f'Exception reading config file at {os.path.join(config_path, config_file)}\nType: {type(e)}'
        logger.warning(msg, exc_info=True)
        print('-' * 60)

    print('Default values (located in []) can be selected by simply hitting "Enter".')

    if not config.has_section('EMAIL'):
        config.add_section('EMAIL')

    if emaildest:
        default = emaildest
    elif config.has_option('EMAIL', 'emaildest'):
        default = config.get('EMAIL', 'emaildest')
    else:
        default = ''
    get_input = input(f'Standard Email Desintation (comma separated) [{default}]: ')
    if get_input.strip():
        config['EMAIL']['emaildest'] = get_input
    else:
        config['EMAIL']['emaildest'] = default

    if emailfrom:
        default = emailfrom
    elif config.has_option('EMAIL', 'emailfrom'):
        default = config.get('EMAIL', 'emailfrom')
    else:
        default = ''
    get_input = input(f'Standard Email Origination (only one email address allowed) [{default}]: ')
    if get_input.strip():
        config['EMAIL']['emailfrom'] = get_input
    else:
        config['EMAIL']['emailfrom'] = default

    if smtppassword:
        default = smtppassword
    elif config.has_option('EMAIL', 'smtppassword'):
        default = config.get('EMAIL', 'smtppassword')
    else:
        default = ''
    get_input = input(f'SMTP password [{default}]: ')
    if get_input.strip():
        config['EMAIL']['smtppassword'] = get_input
    else:
        config['EMAIL']['smtppassword'] = default

    if smtpserver:
        default = smtpserver
    elif config.has_option('EMAIL', 'smtpserver'):
        default = config.get('EMAIL', 'smtpserver')
    else:
        default = ''
    get_input = input(f'SMTP (email) server address [{default}]: ')
    if get_input.strip():
        config['EMAIL']['smtpserver'] = get_input
    else:
        config['EMAIL']['smtpserver'] = default

    if smtpport:
        default = smtpport
    elif config.has_option('EMAIL', 'smtpport'):
        default = config.get('EMAIL', 'smtpport')
    else:
        default = '587'
    while True:
        get_input = input(f'SMTP Port (typically 25, 587 or 465 for SSL) [{default}]: ')
        if get_input.strip():
            config['EMAIL']['smtpport'] = str(get_input)
        else:
            config['EMAIL']['smtpport'] = str(default)
        try:
            test = int(config['EMAIL']['smtpport'])
            if test <= 0:
                raise ValueError
        except ValueError:
            print(f"Your input: {get_input}, however you must input a positive whole number (i.e. 5, 180, etc.)")
        else:
            ## The value already stored or just input is a whole number greater than or equal to 1
            break

    if tls:
        default = str(tls)
    elif config.has_option('EMAIL', 'tls'):
        default = config.get('EMAIL', 'tls')
    else:
        default = 'False'
    while True:
        get_input = input(f'Does your email (SMTP) server required a secure (SSL/TLS) connection? [Y/n] ')
        if get_input.strip().lower() == 'y':
            default = 'True'
            break
        elif get_input.strip().lower() == 'n':
            default = 'False'
            break
        else:
            print(f'Your input: {get_input}\nPlease enter either Y if your server requires a secure connection or N if it does not.')
    if default == 'True':
        config['EMAIL']['tls'] = default
    else:
        if config.has_option('EMAIL', 'tls'):
            config.remove_option('EMAIL', 'tls')

    # if nologin:
    #     default = str(nologin)
    # elif config.has_option('EMAIL', 'nologin'):
    #     default = config.get('EMAIL', 'nologin')
    # else:
    #     default = 'True'
    while True:
        get_input = input(f'Does your email (SMTP) server require you to login (most services do, however if you run an in-house server/relay, you may not need to) [Y/n] ')
        if get_input.strip().lower() == 'y':
            default = 'False'
            break
        elif get_input.strip().lower() == 'n':
            default = 'True'
            break
        else:
            print(f'Your input: {get_input}\nPlease enter either Y if your server requires you to login or N if it does not.')
    if default == 'True':
        config['EMAIL']['nologin'] = default
    else:
        if config.has_option('EMAIL', 'nologin'):
            config.remove_option('EMAIL', 'nologin')


    if silencealert:
        default = str(silencealert)
    elif config.has_option('EMAIL', 'silencealert'):
        default = config.get('EMAIL', 'silencealert')
    else:
        default = '180'
    while True:
        get_input = input(f'Length in minutes to silence notifications that don\'t contain new information [{default}]: ')
        if get_input.strip():
            config['EMAIL']['silencealert'] = get_input
        else:
            config['EMAIL']['silencealert'] = default
        try:
            test = int(config['EMAIL']['silencealert'])
            if test <= 0:
                raise ValueError
        except ValueError:
            print(f"Your input: {get_input}, however you must input a positive whole number (i.e. 5, 180, etc.)")
        else:
            ## The value already stored or just input is a whole number greater than or equal to 1
            break

    if not config.has_section('QUANTUM'):
        config.add_section('QUANTUM')

    if qhost:
        default = qhost
    elif config.has_option('QUANTUM', 'qhost'):
        default = config.get('QUANTUM', 'qhost')
    else:
        default = ''
    get_input = input(f'Quantum server hostname [{default}]: ')
    if get_input.strip():
        config['QUANTUM']['qhost'] = get_input
    else:
        config['QUANTUM']['qhost'] = default

    if qport:
        default = qport
    elif config.has_option('QUANTUM', 'qport'):
        default = config.get('QUANTUM','qport')
    else:
        default = '1521'
    while True:
        get_input = input(f'Quantum server port (typically \'1521\') [{default}]: ')
        if get_input:
                config['QUANTUM']['qport'] = get_input.strip()
        else:
            config['QUANTUM']['qport'] = str(default)
        try:
            test = int(config['QUANTUM']['qport'])
            if test <= 0:
                raise ValueError
        except ValueError:
            print(f"Your input: {get_input}, however you must input a positive whole number (i.e. 5, 180, etc.)")
        else:
            ## The value already stored or just input is a whole number greater than or equal to 1
            break

    if qsid:
        default = qsid
    elif config.has_option('QUANTUM', 'qsid'):
        default = config.get('QUANTUM', 'qsid')
    else:
        default = 'CCTL'
    get_input = input(f'Quantum server SID (typically \'CCTL\') [{default}]: ')
    if get_input.strip():
        config['QUANTUM']['qsid'] = get_input
    else:
        config['QUANTUM']['qsid'] = default

    if qdbuser:
        default = qdbuser
    elif config.has_option('QUANTUM', 'qdbuser'):
        default = config.get('QUANTUM', 'qdbuser')
    else:
        default = 'None'
    get_input = input(f'Quantum database username [{default}]: ')
    if get_input.strip():
        config['QUANTUM']['qdbuser'] = get_input
    else:
        config['QUANTUM']['qdbuser'] = default

    if qdbpassword:
        default=qdbpassword
    elif config.has_option('QUANTUM', 'qdbpassword'):
        default = config.get('QUANTUM', 'qdbpassword')
    else:
        default = 'None'
    get_input = input(f'Quantum server database password (If you don\'t want to store your password, type "None", and use command line arguments to issue password at runtime) [{default}]: ')
    if get_input.strip():
        config['QUANTUM']['qdbpassword'] = get_input
    else:
        config['QUANTUM']['qdbpassword'] = default

    if not config_path:
        path = os.path.dirname(os.path.abspath(__name__))
    else:
        path = config_path

    if not config_file:
        filename = 'qtools.cfg'
    else:
        filename = config_file

    with open(os.path.join(path, filename), 'w') as configfile:
        config.write(configfile)