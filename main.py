import os, json, urllib.parse, time, sys, time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait


def loadProductData(filepath="products.json"):
    # Check if file exists
    if os.path.exists(filepath):
        # Read product data from file
        with open(filepath, "r") as f:
            productData = json.load(f)
        return productData
    else:
        raise FileNotFoundError()


def saveProductData(productData, filepath="products.json"):
    # Ensure product data isn't empty
    if len(productData) > 0:
        # Write product data to file
        # This overwrites your file, so please be careful
        with open(filepath, "w") as f:
            json.dump(productData, f)


def createSelenium(start, end, batch_size):
    # Set the options
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2}) # Stops images from being fetched

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)

    # Navigate to ALDI's homepage
    driver.get("https://aldi.com.au/")

    # Loop through range in batches
    for i in range(start, end, batch_size):
        print(f"Getting products {i} to {i + batch_size}\n")

        # Load the ALDI homepage 
        driver.get("https://aldi.com.au/")

        # Create product data
        data = createProductIDs(i, i + batch_size)
        data_quoted = urllib.parse.quote(data)

        # Update LocalStorage in browser as well as shoppingListLocalStorage element
        driver.execute_script("window.localStorage.setItem('shoppingList', arguments[0]);", data)
        driver.execute_script("document.getElementsByClassName('shoppingListLocalStorage')[0].value = arguments[0];", data_quoted)

        # Wait for the local session storage key "shoppingList" to be updated
        WebDriverWait(driver, 5).until(lambda driver: driver.execute_script("window.localStorage.getItem('shoppingList').length") != 0)
        WebDriverWait(driver, 5).until(lambda driver: driver.execute_script("document.getElementsByClassName('shoppingListLocalStorage')[0].value.length") != 0)

        # Click the button ".shopping-lists-show-button" to open the shopping list
        driver.find_element(By.CLASS_NAME, "shopping-lists-show-button").click()

        # Wait for the shopping list iFrame to load
        WebDriverWait(driver, 25).until(lambda driver: driver.find_element(By.CLASS_NAME, "mfp-iframe"))

        # Parse the entire raw HTML of the iFrame body
        driver.switch_to.frame(driver.find_element(By.CLASS_NAME, "mfp-iframe"))
        data = driver.find_element(By.TAG_NAME, "body").get_attribute("innerHTML")

        # Load any existing product data to itemDatabase dict
        try:
            itemDatabase = loadProductData()
        except:
            itemDatabase = {}
        
        # For each div with class "box--wrapper ym-gl ym-g25", get the text from div with class "box--description--header"
        # and find the <a> link location within the span with class "box--delete"
        for item in driver.find_elements(By.CLASS_NAME, "box--wrapper"):
            # Get name and productID
            itemName = item.find_element(By.CLASS_NAME, "box--description--header").text
            itemProductID = item.find_element(By.CLASS_NAME, "box--delete").find_element(By.TAG_NAME, "a").get_attribute("href").replace("https://www.aldi.com.au/en/shopping-list.html#/productId=", "")
            itemData = {"name": itemName}

            # Get other product information
            # Current price
            try:
                # Both dollar value and decimal was given, combine into one
                # TODO: Check if there's products with only one of these and not both
                itemPriceValue = item.find_element(By.CLASS_NAME, "box--value").text
                itemPriceDecimal = item.find_element(By.CLASS_NAME,"box--decimal").text
                itemData["currentPrice"] = itemPriceValue + itemPriceDecimal
            except:
                pass

            # Former "non-discounted" price
            try:
                itemData["formerPrice"] = item.find_element(By.CLASS_NAME, "box--former-price").text
            except:
                pass

            # Price per unit or quantity
            try:
                itemData["unitPrice"] = item.find_element(By.CLASS_NAME, "box--baseprice").text
            except:
                pass

            # Quantity/amount of product
            try:
                itemData["unit"] = item.find_element(By.CLASS_NAME, "box--amount").text
            except:
                pass

            # Add product to database
            itemDatabase[itemProductID] = itemData

        # Write the data to a file
        saveProductData(itemDatabase)
    
    input("Press Enter to close the browser...")


'''
Create the product ID data for our request 
'''
def createProductIDs(start, end): 
    # Generate LocalStorage data with product IDs for keys
    # This tricks ALDI into adding those products to the shopping cart, which we scrape
    data = {"i": {str(i):[] for i in range(start, end)}, "t": round(time.time() * 1000)}

    # Return in JSON format
    return json.dumps(data)


if __name__ == "__main__":
    # Get the arguments passed to the script
    args = sys.argv[1:]

    if len(args) != 3:
        raise Exception("You must provide 3 arguments: start, end, and batch_size")

    # Get the start and end values
    start = int(args[0])
    end = int(args[1])
    batch_size = int(args[2])

    # Sanity check the values
    if start > end:
        raise Exception("The start value cannot be greater than the end value")
    
    if batch_size <= 0:
        raise Exception("The batch_size value must be greater than 0")

    createSelenium(start, end, batch_size)