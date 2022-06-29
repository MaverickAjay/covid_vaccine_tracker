import json
import os
import smtplib
import ssl
import subprocess
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pprint import pprint
from time import sleep


PORT = 465
SENDER = "vaccinee4youu@gmail.com"
PASSWORD = 'Maverick#18'

CHECK_INTERVAL = 300


def main():
	this_file = os.path.realpath(__file__)
	script_path = os.path.join(os.path.dirname(this_file), 'get_centers_list.py')

	with open(os.path.join(os.path.dirname(this_file), "subscribers.json"), "r") as f:
		subscribers = json.load(f)


	context = ssl.create_default_context()
	with smtplib.SMTP_SSL("smtp.gmail.com", PORT, context=context) as server:
		server.login(SENDER, PASSWORD)

		for subscriber in subscribers['subscribers']:
			message = MIMEMultipart("alternative")
			message["Subject"] = f"{subscriber['vaccine']} availability list"
			message["From"] = SENDER
			message["To"] = f"{subscriber['name']} <{subscriber['email']}>"

			p = subprocess.run(["python" , f"{script_path}" , f"{subscriber['vaccine']}" , f"{subscriber['dose']}", f"{subscriber['age_group']}", "-D" , f"{subscriber['district']}"])
			# q = p.stdout.replace(b" ",b"")
			# r = q.replace(b"\'", b'\"')
			with open('convert.txt') as f:
			    data = f.read()

			# print("Data type before reconstruction : ", type(data))

			# reconstructing the data as a dictionary
			matching_centers = json.loads(data)

			# print("Data type after reconstruction : ", type(js))
			print(matching_centers)

			# try:

			# matching_centers = json.loads(r.decode('utf-8'))
			# except:
			# 	matching_centers = {'centers': [ ]}

			if matching_centers['centers']:
				center_list = ""

				for center in matching_centers["centers"]:
					center_list += "<p>"

					center_list += f"<h2>{center['name']}</h2>"
					center_list += f"<b>Center ID</b>: {center['center_id']}<br>"
					center_list += f"<b>Address</b>: {center['address']} - {center['pincode']}<br>"
					center_list += f"<b>Time</b>: {center['from']} to {center['to']}<br>"
					center_list += f"<b>Fee type</b>: {center['fee_type']}<br>"

					if center['fee_type'] == "Paid":
						center_list += f"<b>Price</b>: ₹{center['vaccine_fees'][0]['fee']}<br>"

					session_num = 0
					for session in center['sessions']:
						if session['min_age_limit'] == subscriber['age_group']:
							if session['available_capacity'] > 0:
								session_num += 1
								center_list += f"<h3>Session {session_num}</h3>"
								center_list += f"<b>Date</b>: {session['date']}<br>"
								center_list += f"<b>Vaccine type</b>: {session['vaccine']}<br>"
								center_list += f"<b>Available capacity</b>: {session['available_capacity']}<br>"
								center_list += f"<b>Dose 1</b>: {session['available_capacity_dose1']}<br>"
								center_list += f"<b>Dose 2</b>: {session['available_capacity_dose2']}<br>"
								center_list += f"<b>Age limit</b>: {session['min_age_limit']}+<br>"
								center_list += f"<b>Slots</b>"

								center_list += "<ul>"
								for slot in session['slots']:
									center_list += f"<li>{slot}</li>"
								center_list += "</ul>"


					center_list += '<br>'
					center_list += "</p>"


				text = f"""
					<html>
						<body>

						Dear {subscriber['name']},<br>

						As per you request for COVID-19 vaccine ({subscriber['vaccine']}) availability \
						reminder, we have compiled a list of centers where you can get vaccinated. <br> <br>

						<i>

						Please do not reply to this email. If you need any clarification write a separate \
						email to contact@example.com.

						</i>

						{center_list}

						Kind Regards,<br>
						Covid Vaccine Reminder<br>

						</body>
					</html>
					"""

				# text = text.replace("\n", rand_str)
				# text = text.replace(">", rand_str_1)

				message.attach(MIMEText(text, "html"))
				pprint(str(text))

				try:
					server.sendmail(SENDER, subscriber['email'], message.as_string())
					# print(f"{datetime.now().strftime('%-I:%M:%S %p')}    Sent mail to {subscriber['email']} ({subscriber['vaccine']})\n")
				except Exception as e:
					print(f"Cannot send mail to {subscriber['email']}\n Exception: {str(e)}")

	pprint(matching_centers)

if __name__ =='__main__':
	run_count = 0
	while True:
		run_count += 1
		# print(f"\n{datetime.now().strftime('%-I:%M:%S %p')}    Run count: {run_count}")
		main()
		sleep(CHECK_INTERVAL)
