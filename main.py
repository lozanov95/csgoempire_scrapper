from selenium import webdriver
import time


def find_awps(browser):
    search_box = browser.find_element_by_class_name("search__input")
    search_box.send_keys("awp")
    time.sleep(2)
    items = []
    while True:
        link = browser.find_element_by_link_text("Next")
        items += [items.append(item.text) for item in browser.find_elements_by_class_name("item__name")]
        time.sleep(1)
        if link.get_attribute("tabindex") == "-1":
            break
        else:
            link.click()
    print(len(items))


def main():
    url = 'https://csgoempire.com/withdraw#730'
    browser = webdriver.Chrome()
    browser.get(url)
    time.sleep(5)
    find_awps(browser)
    browser.quit()


main()


