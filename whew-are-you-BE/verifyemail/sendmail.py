import smtplib, ssl
from pathlib import Path
import os, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
secret_file = os.path.join(BASE_DIR, 'secrets.json') 

with open(secret_file) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets): 
# secret 변수를 가져오거나 그렇지 못 하면 예외를 반환
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

#### [email] ####
sender_email = get_secret("EMAIL_ID")
receiver_email = "nyskyline7@gmail.com"
password = get_secret("EMAIL_APPKEY")

message = MIMEMultipart("alternative")
message["Subject"] = "[휴알유] 회원가입을 위한 인증메일이 도착하였습니다."
message["From"] = "후알유 - 발신전용"
message["To"] = receiver_email

# Create the plain-text and HTML version of your message
text = """\
휴알유 가입을 축하합니다!
이메일 인증을 요청하였다면, 아래의 링크를 눌러 가입을 완료하시기 바랍니다.
인증을 요청한 적이 없다면, 이 메일을 무시하셔도 됩니다. 

https://google.com
"""
html = """\
<html>
  <body>
    <p>휴알유 가입을 축하합니다!
        <br>이메일 인증을 요청하였다면, 아래의 링크를 눌러 가입을 완료하시기 바랍니다.
        <br>
       <a href="https://google.com">이메일 인증 완료하기</a> 
       <br>인증을 요청한 적이 없다면, 이 메일을 무시하셔도 됩니다. 
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

# Create secure connection with server and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(
        sender_email, receiver_email, message.as_string()
    )
