from selenium import webdriver
import time
import re
import json

class CSGOEmpireScrapper:
    def __init__(self, max_money=500, min_money=50, pause_after_page_seconds=1, initial_pause_seconds=10):
        """
        Initializes the CSGO Empire scrapper
        :param max_money: Max money that you want to look for. default value = 500
        :param min_money: Min money that you want to look for. default value = 50
        :param pause_after_page_seconds: Pauses after each time the scrapper clicks next page, so the items can load.
        default value = 1
        :param initial_pause_seconds: Pauses initially, so the page could load before the scrapper starts.
        default value = 10
        """
        self.url = 'https://csgoempire.com/withdraw#730'
        self.config = {'MAX_MONEY': max_money, 'MIN_MONEY': min_money,
                       'PAUSE_AFTER_PAGE_SECONDS': pause_after_page_seconds,
                       'INITIAL_PAUSE_SECONDS': initial_pause_seconds}

    def scrape_items(self):
        """
        Scrapes the CSGO Empire withdraw page
        :return: list of scraped items in JSON format
        """
        browser = webdriver.Chrome()
        browser.get(self.url)
        time.sleep(self.config['INITIAL_PAUSE_SECONDS'])
        items_list = []
        regex = r'(.+[a-zA-Z])\s(\d+\,*\d+\.\d+)\s\+(\d*)%'
        while True:
            try:
                scraped_data = [item.text.replace("\n", " ") for item in
                                browser.find_elements_by_class_name('item__inner')]
                for item in scraped_data:
                    match = re.search(regex, item)
                    if match is not None:
                        groups = match.groups()
                        skin_name, price, percentage = groups[0], float(groups[1].replace(',', '')), groups[2]
                        if self.config['MIN_MONEY'] <= price <= self.config['MAX_MONEY']:
                            items_list.append({'skin_name': skin_name, 'price': price, 'percentage': percentage})
            except Exception as e:
                print(e)
            finally:
                link = browser.find_element_by_link_text('Next')
                if link.get_attribute('tabindex') == '-1':
                    break
                else:
                    try:
                        link.click()
                        time.sleep(self.config['PAUSE_AFTER_PAGE_SECONDS'])
                    except Exception as e:
                        print(e)

        json_items = json.dumps({'values': items_list})
        self.export_data(json_items)
        return json_items

    def scrape_items_new(self):
        browser = webdriver.Chrome()
        browser.get(self.url)
        items_list = []
        regex = r'(?P<skin_quality>[A-Za-z\s|~0-9\.-]{1,30})[>]{2}(?P<weapon_name>.{1,30})[>]{2}(?P<skin_name>.{1,20})' \
                r'[>]{2}(?P<skin_price>\d+\,{0,1}\d+\.\d{0,2})[>+]{0,3}(?P<percentage>\d{0,2})[%]{0,1}'
        expression = re.compile(regex)
        time.sleep(self.config['INITIAL_PAUSE_SECONDS'])
        while True:
            try:
                scraped_items = [item.text.replace('\n', '>>') for item in
                              browser.find_elements_by_class_name('item__inner')]
            except Exception as e:
                print(e)
            break

        text_items = "".join(scraped_items)
        matches = expression.finditer(text_items)
        for match in matches:
            groups = match.groupdict()
            inflated_price = float(groups['skin_price'].replace(',', ''))
            percentage = float(groups['percentage']) if groups['percentage'] is not None else 0
            current_price = round(inflated_price - (inflated_price * percentage / 100), 2)
            items_list.append({'skin_quality': groups['skin_quality'].split(' | ')[0],
                               'weapon_name': groups['weapon_name'],
                               'skin_name': groups['skin_name'],
                               'skin_price': current_price
                               })
        print(items_list)

    def export_data(self, data):
        """
        Exports the information to items.json file
        :param data: JSON formatted items data. "values" : [list_of_item_objects]
        :return: 0 if the file was exported, -1 if there was an exception
        """
        try:
            with open('items.json', 'w') as f:
                f.write(data)
                return 0
        except Exception as e:
            print(e)
            return -1


def main():
    scrapper = CSGOEmpireScrapper(initial_pause_seconds=5)
    #print(scrapper.scrape_items())
    scrapper.scrape_items_new()


if __name__ == '__main__':
    main()
