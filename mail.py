#https://realpython.com/python-send-email/

import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# To send attached binary file:
from email import encoders
from email.mime.base import MIMEBase

#smtp_server = "smtp.gmail.com"
#sender_email = "longtd9999@gmail.com"
#password = 'lritrgxoackpbfla' # Google App password #
#password = input("Type your password and press enter: ")

#Tao Google App Password:
#https://help.warmupinbox.com/en/articles/4934806-configure-for-google-workplace-with-two-factor-authentication-2fa
#Enable IMAP (Individual Mailbox Side)
#https://myaccount.google.com/apppasswords


smtp_server = 'smtp.office365.com'
#sender_email = 'auto_refund@bambooairways.com'
#password = 'refund@000'

sender_email = 'noreply@bambooairways.com'
password = 'bambu@2023'

port_SSL = 465  # For SSL
port_TLS = 587  # For starttls


#receiver_emails = ["longtd@bambooairways.com", "baont@bambooairways.com"]
receiver_emails = "baont@bambooairways.com"

message = MIMEMultipart("alternative")
message["Subject"] = "multipart test"
message["From"] = sender_email
message["To"] = receiver_emails
message["Bcc"] = receiver_emails  # Recommended for mass emails

#message = """Subject: Hi LongTD
#From: From Person <from@fromdomain.com>
#To: To Person <longtd@bambooairways.com>

#This message is sent from Python ssl."""


# Create the plain-text and HTML version of your message
text = """\
Hi,
How are you?
Real Python has many great tutorials:
www.realpython.com"""

html = """\
<html>
  <body>
    <p>Hi Long,<br>
       How are you?<br>
       <a href="http://www.realpython.com">Real Python</a> 
       has many great tutorials.
    </p>
  </body>
</html>
"""

# Turn these into plain/html MIMEText objects
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
message.attach(part1)
message.attach(part2)


#Attach binary file:
#filename = "C:/Temp/Di Phap.xlsx"  # In same directory as script

# Open PDF file in binary mode
'''
with open(filename, "rb") as attachment:
    # Add file as application/octet-stream
    # Email client can usually download this automatically as attachment
    part = MIMEBase("application", "octet-stream")
    part.set_payload(attachment.read())

# Encode file in ASCII characters to send by email:
encoders.encode_base64(part)

# Add header as key/value pair to attachment part
part.add_header(
    "Content-Disposition",
    f"attachment; filename= {filename}",
)

# Add attachment to message and convert message to string
message.attach(part)
'''

def send_ssl():
    #smtplib.SMTP('mail.your-domain.com', 25)
    with smtplib.SMTP_SSL(smtp_server, port_SSL, context=context) as server:

        server.login(sender_email, password)
        #server.sendmail(sender_email, receiver_emails, message)
        server.sendmail(sender_email, receiver_emails, message.as_string())
        

def send_tls():
    with smtplib.SMTP(smtp_server, port_TLS) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.ehlo()  # Can be omitted
        server.login(sender_email, password)
        #server.sendmail(sender_email, receiver_emails, message)
        
        server.sendmail(sender_email, receiver_emails, message.as_string())


# Create a secure SSL context
context = ssl.create_default_context()

#send_ssl() # not work for account auto_refund
send_tls()

'''
import csv
message = """Subject: Your grade

Hi {name}, your grade is {grade}"""

with open("contacts_file.csv") as file:
    reader = csv.reader(file)
    next(reader)  # Skip header row
    for name, email, grade in reader:
        print(f"Sending email to {name}")
        # Send email here
        server.sendmail(sender_email, email, message.format(name=name, grade=grade))
'''


'''
import yagmail

receiver = "your@gmail.com"
body = "Hello there from Yagmail"
filename = "document.pdf"

yag = yagmail.SMTP("my@gmail.com")
yag.send(
    to=receiver,
    subject="Yagmail test with attachment",
    contents=body, 
    attachments=filename,
)

'''