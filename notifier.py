

from Google import Create_Service
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# https://www.reddit.com/r/Python/comments/8gb88e/free_alternatives_to_twilio_for_sending_text/
# Based off this person's video https://www.youtube.com/watch?v=44ERDGa9Dr4


CLIENT_SECRET_FILE = 'credentials.json'
API_NAME = 'gmail'
API_VERSION = 'v1'
SCOPES = ['https://mail.google.com/']


# Carrier lookup https://avtech.com/articles/138/list-of-email-to-sms-addresses/
CARRIERS = {
	'att':    '@mms.att.net',
	'tmobile':' @tmomail.net',
	'verizon':  '@vtext.com',
	'sprint':   '@page.nextel.com'
}


class Notifier:
	def __init__(self):
		self.service = Create_Service(CLIENT_SECRET_FILE, API_NAME, API_VERSION, SCOPES)

	def notify(self, phone_number, phone_provider, message):
		emailMsg = message
		mimeMessage = MIMEMultipart()
		mimeMessage['to'] = str(phone_number)+CARRIERS[phone_provider]


		mimeMessage['subject'] = ''
		mimeMessage.attach(MIMEText(emailMsg, 'plain'))
		raw_string = base64.urlsafe_b64encode(mimeMessage.as_bytes()).decode()

		message = self.service.users().messages().send(userId='me', body={'raw': raw_string}).execute()
		print(message)
