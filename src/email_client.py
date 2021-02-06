import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import time


class Emailer(object):

    @classmethod
    def __init__(cls):
        '''
        Place Holder
        '''

    # def send_email(self, payload):
    #     msg = MIMEText(payload)
    #     # msg.set_charset('utf-8')
    #     msg['Subject'] =  'Saved stories Extract for: ' + str(time.strftime('%Y%m%d%H%M%S'))
    #     msg['From'] = 'your_python_project@github.com'
    #     msg['To'] = 'miller.oleg@gmail.com'

    #     # Send the message via Gmail SMTP server.
    #     smtpserver = smtplib.SMTP("aspmx.l.google.com", 25)
    #     smtpserver.ehlo()
    #     smtpserver.starttls()
    #     smtpserver.ehlo        
    #     try:
    #         smtpserver.send_message(msg)
    #     except: 
    #         pass
    #     smtpserver.quit()


    def email_csv(self, file):
        emailfrom = 'your_python_project@github.com'
        emailto = 'miller.oleg@gmail.com'
        fileToSend = file
        # username = "user"
        # password = "password"

        msg = MIMEMultipart()
        msg["From"] = emailfrom
        msg["To"] = emailto
        msg["Subject"] =  'Saved stories Extract for: ' + str(time.strftime('%Y%m%d%H%M%S'))
        msg.preamble =  'Saved stories Extract for: ' + str(time.strftime('%Y%m%d%H%M%S'))

        ctype, encoding = mimetypes.guess_type(fileToSend)
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"
        maintype, subtype = ctype.split("/", 1)

        if maintype == "text":
            fp = open(fileToSend)
            # Note: we should handle calculating the charset
            attachment = MIMEText(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "image":
            fp = open(fileToSend, "rb")
            attachment = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
        elif maintype == "audio":
            fp = open(fileToSend, "rb")
            attachment = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
        else:
            fp = open(fileToSend, "rb")
            attachment = MIMEBase(maintype, subtype)
            attachment.set_payload(fp.read())
            fp.close()
            encoders.encode_base64(attachment)
        attachment.add_header("Content-Disposition", "attachment", filename=fileToSend)
        msg.attach(attachment)
        
        smtpserver = smtplib.SMTP("aspmx.l.google.com", 25)
        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo        
        try:
            smtpserver.send_message(msg)
        except: 
            pass
        smtpserver.quit()


        # server = smtplib.SMTP("smtp.gmail.com:587")
        # server.starttls()
        # server.login(username,password)
        # server.sendmail(emailfrom, emailto, msg.as_string())
        # server.quit()