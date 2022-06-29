import json
import argparse
from pprint import pprint
from datetime import datetime
import urllib.request as request


def get_request_string(district_id, date):
	return (f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/"
		f"calendarByDistrict?district_id={district_id}&date={date}")


def get_todays_date():
	return datetime.today().strftime("%d-%m-%Y")


def parse_command_line():
	parser = argparse.ArgumentParser(description='Search for COVID-19 vaccinations...')

	parser.add_argument("vaccine_type", choices=['COVISHIELD', 'COVAXIN'],
						help="Vaccine type needed -- COVISHIELD/COVAXIN")

	parser.add_argument("dose", type=int, choices=[1, 2], help="Vaccine dose needed -- 1/2")

	parser.add_argument("age_limit", choices=[18, 45],
						help="Age group of the person -- 18+/45+",
						type=int)

	parser.add_argument("-D", '--district-id', type=int, default=571, help="District ID number")

	return parser.parse_args()


def main():
	args = parse_command_line()

	site = get_request_string(args.district_id, get_todays_date())
	hdr = {
		'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) " \
			"Chrome/23.0.1271.64 Safari/537.11',
    	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    	'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
   		'Accept-Encoding': 'none',
		'Accept-Language': 'en-US,en;q=0.8',
    	'Connection': 'keep-alive',
	}

	req = request.Request(site, headers=hdr)
	page = request.urlopen(req)

	vaccines = json.loads(page.readline())


	matching_centers = [ ]

	for center in vaccines['centers']:
		for session in center['sessions']:
			if session['min_age_limit'] == args.age_limit:
				if session['vaccine'] == args.vaccine_type:
					if session[f"available_capacity_dose{args.dose}"] > 0:
						matching_centers.append(center)
						break

	details = {'centers': matching_centers}
	print(details)


	with open('convert.txt', 'w') as convert_file:
	     convert_file.write(json.dumps(details))


if __name__ == '__main__':
	main()
