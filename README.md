## Welcome to the QTools github site

QTools will incorporate various tools written in Python 3.x to be helper applications for Component Control's Quantum Control software.

At first, QTools only has one tool available, which I call the "GL Monitor."  It pulls the values of your Quantum Control inventory GL accounts and the value of the non-historical inventory that is in that account, compares them, and if different will display the difference on the screen and if configured correctly, will send an email out notifications of the discrepancy.  This is particularly powerful if set up as a scheduled task in Windows or Linux via cron because it will allow you to narrow down the timeframe in which you must search for the "bad" adjustments.  If you run the task every five minutes, you only have to looks through the GL or inventory transactions that occured within the last 5 minutes.

### Quick and basic Windows configuration instructions to get you running
*For Windows computers, this must be installed on a computer with the Quantum client installed*

1. Put all the files from the ZIP file in a folder, i.e. "C:\qtools"
1. Open command prompt in windows by hitting WindowsKey+R, cmd.exe.
1. From the command line, go to the folder you put it in (type: “cd\qtools”)
1. Type “qtools --updateconfig”
    * Answer all the questions it asks of you, the email functions have been tested it using both a personal gmail account and a Windows server IIS email relay, but should work for any properly configured SMTP server.  Gmail requires both TLS and login, whereas the IIS relay does not require TLS nor login.  If using an internal relay, you may have to have your IT make sure that the relay will accept emails from whatever computer this is set up on (it may be easiest to set it up on the same server as your Quantum host, as you know it will always be online as long as Quantum is online).
1. After you go through all the configuration, you can run “qtools --glmonitor”.  
    * A simple way to test this quickly is to make a new GL batch in Quantum, add a journal entry to one of your inventory accounts for say, $100, and DO NOT POST.  The glmonitor will detect the deviation regardless of post status.  
    * Run the “qtools --glmonitor” command again and see that there is a “deviation”.  You can run it again and see that additional emails are not sent (unless your notification timing threshold is set really low).  
    * Be sure to delete the journal entry (you can then delete the entire batch if there are no other entries in it).  
    * Run the tool again, and you’ll get an email that it is resolved.
    * This process CAN be run on your test/training server if you'd like if you'd like, just be sure to either edit qtools.cfg or run "qtools --updateconfig" again to change back to your "live" server.
