# Covid Vaccine Tracker

A simple set of scripts to periodically check for Covid-19 vaccine availability and automatically email people a list of vaccination centers, timings, available capacity, and price.

This works based on the CoWIN Public API provided by [API Setu](https://apisetu.gov.in/public/api/cowin). This only works for locations in India. I am not sure whether/how other countries make this data available publicly through an API. But I am sure it should be pretty easy to make this work for other locations with a little know-how.

![image](https://github.com/MaverickAjay/Personal-Projects/assets/71900138/d4b2f84f-e6d4-4dd7-b6ac-3f82a421b5c2)

## Components

The program is made of three simple components:

- `get_centers_list.py` works like a command like tool using `argparse` and gets data from the above mentioned API.
- `subscribers.json` is where details and preferences of each user are stored.
- `main.py` is the main component that reads the JSON file and gets relevant data using the API and send out emails when vaccines are available.

### get_centers_list.py

Syntax:

```
usage: get_centers_list.py [-h] [-D DISTRICT_ID] {COVISHIELD,COVAXIN} {1,2} {18,45}

Search for COVID-19 vaccinations...

positional arguments:
  {COVISHIELD,COVAXIN}  Vaccine type needed -- COVISHIELD/COVAXIN
  {1,2}                 Vaccine dose needed -- 1/2
  {18,45}               Age group of the person -- 18+/45+

optional arguments:
  -h, --help            show this help message and exit
  -D DISTRICT_ID, --district-id DISTRICT_ID
                        District ID number
```

Example usage:

```
$ python get_centers_list.py COVAXIN 1 18 -D 571
```

This returns a JSON string containing vaccination data for the next 7 days in that particular district (571) for COVAXIN Dose 1 for people belonging to 18+ age group.

By the way district codes can be found using the same API link mentioned above.

### subscribers.json

This file stores the details and preferences for the users who have opted to receive reminder emails. Each user takes the following template.

```
{
    "name": "Foo",
    "email": "foo@example.com",
    "vaccine": "COVAXIN",
    "dose": 1,
    "age_group": 18,
    "district": 571
}
```

Add as many users as you would like to this JSON file.

### main.py

This is the main program that reads the JSON file and gets relevant vaccine data by launching a `subprocess` of `get_centers_list.py` using the syntax mentioned above and sends out an email to the subscribers using SMTP library.

Just replace the `SENDER` variable in `main.py` using the email ID with which you want to send out reminders. And replace `PASSWORD` with your corresponding password. The options are configured to work with Gmail accounts. But setting up a different provider wouldn't be a big deal.

Also, change the `CHECK_INTERVAL` to whatever duration you would like the program to wait between each check.

## Using the tracker

Once you have configured the above options to your needs, all you need to do is to run the `main.py` file.

```
$ python main.py
```

The program will then start running and it will check for vaccines periodically based on your `CHECK_INTERVAL` and it will send out emails to everyone in the `subscribers.json` file whenever vaccines opted for is available for booking.

## Resources

- Check out [this](https://realpython.com/python-send-email/) great Real Python tutorial on how to send emails using Python.

## Things to know

- If you want to run this 24 hrs without having to keep you PC running, you can use Amazon AWS EC2 instance. You can get a free tier with a new account and it will let you run an instance all day long for 1 year for free!
- Gmail has a limit of 500 emails per day. So you may have problems when you are trying to send out emails to a lot of people or when your `CHECK_INTERVAL` is too low. A dumb solution would be to have multiple Gmail accounts and cycle between them each time you are trying to send out an email. Or opt for a better paid email API that has more relaxed limits.


