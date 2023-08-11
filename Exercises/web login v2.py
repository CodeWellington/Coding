from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime

#get the webdriver
driver = webdriver.Chrome()

#provide the target url
url = "https://linkedin.com/home"

#open the page and pause for 1 second
driver.get(url)
time.sleep(1)

email = driver.find_element("xpath", "//*[@id='session_key']")
password = driver.find_element("xpath", "//*[@id='session_password']")

my_user = open("xxxx.txt").read()
my_password = open("xxxx.txt").read()

#send the information to the page and pause for 3 second
email.send_keys(my_user)
password.send_keys(my_password)
time.sleep(1)

#click to enter and pause for 3 seconds
submit = driver.find_element('xpath', '//*[@id="main-content"]/section[1]/div/div/form/div[2]/button').click()
time.sleep(10)
