    
from flask import Flask, render_template, request
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

def execute_query1(store_code, date):
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
    s.store_code = %s;

    """, (date, date, store_code))
    data = cur.fetchall()
    conn.close()
    return data

# Function to execute SQL query
def execute_query(store_code, date):
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
            s.store_code = %s
        GROUP BY 
            id.rate
    """, (date, date, store_code))
    data = cur.fetchall()
    conn.close()
    return data

  

# Function to retrieve store name based on store_id
def get_store_name(store_id):
    conn = pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=3306
    )
    cur = conn.cursor()
    cur.execute("SELECT store_name FROM store_set WHERE store_code = %s", (store_id,))
    store_name_row = cur.fetchone()  # Retrieve the result row

    # Check if store_name_row is not None
    if store_name_row:
        store_name = store_name_row[0]  # Assuming store_name is the first column in the result
    else:
        store_name = None

    conn.close()
    return store_name


# Function to send email
def send_email(data,data1, email_address, date, store_name, store_code):
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    sender_email = 'mohammadrakibur23@gmail.com'
    sender_password = 'mkia fvhe uxug znuh'

    # Calculate total quantity and total amount (taka)
    total_quantity = sum(row[4] if row[4] is not None else 0 for row in data)  # Summing the quantity (assuming it's the 5th column)
    total_amount = sum(row[6] if row[6] is not None else 0 for row in data)  # Summing the total amount (taka) (assuming it's the 7th column)
  # Summing the total amount (taka) (assuming it's the 7th column)

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
        <table>
            <tr>
                <th>Date</th>
                <th>Invoice</th>
                <th>Machine Name</th>
                <th>Product Name</th>
                <th>Quantity</th>
                <th>Rate (taka)</th>
                <th>Total Amount (taka)</th>
            </tr>
    """

    # Adding transaction details
    for row in data1:
        body += "<tr>"
        for item in row:
            body += f"<td>{item}</td>"
        body += "</tr>"

    # Closing the HTML body
    body += """
        </table>
    </body>
    </html>
    """

    # Attach the HTML content to the email
    msg.attach(MIMEText(body, 'html'))

    # Sending the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, email_address, msg.as_string())
    server.quit()


# Route for the main page
@app.route("/", methods=["GET", "POST"])
def index():
    try:
        notObj = {
            "notObj": [  
                {"channel":"email", "value":"rubayet.stl@squaregroup.com","store_code": "143"},  
                {"channel":"email", "value":"biz@vendy.ltd","store_code": "143"},
                {"channel":"email", "value":"rubayet.stl@squaregroup.com","store_code": "144"},  
                {"channel":"email", "value":"biz@vendy.ltd","store_code": "144"},
                {"channel":"email", "value":"rubayet.stl@squaregroup.com","store_code": "145"},  
                {"channel":"email", "value":"biz@vendy.ltd","store_code": "145"},
                {"channel":"email", "value":"rubayet.stl@squaregroup.com","store_code": "146"},  
                {"channel":"email", "value":"biz@vendy.ltd","store_code": "146"},
                {"channel":"email", "value":"niloykhan112026@gmail.com","store_code": "146"},
                
       
            ]
        }
        for item in notObj["notObj"]:
            if item["channel"] == "email":
                store_code = item["store_code"]
                date = datetime.now().strftime('%m-%d-%Y')
                #date='04/01/2024'
               
                print(date) # Modify this line to use the current date
                data = execute_query(store_code, date)
                data1 = execute_query1(store_code, date)
                store_name = get_store_name(store_code)
                if data:
                    send_email(data, data1, item["value"], date, store_name, store_code)
                else:
                    send_email([(date, None, store_name, None, None, None, 0)], [], item["value"], date, store_name, store_code)
            elif item["channel"] == "sms":
                # Logic for sending SMS
                pass
        return "Reports sent successfully!"
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    app.run(debug=True, port=8080)
