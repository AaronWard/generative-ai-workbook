import time
import sqlite3

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('tweets_4.db')
cursor = conn.cursor()

# Create the table (if it doesn't exist)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tweets (
        id INTEGER PRIMARY KEY,
        handle TEXT,
        content TEXT,
        url TEXT
    )
''')
conn.commit()

def user_details():
    twitter_username = input("Please type your Twitter username >> ")
    twitter_password = input("Please type your Twitter password >> ")
    return twitter_username, twitter_password

def scrape_replies(tweet_url, twitter_username, twitter_password):
    wait = WebDriverWait(driver, 30)  # Increased wait time to 30 seconds

    # Navigate to Twitter login page
    driver.get("https://twitter.com/login")

    # Find username field and input username
    username = wait.until(EC.presence_of_element_located((By.NAME, 'text') or (By.NAME, 'session[username_or_email]')))
    username.send_keys(twitter_username)
    username.send_keys(Keys.RETURN)  # Press enter key

    # Find password field and input password
    password = wait.until(EC.presence_of_element_located((By.NAME, 'password')))
    password.send_keys(twitter_password)
    password.send_keys(Keys.RETURN)  # Press enter key to log in

    # Check if login was successful
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="AppTabBar_Home_Link"]')))
        print("Login successful")
    except TimeoutException:
        print("Login failed")
        return

    # Navigate to the specific tweet URL after logging in
    driver.get(tweet_url)

    # Set to keep track of collected replies
    collected_replies = set()

    def collect_replies():
        try:  # Waits for replies to load
            replies = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-testid="tweet"]')))
        except TimeoutException:
            print("No more replies found")
            replies = []

        new_replies = False

        for reply in replies:
            # Extract reply text and Twitter handle
            try:
                reply_text = reply.find_element(By.XPATH, './/div[@lang]').text
                twitter_handle = reply.find_element(By.XPATH, './/span[contains(text(), "@")]').text

                # Extract reply_id from the href attribute of the a element containing the reply text
                a = reply.find_element(By.XPATH, './/a[contains(@href, "/status/")]')
                href = a.get_attribute('href')
                reply_id = href.split('/')[-1]

                # Construct the reply URL
                reply_url = f'https://twitter.com/{twitter_handle}/status/{reply_id}'

                # Debug print to verify reply structure
                print(f"Collected reply: handle={twitter_handle}, content={reply_text}, url={reply_url}")

            except NoSuchElementException:
                continue

            # If the reply is not already collected, process it
            reply_data = (twitter_handle, reply_text, reply_url)
            if reply_data not in collected_replies:
                print("Handle:", twitter_handle)
                print("Content:", reply_text)
                print("URL:", reply_url)
                print("--------------------")
                # Add the reply data to the collected replies set
                collected_replies.add(reply_data)

                # Insert the reply into the database
                cursor.execute('INSERT INTO tweets (handle, content, url) VALUES (?, ?, ?)', (twitter_handle, reply_text, reply_url))
                conn.commit()

                new_replies = True

        return new_replies

    # Scroll down and collect top-level replies
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        try:
            new_replies = collect_replies()

            # Scroll down
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait for some time to allow replies to load
            time.sleep(5)

            # Calculate new scroll height and compare with last scroll height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height and not new_replies:
                break
            last_height = new_height

        except WebDriverException as e:
            print(f"WebDriverException encountered: {e}")
            break

    # Expand and collect nested replies
    for reply in collected_replies.copy():
        try:
            driver.get(reply[2])  # Navigate to the reply URL

            # Wait for nested replies to load
            time.sleep(3)
            collect_replies()
        except WebDriverException as e:
            print(f"WebDriverException encountered while navigating to reply URL: {e}")
            continue

username, password = user_details()

# Setup ChromeDriver service
service = Service(ChromeDriverManager().install())

# Create an instance of Chrome WebDriver
driver = webdriver.Chrome(service=service)

# URL of the tweet you want to scrape replies for
tweet_url = ""

# Call the function & if there is an error this ensures the database closes correctly
try:
    scrape_replies(tweet_url, username, password)
finally:
    cursor.close()
    conn.close()

input("Press enter to close the browser")
driver.quit()  # Close the WebDriver
