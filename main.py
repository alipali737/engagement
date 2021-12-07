import os, platform, time, subprocess, argparse
import random as rd
import re as regex

try:
    import schedule
except ImportError:
    print('Schedule not installed! Attempting to install module with "pip3 install schedule"!')
    os.system('pip3 install schedule')
    import schedule

try:
    from selenium import webdriver
except ImportError:
    print('Selenium not installed! Attempting to install module with "pip3 install selenium"!')
    os.system('pip3 install selenium')
    from selenium import webdriver
    
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# TODO : Add way to validate engagement
# TODO : Validate its actually on a login page or log out first

standardDelay = 30

# Selenium Implementation #
# Create and return a new chrome browser
def CreateBrowser():
    # Define chrome options for headless
    options = Options()
    options.headless = args.headless

    # Create a new chrome instance
    browser = webdriver.Chrome("chromedriver", options=options)
    print("Browser created!")
    return browser

# Attempt to login via the browser page
def BrowserLoginAttempt(browser):
    # Open the login page
    browser.get(("https://winchester.instructure.com/"))

    # Get the input field elements (Waits for username field to be loaded before trying)
    usernameField = WebDriverWait(browser, standardDelay).until(EC.presence_of_element_located((By.ID, "userNameInput")))
    passwordField = WebDriverWait(browser, standardDelay).until(EC.presence_of_element_located((By.ID, "passwordInput")))

    # Fill the username and password
    usernameField.send_keys(creds[0])
    passwordField.send_keys(creds[1])

    # Find and click submit button
    try:
        submitButton = browser.find_element(By.ID,"submitButton")
        submitButton.click()
    except:
        pass

    # Wait for a max of {standardDelay} seconds for the canvas page to load
    _ = WebDriverWait(browser, standardDelay).until(EC.presence_of_element_located((By.ID, "application")))

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

    # Wait for a max of {standardDelay} seconds for the canvas page to load
    _ = WebDriverWait(browser, standardDelay).until(EC.presence_of_element_located((By.ID, "application")))

    print("Resource Accessed!")

# Logout once on the intranet
def BrowserLogout(browser):
    # Go to canvas logout page
    browser.get(("https://winchester.instructure.com/logout"))

    # Find and click the logout button
    logoutButton = browser.find_element(By.ID,"Button--logout-confirm")
    logoutButton.click()

    # Wait for logged out screen
    _ = WebDriverWait(browser, standardDelay).until(EC.presence_of_element_located((By.ID, "openingMessage")))

    print("logged out!")

# Get username and password as touple
def GetCreds():
    # Add your winchester student email here
    if args.username == "":
        username = "a.painter.21@unimail.winchester.ac.uk"
    else:
        username = args.username

    # Add you password here if you wish to hardcode them otherwise leave blank for pull from 1password CLI
    if args.password == "":
        password = ""
    else:
        password = args.password

    # To setup one password CLI please configure the vars below
    opSessionName = "ibm"
    opUniLoginItemName = "UNI_LOGIN"

    # Test if password is blank, if so attempt to get from 1password CLI
    if password == "":
        # If the platform is windows 'eval' doesn't exist
        if platform.system() == "Windows":
            password = subprocess.run(["powershell", "-Command", "Invoke-Expression $(op signin %s) && op get item --fields password %s" %(opSessionName, opUniLoginItemName)], capture_output=True)
        else:
            stream = os.popen("eval $(op signin %s) && op get item --fields password %s" %(opSessionName, opUniLoginItemName))
            password = stream.read()

    return username, password

def Main():
    browser = CreateBrowser()
    BrowserLoginAttempt(browser)    
    for i in range(5):
        OpenRandomCanvasResource(browser)
    BrowserLogout(browser)
    browser.quit()

if __name__ == "__main__":

    # Create the argument parser
    argparser = argparse.ArgumentParser(description="Bot to increase canvas engagement")

    # Add the arguments
    argparser.add_argument("-s","--schedule", dest="scheduler", action="store_true", default=False, help="Whether to enable the scheduler")
    argparser.add_argument("--min-hours", dest="minHours", action="store", default=3, help="Minimum amount of hours for the scheduler (Only has effect is scheduler is enabled)")
    argparser.add_argument("--max-hours", dest="maxHours", action="store", default=5, help="Maximum amount of hours for the scheduler (Only has effect is scheduler is enabled)")

    argparser.add_argument("-u","--username", dest="username", action="store", default="", help="Username for the login")
    argparser.add_argument("-p","--password", dest="password", action="store", default="", help="Password for the login")

    argparser.add_argument("--not-headless", dest="headless", action="store_false", default=True, help="Disable headless running of the browser")

    # Execute the parse_args() method to handle the arguments given
    args = argparser.parse_args()

    scheduler = args.scheduler
    minHours = args.minHours
    maxHours = args.maxHours

    # Get credentials for the login
    creds = GetCreds()

    if scheduler:
        # Setup scheduler to run every 3-5 hours (random delay)
        print ("Scheduler set to run every %d-%d hours. Please just leave this running in the background!" %(minHours, maxHours))
        schedule.every(minHours).to(maxHours).hours.do(Main)

        # Create a loop for the scheduler
        while True:
            # Run the schedules as defined
            schedule.run_pending()
            # Wait 1 minute before checking time again
            time.sleep(60)
    else:
        Main()

