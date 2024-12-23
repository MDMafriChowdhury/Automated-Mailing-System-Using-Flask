import json
from flask import Flask, request
import pymysql
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

app = Flask(__name__)

DB_HOST = ''
DB_NAME = ''
DB_USER = ''
DB_PASSWORD = ''

def execute_query1(store_codes, date):
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=3306
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            %s AS DATE,
            i.invoice,
            s.store_name,
            p.product_name,
            id.quantity,
            id.rate,
            i.total_amount
        FROM 
            store_set s
        LEFT JOIN 
            invoice i ON i.store_id = s.store_id AND i.date = %s
        LEFT JOIN 
            invoice_details id ON i.invoice_id = id.invoice_id
        LEFT JOIN 
            product_information p ON id.product_id = p.product_id
        WHERE 
            s.store_code IN %s;
    """, (date, date, tuple(store_codes.split(','))))
    data = cur.fetchall()
    conn.close()
    return data

# Function to execute SQL query 2
def execute_query(store_codes, date):
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=3306
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            %s AS DATE,
            i.invoice,
            s.store_name,
            p.product_name,
            SUM(id.quantity) AS total_quantity,
            id.rate,
            SUM(i.total_amount) AS total_amount
        FROM 
            store_set s
        LEFT JOIN 
            invoice i ON i.store_id = s.store_id AND i.date = %s
        LEFT JOIN 
            invoice_details id ON i.invoice_id = id.invoice_id
        LEFT JOIN 
            product_information p ON id.product_id = p.product_id
        WHERE 
            s.store_code IN %s
        GROUP BY 
            id.rate;
    """, (date, date, tuple(store_codes.split(','))))
    data = cur.fetchall()
    conn.close()
    return data


def get_notification_channels(store_code):
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=3306
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT notificaitonChannels
        FROM store_set
        WHERE store_code = %s;
    """, (store_code,))
    notification_channels = cur.fetchone()[0]  # Assuming notificationChannels is a single value
    conn.close()
    return notification_channels



# Function to send email
def send_email(data, data1, email_address, date, store_name, store_code):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'it@onutiative.com'
    sender_password = 'auqn yqet rsla tone'

    # Calculate total quantity and total amount (taka)
    total_quantity = sum(row[4] if row[4] is not None else 0 for row in data)  # Summing the quantity (assuming it's the 5th column)
    total_amount = sum(row[6] if row[6] is not None else 0 for row in data)  # Summing the total amount (taka) (assuming it's the 7th column)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = email_address
    msg['Subject'] = f"(No reply) Sales Report - {date} - {store_name}"

    # Constructing the HTML table for the email body
    body = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Daily Sales Report</title>
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
            }}
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
                text-align: left;
            }}
            th {{
                background-color: #f2f2f2;
            }}
        </style>
    </head>
    <body>
        <h1>Vendy Daily Sales Report</h1>
        <p>Report Date: {date}</p>
        <table>
            <tr>
                <th>Machine Code</th>
                <th>Store Name</th>
            </tr>
            <tr>
                <td>{store_code}</td>
                <td>{store_name}</td>
            </tr>
            <tr>
                <th>Total Quantity</th>
                <th>Total Sold (taka)</th>
            </tr>
            <tr>
                <td>{total_quantity}</td>
                <td>{total_amount}</td>
            </tr>
            <!--  <tr>
                <th>Last Refill Quantity</th>
                <th>Last Refill Date</th>
            </tr>
            <tr>
                <td></td>
                <td></td>
            </tr> -->
        </table>
        <h3>Last Days Transaction Details:</h3>
        
    """
    # Sorting unique store names by the numerical part
    # Sorting unique store names by the last two or three digits of the store code
    unique_store_names = sorted(set(row[2] for row in data1), key=lambda x: int(''.join(filter(str.isdigit, x))[-3:]))



    # Generate table for each store
    for store_name in unique_store_names:
        store_data = [row for row in data1 if row[2] == store_name]
        body += f"""
        <h2>{store_name}</h2>
        <table>
            <tr>
                <th>Date</th>
                <th>Invoice</th>
                <th>Machine Name</th>
                <th>Product Name</th>
                <th>Quantity</th>
                <th>Rate (taka)</th>
                <th>Amount (taka)</th>
            </tr>
        """

        for row in store_data:
            body += "<tr>"
            for item in row:
                body += f"<td>{item}</td>"
            body += "</tr>"

        body += "</table>"

    body += """
    </body>
    </html>
    """

    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, email_address, msg.as_string())
    server.quit()

import re
def remove_numbers(store_name):
    return re.sub(r'\d+', '', store_name)
    
def extract_numerical_part(store_name):
    # Extract numerical part from store name
    numerical_part = re.findall(r'\d+', store_name)
    if numerical_part:
        return int(numerical_part[0])
    else:
        return float('inf')     

# Route for the main page
@app.route("/get_data", methods=["POST"])
def get_data():
    try:
        data = request.json
        store_codes = data.get('store_codes')
        first_store_code = store_codes.split(',')[0]
        notObj=get_notification_channels(first_store_code)
        notObj = json.loads(notObj)
        
        
        for item in notObj['notObj']:
            if item["channel"] == "email":
                email_address = item["value"]
                date = datetime.now().strftime('%m-%d-%Y')
                email_data = execute_query(store_codes, date)
                email_data1 = execute_query1(store_codes, date)
                store_name = remove_numbers(email_data[0][2]) if email_data else None

                if email_data:
                    send_email(email_data, email_data1, email_address, date, store_name, store_codes)
                else:
                    send_email([(date, None, store_name, None, None, None, 0)], [], email_address, date, store_name, store_codes)
            elif item["channel"] == "sms":
                # Logic for sending SMS
                pass
        return "Reports sent successfully!"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, port=8080)


