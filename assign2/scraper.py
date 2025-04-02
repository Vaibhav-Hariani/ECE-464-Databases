import re
from selenium import webdriver
from selenium.webdriver.common.by import By

from urllib.parse import urljoin


##Using the firefox gecko driver as I've dealt with it before
driver = webdriver.Firefox()


base_page = "https://books.toscrape.com/"
start_page = urljoin(base_page, "catalogue/page-1.html")


class Book():
    ##I will not lie: I had gemini produce this regex as I was feeling lazy
    def parse(avail_str: str) -> int:
        match = re.search(r'\((\d+)\s+available\)', avail_str)
        if match:
            count = int(match.group(1))
            return count
        return 0

    def __init__(self, name, type, avail, upc, price):
        self.name = name
        self.type = type
        self.avail = Book.parse(avail)
        self.UPC = upc
        self.price = price
    def __repr__(self):
        return (f"Book(Name: '{self.name}', Type: '{self.type}', "
                f"Availability: '{self.avail}', UPC: '{self.UPC}', Price: '{self.price}')")

    

def book_extract(category) -> Book:
        name = driver.find_element(By.CSS_SELECTOR, "div.product_main h1").text
        avail = driver.find_element(By.CSS_SELECTOR, "p.instock.availability").text.strip()
        upc = driver.find_element(By.XPATH, "//table[contains(@class, 'table-striped')]//th[text()='UPC']/following-sibling::td").text
        price = driver.find_element(By.CSS_SELECTOR, "p.price_color").text
        return Book(name=name, type=category, avail=avail, upc=upc, price=price)


def scrape_page(driver: webdriver.Firefox, category) -> list[Book]:
    Books = []
    ref_page = driver.current_url
    book_pages = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")
    book_links = [el.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href") for el in book_pages]
    for book in book_links:
        driver.get(book)
        Books.append(book_extract(category))
        driver.back()
        # driver.get(ref_page)

    return Books


def get_books(driver: webdriver.Firefox, category) -> list[Book]:
    books = []
    next_page = True

    while next_page:
        books += scrape_page(driver, category)
        ##Scrape here
        num_books = driver.find_elements(By.CLASS_NAME, "form-horizontal > strong")
        ##I discovered that find_elements when an element doesn't exist is very very slow
        ## To speed it up, I first filter to make sure that there's a next button
        if len(num_books) >= 3 and (num_books[0].text != num_books[-1].text):
            next_button = driver.find_element(By.CSS_SELECTOR, "ul.pager > li.next > a")
            next_page = next_button.get_attribute("href")
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
    for book in books:
        print(book)    
    driver.quit()
