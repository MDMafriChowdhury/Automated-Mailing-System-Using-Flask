**README.md**

**Title: Automated Sales Report Sender using Flask**

**Description:**
This project provides a Flask-based application to automate the sending of daily sales reports via email. The application fetches data from a MySQL database, generates an HTML email containing sales information, and sends it to designated email addresses. The automation can be integrated with cPanel's cron jobs for scheduled execution.

**Prerequisites:**
- Python 3.x installed on your system.
- Access to a MySQL database.
- An SMTP server for sending emails.
- Basic knowledge of Flask and MySQL.

**Setup:**
1. Clone or download the project repository.

2. Install the required Python packages using pip:
    ```
    pip install Flask pymysql
    ```

3. Update the following variables in `app.py` with your MySQL database credentials:
    - `DB_HOST`: MySQL host address.
    - `DB_NAME`: Name of the MySQL database.
    - `DB_USER`: MySQL username.
    - `DB_PASSWORD`: MySQL password.

4. Update the SMTP server details and sender email credentials in the `send_email` function in `app.py`.

5. Modify the `notObj` dictionary in the `index` function in `app.py` to include the email addresses and store codes for sending reports.

6. Test the application locally:
    ```
    python app.py
    ```

7. Ensure the Flask application runs without errors.

**Deployment:**
1. Upload the `app.py` file to your cPanel's File Manager.

2. Set up a virtual environment in cPanel to install dependencies:
    ```
    virtualenv <your_virtualenv_name>
    ```

3. Activate the virtual environment:
    ```
    source <your_virtualenv_name>/bin/activate
    ```

4. Install Flask and pymysql within the virtual environment:
    ```
    pip install Flask pymysql
    ```

5. Configure a cron job in cPanel to run the Flask application at the desired schedule. For example, to run the application daily, add the following cron job:
    ```
    0 0 * * * /path/to/python3 /path/to/app.py
    ```

Replace `/path/to/python3` with the path to the Python 3 interpreter and `/path/to/app.py` with the absolute path to your `app.py` file.

**Usage:**
- The Flask application is designed to run automatically at scheduled intervals.
- It retrieves sales data from the MySQL database, constructs an HTML email, and sends it to the specified email addresses.
- Check the designated email addresses for the received sales reports.

**Contributing:**
Contributions to the project are welcome. Feel free to submit bug reports, feature requests, or pull requests.

**License:**
This project is licensed under the MIT License. See the LICENSE file for details.
