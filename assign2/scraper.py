import time
from selenium import webdriver
from selenium.webdriver.common.by import By

from urllib.parse import urljoin

import json # To print the final data nicely


##Using the firefox gecko driver as I've dealt with it before
driver = webdriver.Firefox()


base_page = "https://books.toscrape.com/"
start_page = urljoin(base_page, "catalogue/page-1.html")


class Book():
    def __init__(self, name, type, avail, upc, price):
        self.name = name
        self.type = type
        self.avail = avail
        self.UPC = upc
        self.price = price

def book_extract(category) -> Book:
        name = driver.find_element(By.CSS_SELECTOR, "div.product_main h1").text
        avail = driver.find_element(By.CSS_SELECTOR, "p.instock.availability").text.strip()
        upc = driver.find_element(By.XPATH, "//table[contains(@class, 'table-striped')]//th[text()='UPC']/following-sibling::td").text
        price = driver.find_element(By.CSS_SELECTOR, "p.price_color").text
        return Book(name=name, type=category, avail=avail, upc=upc, price=price)


def scrape_page(driver: webdriver.Firefox, category) -> list[Book]:
    Books = []
    ref_page = driver.current_url
    print("Oops, not done yet!")
    book_pages = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")
    book_links = [el.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href") for el in book_pages]
    for book in book_links:
        driver.get(book)
        # book_clickable = book_el.find_element(By.CSS_SELECTOR, "h3 a")
        # book_clickable.click()
        Books.append(book_extract(category))
        driver.back()
        # driver.get(ref_page)

       # book_url = book.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href")
    return Books


def get_books(driver: webdriver.Firefox, category) -> list[Book]:
    books = []
    next_page = True

    while next_page:
        books += scrape_page(driver, category)
        ##Scrape here
        next_button = driver.find_elements(By.CSS_SELECTOR, "ul.pager > li.next > a")
        if len(next_button) > 0:
            next_page = next_button[0].get_attribute("href")
            driver.get(next_page)
        else:
            next_page = False
    return books



if __name__ == "__main__":
    books = []
    categories = []
    links = []

    driver.get(base_page)
    driver.implicitly_wait(2)
    category_list_element = driver.find_element(By.CSS_SELECTOR, "div.side_categories ul.nav-list > li > ul")
    category_elements = category_list_element.find_elements(By.TAG_NAME, "a")
    categories = [elem.accessible_name for elem in category_elements]
    links =[elem.get_attribute("href") for elem in category_elements]
    for category, link in zip(categories, links):
        driver.get(link)
        books += get_books(driver, category)    
    driver.quit()




# # --- Step 1: Collect all bookc detail page URLs from all listing pages ---
# print("Collecting book detail URLs...")
# while current_page_url:
#     print(f"Scraping listing page: {current_page_url}")
#     try:
#         driver.get(current_page_url)
#         # Give the page a moment to load (better practice: use WebDriverWait)
#         time.sleep(1)

#         # Find all book containers on the current page
#         book_elements = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")

#         # Extract the detail page URL from each book
#         for book in book_elements:
#             try:
#                 # The URL is relative, so we need to join it with the base catalogue URL
#                 relative_url = book.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href")
#                 # Correctly join relative URLs that might step up directories
#                 # Example: ../../../the-exiled_247/index.html -> https://books.toscrape.com/catalogue/the-exiled_247/index.html
#                 detail_url = base_url + relative_url.replace('../', '')
#                 all_book_detail_urls.append(detail_url)
#             except NoSuchElementException:
#                 print("Warning: Could not find detail URL for a book on this page.")
#             except Exception as e:
#                  print(f"Warning: Error extracting detail URL: {e}")


#         # Find the 'next' button
#         try:
#             next_button = driver.find_element(By.CSS_SELECTOR, "li.next a")
#             next_page_relative_url = next_button.get_attribute("href")
#             # Construct the full URL for the next page
#             current_page_url = base_url + next_page_relative_url
#         except NoSuchElementException:
#             # No 'next' button found, assume it's the last page
#             print("No 'next' button found. Reached the last listing page.")
#             current_page_url = None # End the loop

#     except WebDriverException as e:
#         print(f"Error loading page {current_page_url}: {e}")
#         # Decide how to handle this - retry, skip, or stop? Here we stop.
#         current_page_url = None
#     except Exception as e:
#         print(f"An unexpected error occurred on listing page {current_page_url}: {e}")
#         current_page_url = None

# print(f"Collected {len(all_book_detail_urls)} book detail URLs.")

# # --- Step 2: Visit each detail page and extract data ---
# print("Extracting data from detail pages...")
# book_count = 0
# for url in all_book_detail_urls:
#     book_count += 1
#     print(f"Processing book {book_count}/{len(all_book_detail_urls)}: {url}")
#     try:
#         driver.get(url)
#         # Give the page a moment to load (better practice: use WebDriverWait)
#         time.sleep(0.5) # Shorter sleep as detail pages might load faster

#         # Initialize book data dictionary with default values
#         book_data = {
#             "name": None,
#             "price": None,
#             "availability": None,
#             "genre": None,
#             "upc": None,
#             "url": url # Store the URL for reference
#         }

#         # Extract data using robust methods
#         try:
#             book_data["name"] = driver.find_element(By.CSS_SELECTOR, "div.product_main h1").text
#         except NoSuchElementException:
#             print(f"Warning: Could not find name for book at {url}")

#         try:
#             book_data["price"] = driver.find_element(By.CSS_SELECTOR, "p.price_color").text
#         except NoSuchElementException:
#             print(f"Warning: Could not find price for book at {url}")

#         try:
#             # Availability text is like "In stock (22 available)"
#             availability_text = driver.find_element(By.CSS_SELECTOR, "p.instock.availability").text.strip()
#             book_data["availability"] = availability_text
#         except NoSuchElementException:
#              print(f"Warning: Could not find availability for book at {url}")
#              book_data["availability"] = "Availability not found" # Default if missing

#         try:
#             # Genre is the 3rd item in the breadcrumb list
#             book_data["genre"] = driver.find_element(By.XPATH, "//ul[@class='breadcrumb']/li[3]/a").text
#         except NoSuchElementException:
#             print(f"Warning: Could not find genre for book at {url}")

#         try:
#             # UPC is in the product information table
#             book_data["upc"] = driver.find_element(By.XPATH, "//table[@class='table table-striped']//th[text()='UPC']/following-sibling::td").text
#         except NoSuchElementException:
#             print(f"Warning: Could not find UPC for book at {url}")

#         # Add the extracted data to our main list
#         all_books_data.append(book_data)

#     except WebDriverException as e:
#         print(f"Error loading detail page {url}: {e}")
#         # Optionally add a placeholder or skip this book
#         all_books_data.append({"url": url, "error": str(e)})
#     except Exception as e:
#         print(f"An unexpected error occurred processing {url}: {e}")
#         all_books_data.append({"url": url, "error": f"Unexpected error: {str(e)}"})


# # --- Step 3: Cleanup ---
# print("Closing the browser...")
# driver.quit()

# # --- Step 4: Output the data ---
# print(f"\n--- Collected {len(all_books_data)} Book Records ---")
# # Pretty print the first 5 results as an example
# print(json.dumps(all_books_data[:5], indent=2))

# # To save to a file (e.g., JSON):
# # file_path = 'books_data.json'
# # try:
# #     with open(file_path, 'w', encoding='utf-8') as f:
# #         json.dump(all_books_data, f, ensure_ascii=False, indent=4)
# #     print(f"\nData successfully saved to {file_path}")
# # except IOError as e:
# #     print(f"\nError saving data to file: {e}")

# print("\nScraping finished.")