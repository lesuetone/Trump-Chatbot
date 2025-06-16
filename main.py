
import requests
import sys
from datetime import datetime
import pytz
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(subject, body, to_email, from_email, from_password, smtp_server="smtp.gmail.com", smtp_port=587):
    """
    Send an email with the extracted variables.
    
    Args:
        subject (str): Email subject
        body (str): Email body content
        to_email (str): Recipient email address
        from_email (str): Sender email address
        from_password (str): Sender email password or app password
        smtp_server (str): SMTP server address
        smtp_port (int): SMTP server port
    """
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        msg.attach(MIMEText(body, 'plain'))
        
        # Setup SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable encryption
        server.login(from_email, from_password)
        
        # Send email
        text = msg.as_string()
        server.sendmail(from_email, to_email, text)
        server.quit()
        
        print(f"Email sent successfully to {to_email}")
        
    except Exception as e:
        print(f"Error sending email: {e}")

def fetch_website_content(url, max_chars=100000, stop_date=None):
    """
    Fetch content from a website and return the first max_chars characters.
    Optionally stop when a specific date is found.
    
    Args:
        url (str): The URL to fetch content from
        max_chars (int): Maximum number of characters to return
        stop_date (str): Date string to stop at (format: YYYY-MM-DD)
    
    Returns:
        str: The content from the website
    """
    try:
        # Send GET request to the URL
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        content = response.text
        
        # If stop_date is provided, find where to stop
        if stop_date:
            stop_pattern = f'"date":"{stop_date}"'
            stop_index = content.find(stop_pattern)
            if stop_index != -1:
                content = content[:stop_index]
                # Remove first character and last two characters
                if len(content) >= 3:
                    content = content[1:-2]
                elif len(content) >= 1:
                    content = content[1:]
        
        # Limit to max_chars
        content = content[:max_chars]
        
        return content
    
    except requests.exceptions.RequestException as e:
        return f"Error fetching content: {e}"

def main():
    # Default URL - the one you provided
    default_url = "https://media-cdn.factba.se/rss/json/trump/calendar-full.json"
    
    # Check if a URL was provided as command line argument
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = default_url
    
    
    # Get current date in EDT timezone
    edt = pytz.timezone('US/Eastern')
    current_date_edt = datetime.now(edt)
    
    # Split date into separate variables
    current_year = current_date_edt.year
    current_month = current_date_edt.month
    current_day = current_date_edt.day
    
    # Calculate stop date (current day minus 1)
    stop_day = current_day - 1
    stop_date = f"{current_year}-{current_month:02d}-{stop_day:02d}"
    
    # Fetch content with stop date
    content = fetch_website_content(url, 100000, stop_date)
    
    # Replace all { and " symbols, : symbols, commas with spaces, and remove last character
    cleaned_content = content.replace('{', ' ').replace('"', ' ').replace(':', ' ').replace(',', ' ')
    
    # Remove double spaces and ensure maximum one space apart
    import re
    cleaned_content = re.sub(r' +', ' ', cleaned_content)
    
    # Remove the last character if content exists
    if len(cleaned_content) > 0:
        cleaned_content = cleaned_content[:-1]
    
    # Extract all words and numbers as variables
    words_and_numbers = cleaned_content.split()
    
    # Extract specific patterns and collect them for email
    extracted_variables = []
    i = 0
    while i < len(words_and_numbers):
        item = words_and_numbers[i]
        
        # Next 3 variables after 'time'
        if item == 'time' and i + 3 < len(words_and_numbers):
            time_vars = f"{words_and_numbers[i+1]} {words_and_numbers[i+2]} {words_and_numbers[i+3]}"
            print(time_vars)
            extracted_variables.append(f"Time: {time_vars}")
        
        # Variables between 'details' and 'location'
        elif item == 'details':
            details_vars = []
            j = i + 1
            while j < len(words_and_numbers) and words_and_numbers[j] != 'location':
                details_vars.append(words_and_numbers[j])
                j += 1
            if details_vars:
                details_text = ' '.join(details_vars)
                print(details_text)
                extracted_variables.append(f"Details: {details_text}")
        
        # Variables between 'location' and 'coverage'
        elif item == 'location':
            location_vars = []
            j = i + 1
            while j < len(words_and_numbers) and words_and_numbers[j] != 'coverage':
                location_vars.append(words_and_numbers[j])
                j += 1
            if location_vars:
                location_text = ' '.join(location_vars)
                print(location_text)
                extracted_variables.append(f"Location: {location_text}")
        
        i += 1
    
    # Email configuration - Update these with your email details
    TO_EMAIL = "joebonnaud@gmail.com"  # Change this to your recipient email
    FROM_EMAIL = "achatbot040@gmail.com"  # Change this to your sender email
    FROM_PASSWORD = "gabf mptn ayep izjd"  # Use an app password for Gmail
    
    # Create email content
    email_subject = f"Extracted Variables - {current_date_edt.strftime('%Y-%m-%d')}"
    email_body = "Extracted Variables:\n\n" + "\n".join(extracted_variables)
    
    # Send email
    send_email(email_subject, email_body, TO_EMAIL, FROM_EMAIL, FROM_PASSWORD)

if __name__ == "__main__":
    main()
