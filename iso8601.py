import requests
import pytz
from time import mktime
from pytz import timezone, utc
from datetime import datetime


# fmt = '%m-%d-%Y %I:%M %p %Z%z'
fmt = '%I:%M %p %Z%z'
tz_list = ['US/Pacific', 'US/Mountain', 'US/Central', 'US/Eastern']

# now_utc = datetime.now(timezone('UTC'))
# print(f"UTC Time: {now_utc}")

# String from Epic Games (UTC). Remove "Z" to use fromisoformat conversion
utc_string = '2021-12-23T16:00:00.000Z'.replace('Z', '')
utc_datetime = datetime.fromisoformat(utc_string)
print(utc_datetime)
# Localize the datetime object so that it can be converted to other timezones
utc_localized = pytz.utc.localize(utc_datetime)
print(utc_localized)

print(utc_datetime.date().strftime('%m-%d-%Y'))
for i in tz_list:
    converted_time = utc_localized.astimezone(timezone(i)).strftime(fmt)
    print(f"{converted_time}")


# http://api.timezonedb.com/v2.1/convert-time-zone?key=1EEA5ZPUTDMA&format=json&from=America/Los_Angeles&to=Australia/Sydney&time=1464793200

# TZ_KEY = '1EEA5ZPUTDMA'
# tz_return_format = 'json'
# tz_from = 'Antarctica/Troll'
# tz_to = 'America/New_York'
# tz_dict = {
#     'PST': 'America/Los_Angeles',
#     'MST': 'America/Denver',
#     'CST': 'America/Chicago',
#     'EST': 'America/New_York'
# }

# end_date = datetime.fromisoformat('2021-12-23T16:00:00.000')
# unix_timestamp = int(end_date.timestamp())

# for key, value in tz_dict.items():
#     tz_to = tz_dict[key]
#     url = f'http://api.timezonedb.com/v2.1/convert-time-zone?key={TZ_KEY}&format={tz_return_format}&from={tz_from}&to={tz_to}&time={unix_timestamp}'
#     r_json = requests.get(url).json()
#     print("Deal ends:")
#     print(f"{key}: {datetime.fromtimestamp(r_json['toTimestamp'])}")

# # URL to convert from one timezone to another
# url = f'http://api.timezonedb.com/v2.1/convert-time-zone?key={TZ_KEY}&format={tz_return_format}&from={tz_from}&to={tz_to}&time={unix_timestamp}'
# r_json = requests.get(url).json()
# print(str(r_json))
# 
# print(f"Unix Timestamp: {unix_timestamp}")
# from_timestamp = datetime.fromtimestamp(r_json['fromTimestamp'])
# to_timestamp = datetime.fromtimestamp(r_json['toTimestamp'])

