import discord
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
import warnings
import os



client = discord.Client()
guild = discord.Guild

my_mail = os.environ.get("EMAIL_SENDER")
password = os.environ.get("PASSWORD")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    else:
        name_of_channel = message.channel.name.title()
        if message.content == "!links":
            data = pd.DataFrame(columns=["content", "time", "author"])
            limit = 1000000
            async for message in message.channel.history(limit=limit):
                if message.author != client.user:
                    words = message.content.split()
                    for word in words:
                        test_list = [".com", ".ru", ".net", ".org", ".info", ".biz", ".io", ".co", "https://", "http://"]
                        found = False
                        for extension in test_list:
                            if extension in word:
                                found = True
                                break
                        if found:
                            word = message.content
                            if message.author != client.user:

                                data = data.append({"content": word,
                                                    "time": message.created_at,
                                                    "author": message.author}, ignore_index=True)
                                if len(data) == limit:
                                    break
                        warnings.simplefilter(action="ignore", category=FutureWarning)

                        file_location = "data.csv"
                        data.to_csv(file_location, index=False)
                        # Create a multipart message
            msg = MIMEMultipart()
            body_part = MIMEText(f"Here is the file for {name_of_channel} channel's links", 'plain')
            msg['Subject'] = f"{name_of_channel} CHANNEL'S LINKS IN CSV FILE"
            msg['From'] = os.environ.get("EMAIL_SENDER")
            msg['To'] = os.environ.get("EMAIL_RECEIVER")
            # Add body to email
            msg.attach(body_part)
                        # open and read the CSV file in binary
            with open(file="data.csv", mode="rb") as file:
                # Attach the file with filename to the email
                msg.attach(MIMEApplication(file.read(), Name="Links_in_csv.csv"))

            # Create SMTP object
            with smtplib.SMTP_SSL("smtp.gmail.com") as connection:
                # connection.starttls()
                connection.login(user=my_mail, password=password)
                # Convert the message to a string and send it
                connection.sendmail(from_addr=msg['From'], to_addrs=msg['To'], msg=msg.as_string())
                print("sent")
                connection.quit()


client.run(os.environ.get("SECRET_KEY"))
