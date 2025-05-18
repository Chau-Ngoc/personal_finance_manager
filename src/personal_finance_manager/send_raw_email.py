import email.contentmanager
import email.parser
import email.policy
import os
import smtplib

from dotenv import load_dotenv

load_dotenv()

# mail_parser = email.parser.BytesParser(policy=email.policy.SMTP)
cm = email.contentmanager.raw_data_manager
#
# with open("object.txt", "rb") as f:
#     bytes_mess = f.read()
#
# mess = mail_parser.parsebytes(bytes_mess)
#
# deleted_headers = ('From', 'To', 'Return-Path')
# for k in mess.keys():
#     if k in deleted_headers:
#         del mess[k]
#
# mess['From'] = 'playerzawesome@gmail.com'
# mess['To'] = ['personal_finance_manager@ihaveacooldomain.click']
# mess['Return-Path'] = 'playerzawesome@gmail.com'
#
# with open("bidv.html", "r") as f:
#     attachment_content = f.read()
#     mess.add_attachment(attachment_content, disposition="attachment", filename="bidv.html", content_manager=cm)
mess = email.message.EmailMessage(policy=email.policy.SMTP)
mess["Subject"] = "Test send email to owned domain"
mess["From"] = "playerzawesome@gmail.com"
mess["To"] = ["personal_finance_manager@ihaveacooldomain.click"]
mess.set_content("Hello, this is a test email.", content_manager=cm)

smtpusername = os.getenv("SES_SMTP_USERNAME")
smtppassword = os.getenv("SES_SMTP_PASSWORD")
with smtplib.SMTP("email-smtp.ap-southeast-1.amazonaws.com", 2587) as smtp:
    smtp.starttls()
    smtp.login(smtpusername, smtppassword)
    smtp.send_message(mess)
