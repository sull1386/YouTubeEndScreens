#addEndScreens.py
#Purpose it to add the same end screen to all of your youtube videos
#parameters: number of videos (starting from newest) that will get the end screens from endscreentocopy in properties file (Note: parameters are now stored in endscreen.properties)
#Example call: .\addEndScreens.py 5

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import sys
import time
import configparser
import math
import logging

def getWebElementFromList(xPath):
    try:
        webElement= None
        list_element = driver.find_elements(By.XPATH,xPath)
        if len(list_element) > 0:
            webElement= list_element[0]
        return webElement
    except Exception as e:
        print("getWebElementFromList | An error occurred:", e)
    
def browserSetup():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument(f'--user-data-dir={user_data_dir}')  # Specify user profile directory
    chrome_options.add_argument('--start-maximized')  # Maximize the browser window
    chrome_options.binary_location = chrome_binary_path  # Set Chrome binary path (optional)
    # Initialize the WebDriver with Chrome options
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def clickOnBtnFromXPath(xPathString):
    btn= None
    btn= driver.find_element(By.XPATH,xPathString)
    if btn is None:
        print("Found to find button with xPath: " + xPathString)
        return False
    btn.click()
    return True

def openYTStudio():
    #time.sleep(1)
    # Open the web page
    driver.get(youtubeStudioURL)
    time.sleep(1)

def openYTContent():
    try:
        contentButton= getWebElementFromList(XPATH_CONTENT)
        if contentButton:
            contentButton.click()
    except Exception as e:
        print("An error occurred:", e)
    time.sleep(1)

def clearExistingEndScreens():
    deleteFound= True
    while deleteFound:
        try:
            clickOnBtnFromXPath(XPATH_END_SCREEN_CLEAR)
        except NoSuchElementException as e:
            deleteFound= False

def addEndScreens():
    try:
        #click the end screen button
        clickOnBtnFromXPath(XPATH_EDIT_END_SCREEN_BTN)
        time.sleep(1)
        #check if existing end screens already exist and clear them if so
        clearExistingEndScreens()
        time.sleep(1)
        #click the from video button
        clickOnBtnFromXPath(XPATH_END_SCREEN_IMPORT_BTN)
        time.sleep(1)
        #add end screen to copy text
        searchYoursField= None
        xPathYours= XPATH_IMPORT_TEXT_FIELD
        searchYoursField= driver.find_element(By.XPATH,xPathYours)
        if searchYoursField is None:
            return
        searchYoursField.send_keys(end_screen_to_copy)
        time.sleep(1)
        #select the first result returned in the search
        clickOnBtnFromXPath(XPATH_IMPORT_VIDEO)
        time.sleep(1)
        #save the end screen
        saveEndScreenBtn= None        
        saveEndScreenBtn= driver.find_element(By.XPATH,XPATH_END_SCREEN_SAVE_BTN)
        if saveEndScreenBtn is not None:            
            is_disabled = saveEndScreenBtn.get_attribute("disabled")
            if is_disabled is None:                
                saveEndScreenBtn.click()
            else:                
                discardBtn= None                             
                discardBtn= driver.find_element(By.XPATH,XPATH_END_SCREEN_DISCARD_BTN)
                if discardBtn is not None:
                    logging.info("clicking discard button")
                    discardBtn.click()
        else:
            logging.info("Got to else statement")
        time.sleep(1)
    except Exception as e:
        print("addEndScreens | An error occurred:", e)
        logging.info("Exception | %s",str(e))

def editVideo(index):
    try:
        print("Called addEndScreenToVideo with index: " + index)
        # Find the element to hover over
        video_to_hover_over= None
        xPath= XPATH_VIDEO_TO_HOVER_START + index + XPATH_VIDEO_TO_HOVER_END
        #xPath= "/html/body/ytcp-app/ytcp-entity-page/div/div/main/div/ytcp-animatable[4]/ytcp-content-section/ytcp-video-section/ytcp-video-section-content/div/ytcp-video-row[" + index + "]/div/div[2]/ytcp-video-list-cell-video/div[2]/h3/a/span"
        video_to_hover_over= getWebElementFromList(xPath)
        if video_to_hover_over:
            #first ensure the video found is not the end screen to copy
            videoTitle= video_to_hover_over.text
            print("video title: " + videoTitle)
            if videoTitle in end_screen_to_copy:
                print("Can't edit this video, it's the end screens to copy: " + videoTitle)
                return
            # Create an ActionChains object
            action_chains = ActionChains(driver)        
            # Move the mouse pointer to the element to hover over
            action_chains.move_to_element(video_to_hover_over).perform()                
            #find the edit button for the video and click it
            clickOnBtnFromXPath(XPATH_EDIT_START + index + XPATH_EDIT_END)
            time.sleep(2)
            #click on the "No, it's not made for kids button"
            clickOnBtnFromXPath(XPATH_EDIT_NOT_FOR_KIDS)
            #now add the end screens
            addEndScreens()
            #save the edit
            saveBtn= None
            logging.info("About to look for save button")
            try:            
                saveBtn= driver.find_element(By.XPATH,XPATH_EDIT_SAVE)
                logging.info("Edit save button")
                if saveBtn is not None:
                    is_disabled = saveBtn.get_attribute("disabled")                
                    if is_disabled is None:
                        saveBtn.click()
                        time.sleep(1)
                else:
                    logging.info("Can't find save button")
            except Exception as e:
                logging.info("Save Button not found, just pressing back button")
            #return back to main content page for now
            backBtn= None            
            backBtn= driver.find_element(By.XPATH,XPATH_EDIT_BACK_BTN)
            if backBtn:
                backBtn.click()
            time.sleep(2)
    except Exception as e:
        print("editVideo | An error occurred:", e)


# Check if the correct number of arguments is provided
if len(sys.argv) != 2:
    print("Usage: python addEndScreens.py arg1...")
    sys.exit(1)

#read the number of videos from the properties file

numOfVideos= sys.argv[1]
#read values from the endscreen.properties file
config = configparser.ConfigParser()
config.read('endscreen.properties')
youtubeStudioURL = config['studio_settings']['youtubestudiourl']
end_screen_to_copy = config['studio_settings']['endscreentocopy']
user_data_dir = config['machine_settings']['userdatadir']
chrome_binary_path = config['machine_settings']['chromebinarypath']

print("Number of videos: " + numOfVideos)
print("From endscreen.properties:")
print("youtubeStudioURL: " + youtubeStudioURL)
print("user_data_dir: " + user_data_dir)
print("chrome_binary_path: " + chrome_binary_path)
print("end_screen_to_copy: " + end_screen_to_copy)

#setup logging
# Configure the logging
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filemode='w')  # Overwrite the log file)

#log the parameters
logging.info("PARAMETER | Number of videos:  %s",numOfVideos)
logging.info("PARAMETER | youtubeStudioURL:  %s",youtubeStudioURL)
logging.info("PARAMETER | end_screen_to_copy:  %s",end_screen_to_copy)
logging.info("PARAMETER | user_data_dir:  %s",user_data_dir)
logging.info("PARAMETER | chrome_binary_path:  %s",chrome_binary_path)


#setup the xPath strings
XPATH_CONTENT= "/html/body/ytcp-app/ytcp-entity-page/div/div/ytcp-navigation-drawer/nav/ytcp-animatable[2]/ul/li[2]/ytcp-ve/a/tp-yt-paper-icon-item"
XPATH_BASE_YTCP= "/html/body/ytcp-app/ytcp-entity-page/div/div/main/div/ytcp-animatable"
XPATH_VIDEO_TO_HOVER_START= XPATH_BASE_YTCP + "[4]/ytcp-content-section/ytcp-video-section/ytcp-video-section-content/div/ytcp-video-row["
XPATH_VIDEO_TO_HOVER_END= "]/div/div[2]/ytcp-video-list-cell-video/div[2]/h3/a/span"
XPATH_EDIT_START= XPATH_BASE_YTCP + "[4]/ytcp-content-section/ytcp-video-section/ytcp-video-section-content/div/ytcp-video-row["
XPATH_EDIT_END= "]/div/div[2]/ytcp-video-list-cell-video/div[2]/div[2]/a[1]/ytcp-icon-button"
XPATH_EDIT_NOT_FOR_KIDS= XPATH_BASE_YTCP + "[10]/ytcp-video-details-section/ytcp-video-metadata-editor/div/ytcp-video-metadata-editor-basics/div[5]/ytkc-made-for-kids-select/div[4]/tp-yt-paper-radio-group/tp-yt-paper-radio-button[2]/div[2]/ytcp-ve"
XPATH_EDIT_SAVE= XPATH_BASE_YTCP + "[10]/ytcp-video-details-section/ytcp-sticky-header/ytcp-entity-page-header/div/div[2]/ytcp-button[2]/ytcp-button-shape/button/yt-touch-feedback-shape/div/div[2]"
XPATH_EDIT_BACK_BTN= "/html/body/ytcp-app/ytcp-entity-page/div/div/ytcp-navigation-drawer/nav/ytcp-animatable[1]/ytcp-ve/a/tp-yt-paper-icon-item"
XPATH_EDIT_END_SCREEN_BTN= XPATH_BASE_YTCP + "[10]/ytcp-video-details-section/ytcp-video-metadata-editor/ytcp-video-metadata-editor-sidepanel/ytcp-text-dropdown-trigger[2]/ytcp-dropdown-trigger/div/div[2]/span"
XPATH_END_SCREEN_BASE= "/html/body/ytve-endscreen-modal/ytve-modal-host/ytcp-dialog/tp-yt-paper-dialog/div"
XPATH_END_SCREEN_IMPORT_BTN= XPATH_END_SCREEN_BASE + "[2]/div/ytve-editor/div[1]/div/ytve-endscreen-editor-options-panel/div[1]/ytcp-button[2]"
XPATH_END_SCREEN_SAVE_BTN= XPATH_END_SCREEN_BASE + "[1]/div/div[2]/div/div[2]/ytcp-button"
XPATH_END_SCREEN_DISCARD_BTN= XPATH_END_SCREEN_BASE + "[1]/div/div[2]/div/ytcp-button"
XPATH_END_SCREEN_CLEAR= XPATH_END_SCREEN_BASE + "[2]/div/ytve-editor/div[1]/div/ytve-endscreen-editor-options-panel/div[2]/div/ytcp-icon-button"
XPATH_IMPORT_BASE= "/html/body/ytcp-video-pick-dialog/ytcp-dialog/tp-yt-paper-dialog/div"
XPATH_IMPORT_TEXT_FIELD= XPATH_IMPORT_BASE + "[1]/div[2]/div/tp-yt-paper-tabs/div/div/tp-yt-paper-tab[1]/div/input"
XPATH_IMPORT_VIDEO= XPATH_IMPORT_BASE + "[2]/div/ytcp-video-pick-dialog-contents/div/div/div/ytcp-entity-card"
XPATH_NEXT_PAGE= XPATH_BASE_YTCP + "[4]/ytcp-content-section/ytcp-video-section/ytcp-video-section-content/div/div[2]/ytcp-table-footer/div[2]/ytcp-icon-button[3]/tp-yt-iron-icon"

driver= browserSetup()
openYTStudio()
openYTContent()

#looks like youtube studio always defaults to 30
videosPerPage= 30
numOfPages= math.floor(int(numOfVideos) / videosPerPage) + 1
print("Number of pages:" + str(numOfPages))

numOfVideosRange= int(numOfVideos) + 1
for i in range(0,numOfPages):
    if i != 0:
        #go to the next page
        clickOnBtnFromXPath(XPATH_NEXT_PAGE)
    videoRange= videosPerPage
    #on the last page determine the video range (example if 67 videos, numOfVides (67) mod videosPerPage (30) = 7 more videos)
    if i == numOfPages - 1:
        videoRange= int(numOfVideos) % videosPerPage
    #loop through and edit each video
    for j in range(1, videoRange + 1):
        editVideo(str(j))
    time.sleep(1)    

#loop through and edit each video, TODO: read number of videos to edit as a parameter, considering creating a settings/properties file to read in instead of using command line parameters
#for i in range(1, numOfVideosRange):
    #editVideo(str(i))

time.sleep(1)

# Wait for user input before closing the window
input("Press Enter to exit...")

# Close the browser
driver.quit()