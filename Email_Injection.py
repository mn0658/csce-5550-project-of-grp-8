import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
from pathlib import Path

# Email settings
smtp_server = 'smtp.example.com' 
smtp_port = 587  
smtp_username = 'your-email@example.com' 
smtp_password = 'your-password'  

# Recipient's email address
recipient_email = ''

attachment_path = '\Downloads\Hello world.zip'

# Create the email message
email_message = EmailMessage()
email_message['From'] = smtp_username
email_message['To'] = recipient_email
email_message['Subject'] = 'Updated Kt Session'
email_message.set_content('')

# Generic file attachment method
def attach_file_to_email(email_message, file_path):
    file_name = Path(file_path).name
    ctype = 'application/octet-stream'
    maintype, subtype = ctype.split('/', 1)
    with open(file_path, 'rb') as fp:
        email_message.add_attachment(fp.read(), maintype=maintype, subtype=subtype, filename=file_name)

# Attach the file
attach_file_to_email(email_message, attachment_path)

# Send the email
try:
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()  # Secure the connection
        server.login(smtp_username, smtp_password)  # Login to the email server
        server.send_message(email_message)  # Send the email
        print('Email sent successfully!')
except Exception as e:
    print(f'An error occurred: {e}')