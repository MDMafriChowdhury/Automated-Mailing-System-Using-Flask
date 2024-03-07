import pymysql

DB_HOST = '167.99.65.231'
DB_NAME = 'vendystore'
DB_USER = 'vendystoreViewer'
DB_PASSWORD = 'p@$$ofStoreV!3wer'

def delete_and_retrieve_data():
    try:
        # Connect to the database
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=3306
        )

        # Create a cursor object
        cursor = connection.cursor()





        # Define your modified SQL query
        modified_query = """
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
        """

        # Define the parameters for the modified query
        date = "12-30-2024"  # Example date
        store_code = "143"  # Example store code

        # Execute the modified query
        cursor.execute(modified_query, (date, date, store_code))

        # Fetch all the rows
        modified_rows = cursor.fetchall()

        # Print the modified data
        for row in modified_rows:
            print("Modified data:", row)

        # Close the cursor and connection
        cursor.close()
        connection.close()

    except pymysql.Error as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    delete_and_retrieve_data()
