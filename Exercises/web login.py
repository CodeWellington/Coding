from selenium import webdriver
from selenium.webdriver.common.by import By

username = input("Username: ")
password = input("Passord: ")

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome()

driver.get("https://github.com/login")

# Find the username/email field and send the username to the input field.
uname = driver.find_element("id", "login_field")
uname.send_keys(username)

# Find the password input field and send the password to the input field.
pword = driver.find_element("id", "password")
pword.send_keys(password)

# Click sign in button to login the website.
driver.find_element("name", "commit").click()
# Wait for login process to complete.

# Verify that the login was successful.
error_message = "Incorrect username or password."
# Retrieve any errors found.
errors = driver.find_elements(By.CLASS_NAME, "flash-error")

# When errors are found, the login will fail.
if any(error_message in e.text for e in errors):
    print("[!] Login failed")
else:
    print("[+] Login successful")
# Close the driver
driver.close()
