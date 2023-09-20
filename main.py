import os, json, urllib.parse, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait

def createSelenium():
    # Set the options
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920x1080")

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)

    # Nevigate to ALDI's homepage
    driver.get("https://aldi.com.au/")

    amount = 3000
    for i in range(0, 200000, amount):
        data = createProductData(i, i + amount)

        # Ensure we're on the ALDI homepage
        driver.get("https://aldi.com.au/")

        # Ensure the data is a JSON string
        data = json.dumps(data)

        # Update the local session storgae key "shoppingList" with the data from createProductData()
        driver.execute_script("window.localStorage.setItem('shoppingList', arguments[0]);", data)

        # Wait for the local session storage key "shoppingList" to be updated
        WebDriverWait(driver, 5).until(lambda driver: driver.execute_script("window.localStorage.getItem('shoppingList').length") != 0)

        # Set the value for the input with the class "shoppingListLocalStorage" to a URL-encoded version of the data
        data = urllib.parse.quote(data)
        driver.execute_script("document.getElementsByClassName('shoppingListLocalStorage')[0].value = arguments[0];", data)
        time.sleep(3)

        # Click the button with class "shopping-lists-show-button"
        driver.find_element(By.CLASS_NAME, "shopping-lists-show-button").click()

        # Wait for the page to load
        WebDriverWait(driver, 25).until(lambda driver: driver.find_element(By.CLASS_NAME, "mfp-iframe"))

        # Get the entire raw HTML of the iFrame body
        driver.switch_to.frame(driver.find_element(By.CLASS_NAME, "mfp-iframe"))
        data = driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")

        itemData = []
        # For each div with class "box--wrapper ym-gl ym-g25", get the text from div with class "box--description--header"
        # and find the <a> link location within the span with class "box--delete"
        for item in driver.find_elements(By.CLASS_NAME, "box--wrapper"):
            itemData.append(
                {
                    "name": item.find_element(By.CLASS_NAME, "box--description--header").text,
                    "productId": item.find_element(By.CLASS_NAME, "box--delete").find_element(By.TAG_NAME, "a").get_attribute("href").replace("https://www.aldi.com.au/en/shopping-list.html#/productId=", "")
                }
            )

        # Write the data to a file
        with open("products.json", "a") as f:
            json.dump(itemData, f)

        # # Don't close the browser
        # input("Press Enter to continue...")
    
    input("Press Enter to close the browser...")


'''
Create the product data
'''
def createProductData(start, end): 
    data = []
    for i in range(start, end):
        data.append({
            "i": {
                str(i): [
                    "33869",
                    "company",
                    "",
                    "",
                    "",
                    ""
                ]
            }
        })

    new_data = {"i": {}}
    for item in data:
        for key, value in item["i"].items():
            if key not in new_data["i"]:
                new_data["i"][key] = value
            else:
                new_data["i"][key].extend(value)
            
    new_data['t'] = 1694954487428

    # Delete the existing data file
    if os.path.exists("shoppingCartData.json"):
        os.remove("shoppingCartData.json")

    # Create a new data file
    with open("shoppingCartData.json", "w") as f:
        json.dump(new_data, f)

    return new_data


if __name__ == "__main__":
    createSelenium()