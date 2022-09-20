import yaml
import urllib3
import json
import smtplib, ssl
from email.mime.text import MIMEText


# Load email and password from credentials yaml.
with open("credentials.yaml", "r") as f:
    credentials = yaml.safe_load(f)

sender_email = credentials["sender_email"]
receiver_email = credentials["receiver_email"]
password = credentials["password"]

# Open the settings.yaml file and import the json_url variable.
with open("settings.yaml", "r") as f:
    settings = yaml.load(f, Loader=yaml.FullLoader)
    json_url = settings["json_url"]

# Use the urllib3 library to get the json_url and store it in a file.
http = urllib3.PoolManager()
r = http.request('GET', json_url)
with open("data.json", "wb") as f:
    f.write(r.data)

# Open the data.json file and import the data.
with open("data.json", "r") as f:
    data = json.load(f)

set_of_names = set()
# Loop through the results list and extract the nameEn value.
# Only take the string after the last colon.
for result in data["results"]:
    name = result["nameEn"].split(":")[-1]
    # Remove the leading and trailing spaces.
    name = name.strip()
    set_of_names.add(name)

# Load the set of names from the names.txt file into a set.
with open("names.txt", "r") as f:
    previous_names = set(f.read().splitlines())

# Compare the two sets and if there is a difference, save the difference in a variable.
difference = set_of_names.difference(previous_names)

# If difference is not empty, send an email via gmail.
if difference:
    msg = MIMEText("""
    The following age ranges are now available:
    {}
    """.format(difference))
    msg['Subject'] = 'Difference(s) detected in vaccine availability'
    msg['From'] = sender_email
    msg['To'] = receiver_email

    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.ehlo()
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 
        
# Save the set_of_names to a file with a newline.
with open("names.txt", "w") as f:
    for name in set_of_names:
        f.write(name+'\n')
