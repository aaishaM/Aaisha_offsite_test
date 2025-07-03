#import libraries
import requests
from bs4 import BeautifulSoup
import pandas as pd
import smtplib
import os
from email.mime.text import MIMEText
from  email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


"""Function to get stock price from provided URL using web scrapping
    Returns current stock price"""

def get_stock_price():
    yahoo_url="https://finance.yahoo.com/quote/AAPL?p=AAPL"
    headers= {"User-Agent" : "Mozilla/5.0",
                'Cache-Control': 'no-cache',
                'Pragma' : 'no-cache'}
    response= requests.get(yahoo_url,headers=headers)
    soup = BeautifulSoup(response.text,'html.parser')
    stock_price=soup.find('span',{'data-testid':'qsp-price'})

    if stock_price:
        sp_text=stock_price.text.strip()
        return float(sp_text.replace(',',''))
    else:
        raise Exception("Stock price not found")





"""Data Reconciliation:
   Input Current Price dervied from the web page.
   Returns previous price from csv, difference and change in percentage"""

stock_csv=('data/stock_data.csv')

def check_price_change(current_price):
    df=pd.read_csv(stock_csv)

    apple_price=df[df['Company']=='AAPL']['Price']
    if apple_price.empty:
        print("No previous records")
        return None,None,None

    previous_price=float(apple_price.iloc[-1])
    difference=current_price-previous_price
    percent_change=(difference/previous_price)*100.
    return previous_price,difference,percent_change




"""Send Email with the change in stock price"""

load_dotenv(override=True)

EMAIL_SENDER= os.environ.get("EMAIL_SENDER")
EMAIL_RECEIVER=os.environ.get("EMAIL_RECEIVER")
EMAIL_PASSWORD=os.environ.get("EMAIL_PASSWORD")

SMTP_SERVER="smtp.gmail.com"
SMTP_PORT=587
threshold=1.0

def send_mail(current_price,previous_price,difference,percentage_change):

    subject= f"Apple Products Stock Price Change Alert"
    body = f"""Stock Price Change Triggered:
    Current Price : ${current_price:.2f}
    Previous Price : ${previous_price:.2f}
    Amount Changed : ${difference:.2f}
    """
    msg=MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject']=subject
    msg.attach(MIMEText(body,'plain'))

    try:
        with smtplib.SMTP(SMTP_SERVER,SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER,EMAIL_PASSWORD)
            server.send_message(msg)
            print("Email Sent")
    except Exception as e:
        print(f"Failed to send mail : {e}")



"""Main Function
    Prints Current price, previous price, difference, and percentage of change
    Checks against predefined threshold and sends email if percentage of change is higher than threshold"""

threshold_percent=1.0
def main():
    try:
        current_price= get_stock_price()
        prev_price, diff, per_diff = check_price_change(current_price)

        print(f"Current Price : $ {current_price:.2f}")
        print(f"Previous Price : $ {prev_price:.2f}")
        print(f"Price Difference : $ {diff:.2f}")
        print(f"Percentage of Difference : {per_diff:.2f} %")

        if per_diff>threshold_percent:
            send_mail(current_price,prev_price,diff,per_diff)
        else:
            print("Change did not exceed threshold value. Email not sent.")


    except Exception as e:
        print(f"Error : {e}")
if __name__ == "__main__":
    main()