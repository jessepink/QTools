import os
import configparser
import logging
from datetime import datetime, timedelta
from support.support import connect_quantum
from emailer.emailer import send_email

try:
    logger = logging.getLogger('__main__')
except:
    logger = logging.getLogger(__name__)

def glmonitor(args=None):

    if not args:
        print("No arguments provided, aborting...")

    glmon = configparser.ConfigParser()
    glmon.read(os.path.join(os.path.dirname(os.path.abspath(__name__)), 'glmonitor.ini'))

    # try:
    #     if args.config_file:
    #         config_file = args.configfile
    #     else:
    #         config_file = None
    #     if args.config_path:
    #         config_path = args.configpath
    #     else:
    #         config_path = None
    #     config.read(os.path.join(config_path, config_file))
    # except Exception as e:
    #     print('\n' + '-' * 60)
    #     msg = f'Exception reading config file at {os.path.join(config_path, config_file)}\nType: {type(e)}'
    #     logging.warning(msg, exc_info=True)
    #     print('-' * 60)

    quantum_con = connect_quantum(args)

    sql_check = """select act.account_number, act.total_balance as "gl_total_balance", stk.total_balance as "stk_total_balance"
	    from view_inv_val_accounts act,
	    (select account_number, sum(QTY_OH * UNIT_COST) as total_balance from view_inv_val_stock group by account_number) stk
        where stk.account_number = act.account_number"""

    cur = quantum_con.cursor()

    try:
        cur.execute(sql_check)
        fetch = cur.fetchall()

    except Exception as e:
        print('\n' + '-' * 60)
        msg = f'Exception fetching GL info from database.\nType: {type(e)}'
        logging.warning(msg, exc_info=True)
        print('-' * 60)
        cur.close()
        quantum_con.close()
        email_msg = f'{msg}\n{e}'
        send_email(args, "Error with GL Monitor", email_msg)
        return

    cur.close()
    quantum_con.close()

    current_time = datetime.now()

    email_msg = ''

    for account in fetch:
        if not glmon.has_section(account[0]):
            glmon.add_section(account[0])

        diff = account[1] - account[2]
        updated = False
        if glmon.has_option(account[0], 'diff_amount'):
            if glmon[account[0]]['diff_amount'] != f'{diff:.2f}':
                last_changed = str(current_time)
                if diff == 0:
                    glmon[account[0]]['off_since'] = 'NA'
                elif glmon.has_option(account[0], 'off_since'):
                    if glmon[account[0]]['off_since'] == 'NA':
                        glmon[account[0]]['off_since'] = last_changed
                else:
                    glmon[account[0]]['off_since'] = last_changed

                updated = True
            else:
                if glmon.has_option(account[0], 'last_changed'):
                    last_changed = glmon[account[0]]['last_changed']
                else:
                    last_changed = str(current_time)
                    glmon[account[0]]['last_changed'] = last_changed


                if not glmon.has_option(account[0], 'off_since'):
                    if diff == 0:
                        glmon[account[0]]['off_since'] = 'NA'
                    else:
                        glmon[account[0]]['off_since'] = glmon[account[0]]['last_changed']
                else:
                    if diff == 0:
                        glmon[account[0]]['off_since'] = 'NA'



                  ## still need to figure out how to get off_since to only update upon initial gl deviation
                    # elif glmon[account[0]]['diff_amount'] != 0:
                    #     glmon[account[0]]['off_since'] = str(current_time)




        else:
            glmon[account[0]]['diff_amount'] = f'{diff:.2f}'
            last_changed = str(current_time)
            if diff != 0:
                glmon[account[0]]['off_since'] = str(current_time)
            else:
                glmon[account[0]]['off_since'] = 'NA'

        if updated == True:
            if diff == 0:
                msg = f'Deviation resolved for account {account[0]}, current balance: ${account[1]}.\n'
                logger.warning(msg)
                email_msg = f'{email_msg}\n{msg}'

            else:
                msg = f'GL Deviation for account {account[0]} is ${diff:.2f}.  Account balance: ${account[1]}, Inventory balance: ${account[2]}.'
                logger.warning(msg)
                email_msg = f'{email_msg}\n{msg}'
            glmon[account[0]]['last_changed'] = last_changed
            glmon[account[0]]['diff_amount'] = f'{diff:.2f}'
        elif diff != 0 and current_time - datetime.strptime(last_changed, '%Y-%m-%d %H:%M:%S.%f') > timedelta(0, args.silencealert * 60, 0):
            msg = f'GL Deviation for account {account[0]} is ${diff:.2f}.  Account balance: ${account[1]}, Inventory balance: ${account[2]}. Account has been off balance since {glmon[account[0]]["off_since"]}.'
            logger.warning(msg)
            email_msg = f'{email_msg}\n{msg}'
            glmon[account[0]]['last_changed'] = str(current_time)
        else:
            logger.info('Nothing to report...')

    with open(os.path.join(os.path.dirname(os.path.abspath(__name__)), 'glmonitor.ini'), 'w') as configfile:
        glmon.write(configfile)

    if email_msg:
        send_email(args, subject='GL Deviation Monitor', message=email_msg)

    return