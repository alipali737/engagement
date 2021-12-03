import os, platform
import random as rd
import re as regex
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# TODO : Add way to validate engagement
# TODO : Validate its actually on a login page or log out first

# Selenium Implementation #
# Create and return a new chrome browser
def CreateBrowser():
    # Create a new chrome instance
    browser = webdriver.Chrome()
    print("Browser created!")
    return browser

# Attempt to login via the browser page
def BrowserLoginAttempt(browser):
    # Open the login page
    browser.get(("https://winchester.instructure.com/"))

    # Get the input field elements
    usernameField = browser.find_element(By.ID,"userNameInput")
    passwordField = browser.find_element(By.ID,"passwordInput")

    # Fill the username and password
    usernameField.send_keys(creds[0])
    passwordField.send_keys(creds[1])

    # Find and click submit button
    submitButton = browser.find_element(By.ID,"submitButton")
    submitButton.click()

    # Wait for a max of 10 seconds for the canvas page to load
    _ = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "application")))

    print("Logged in!")

# Access a canvas resource at random
def OpenRandomCanvasResource(browser):
    # Course IDs for all 3 modules
    courseIDList = ["15537","15919","15536"]

    # Request a random course page
    resourceURL = "https://winchester.instructure.com/courses/"+rd.choice(courseIDList)+"/modules"
    browser.get(resourceURL)

    # Get a list of all resources in the module
    itemsList = browser.find_elements(By.CLASS_NAME,"context_module_item")
    
    # Chose a resource at random an get its id
    itemID = regex.search('\d+',rd.choice(itemsList).get_attribute("id"))
    
    # Append URL and request resource page
    resourceURL += "/items/"+itemID.group(0)
    browser.get(resourceURL)

    # Wait for a max of 10 seconds for the canvas page to load
    _ = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.ID, "application")))

    print("Resource Accessed!")

# Logout once on the intranet
def BrowserLogout(browser):
    # Go to canvas logout page
    browser.get(("https://winchester.instructure.com/logout"))

    # Find and click the logout button
    logoutButton = browser.find_element(By.ID,"Button--logout-confirm")
    logoutButton.click()
    print("logged out!")

# Get username and password as touple
def GetCreds():
    # Add your winchester student email here
    username = "...@unimail.winchester.ac.uk"

    # Add you password here if you wish to hardcode them otherwise leave blank for pull from 1password CLI
    password = ""

    # Test if password is blank, if so attempt to get from 1password CLI
    # To setup please configure the vars below
    opSessionName = ""
    opUniLoginItemName = ""

    if password == "":
        # If the platform is windows 'eval' doesn't exist
        if platform.system() == "Windows":
            stream = os.popen("Invoke-Expression $(op signin %s) && op get item --fields password %s" %(opSessionName, opUniLoginItemName))
        else:
            stream = os.popen("eval $(op signin %s) && op get item --fields password %s" %(opSessionName, opUniLoginItemName))
        password = stream.read()

    return username, password

if __name__ == "__main__":
    creds = GetCreds()
    browser = CreateBrowser()
    BrowserLoginAttempt(browser)
    OpenRandomCanvasResource(browser)
    BrowserLogout(browser)
    browser.quit()

