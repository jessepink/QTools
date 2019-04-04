import smtplib
import os
import imghdr
from email.message import EmailMessage

def send_email(args, subject, message):
    email = EmailMessage()

    email['Subject'] = subject
    email['From'] = args.emailfrom
    email['To'] = args.emaildest
    email.set_content(message)

    with smtplib.SMTP(args.smtpserver, args.smtpport) as smtp:

        if args.nologin != True:
            smtp.ehlo()

            if args.tls == True:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(args.emailfrom, args.smtppassword)

        smtp.send_message(email)

