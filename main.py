from selenium import webdriver
import time
import re
import json

MAX_MONEY = 500.0
MIN_MONEY = 50.0


def scrape_items(browser):
    items_list = []
    regex = r'(.+[a-zA-Z])\s(\d+\,*\d+\.\d+)\s\+(\d*)%'
    while True:
        try:
            link = browser.find_element_by_link_text('Next')
            scraped_data = [item.text.replace("\n", " ") for item in browser.find_elements_by_class_name('item__inner')]
            for item in scraped_data:
                match = re.search(regex, item)
                if match is not None:
                    groups = match.groups()
                    skin_name, price, percentage = groups[0], float(groups[1].replace(',', '')), groups[2]
                    if MIN_MONEY <= price <= MAX_MONEY:
                        items_list.append({'skin_name': skin_name, 'price': price, 'percentage': percentage})
        except Exception as e:
            print(e)
        finally:
            if link.get_attribute('tabindex') == '-1':
                break
            else:
                try:
                    link.click()
                    time.sleep(1)
                except Exception as e:
                    print(e)
    return items_list


def export_data(data):
    with open('items.json', 'w') as f:
        json.dump({"values": data}, f)


def main():
    url = 'https://csgoempire.com/withdraw#730'
    browser = webdriver.Chrome()
    browser.get(url)
    time.sleep(10)
    export_data(scrape_items(browser))
    browser.quit()


main()


