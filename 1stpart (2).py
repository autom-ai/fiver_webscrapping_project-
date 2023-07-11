
import time
import pandas as pd
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")
from selenium.webdriver.support.ui import Select
import re
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse, parse_qs
from urllib.parse import urlencode


service = Service(executable_path=r'/usr/bin/chromedriver')

df = pd.read_excel('results_2.xlsx')



options = webdriver.ChromeOptions()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--disable-dev-shm-usage')
# # Open the Web Browser Or Load The Chrome

# In[4]:


# options = Options()
driver = webdriver.Chrome(service=service, options=options)
def set_US_mode(url):

    # Find the element by class name
    driver.get(url)
    element = driver.find_elements(By.CLASS_NAME , 'wt-display-inline-block')
    count=0

    try:
        for i in element:
            if ('  Pakistan   |   English (UK)   |   $ (USD)' in i.text):
                clicker=i
            count+=1


        clicker.click()

        # Find the option for 'United States' by its value and click it
        wait = WebDriverWait(driver, 10)
        select_element = wait.until(EC.presence_of_element_located((By.ID, 'locale-overlay-select-region_code')))

        option = select_element.find_element(By.XPATH, f".//option[@value='US']")
        option.click()

        # Wait for the Save button to be clickable
        wait = WebDriverWait(driver, 10)
        save_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[name="save"]')))

        # Click the Save button
        save_button.click()

    except:
        pass


def get_all_links(url , pageno):

    href_list=[]
    all_pages=[]
    ads_check = []
    temp= url + '&ref=pagination&page='
    tempo = temp + str(pageno+1)

    try:
        driver.get(tempo)
        # Find the elements representing the products
        product_elements = driver.find_elements(By.CLASS_NAME , "listing-link")

        
        for element in product_elements:
            tempn = element.get_attribute("href")
            html = element.get_attribute("innerHTML")
            if ">Ad by Etsy seller<" in html:
                ads_check.append(0)
            #    print(html)
            else:
                ads_check.append(1)
            href_list.append(tempn)

    except:
           pass
    print(ads_check)
    values = href_list
    conditions = ads_check
    filtered_values = [value for value, condition in zip(values, conditions) if condition == 1]

    return filtered_values



def page_pos_new_link(urln , link_id):

    for pageno in range(250):
        href_list_2 = get_all_links(urln , pageno)

#         print("Href: " , len(href_list_2))
#        print(href_list_2)
        new_linksser=[]
        page_num=[]
        pos=[]
        main_url=[]
        ids=[]
        mainer=False

        for i in range(len(href_list_2)):
            if str(int(link_id)) in href_list_2[i]:
                main_url.append(urln)
                ids.append(link_id)
                new_linksser.append(href_list_2[i])
                page_num.append(pageno+1)

                ###########

                pattern = r"-([1-9]|[1-9][0-9]|[12][0-4][0-9])&"
                matches = re.findall(pattern, new_linksser[0])
                print(matches)
                try:
                    pos.append(matches[0])
                except:
                    pos.append('NULL')
                #####################
                print(href_list_2[i])
                print(page_num)
                print(pos)
                mainer=True

                return main_url , ids , new_linksser, page_num, pos


    main_url.append(urln)
    ids.append(link_id)
    new_linksser.append('Null')
    page_num.append('Null')
    pos.append('Null')

    return main_url , ids , new_linksser, page_num, pos
list_id = df['listing id'].to_list()
url = df['url '].to_list()


new_links=[]
pages=[]
positions=[]
old_links=[]
ides=[]

try:
    print(url[0])
    set_US_mode(url[0])
except:
    try:
        set_US_mode(url[1])
    except:
        print("Link Incorrect or US Mode has already opened.")

for i in range(len(url)):
    found=False
    try:
        driver.get(url[i])
        found=True

    except:
        found=False

    if(found==True):
        print("----Hello---")
        x , y , a , b , c = page_pos_new_link(url[i] , list_id[i])
        print(x,y,a,b,c)
        old_links+=x
        ides += y
        new_links+=a
        pages+=b
        positions+=c



len(old_links)

len(ides)
len(new_links)
len(pages)
len(positions)
data = {
    'URL': old_links,
    'Listing ID': ides,
    'New URL': new_links,
    'Page No': pages,
    'Position': positions
}

df = pd.DataFrame(data)
df.to_csv('data.csv', index=False)

for i in new_links:
    founds = False

    try:
        driver.get(i)
        founds = True
    except:
        founds = False

    if founds:
        try:
            select_element = driver.find_element(By.ID, "variation-selector-0")
            select = Select(select_element)
            select.select_by_index(1)
        except:
            pass

        time.sleep(1)

        try:
            select_element = driver.find_element(By.ID, "variation-selector-1")
            select = Select(select_element)
            select.select_by_index(1)
        except:
            pass

        time.sleep(1)

        try:
            textarea_element = driver.find_element(By.ID, "listing-page-personalization-textarea")
            textarea_element.clear()
            textarea_element.send_keys("thank you")
        except:
            pass

        time.sleep(1)

        try:
            button_element = driver.find_element(By.XPATH, "//button[contains(text(), 'Add to basket')]")
            button_element.click()
            print("Item Added To Basket")
        except:
            print("Item not added for some reason and the link is:", i)