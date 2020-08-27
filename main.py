from csgoempire_scrapper import CSGOEmpireScrapper
import json


def export_items(file_name, data):
    with open(file_name, 'w') as f:
        f.write(data)


def main():
    scrapper = CSGOEmpireScrapper()
    data = json.loads(scrapper.scrape_items())
    priced_items = []
    try:
        for value in data['values']:
            existing = False
            for item in priced_items:
                if item.get('weapon_name') == value['weapon_name'] and item.get('skin_name') == value['skin_name'] \
                        and item.get('skin_quality') == value['skin_quality']:
                    existing = True
                    if item['min_price'] > value['skin_price']:
                        item['min_price'] = value['skin_price']
                    if item['max_price'] < value['skin_price']:
                        item['max_price'] = value['skin_price']
                    break
            if not existing:
                priced_items.append({'skin_quality': value['skin_quality'], 'weapon_name': value['weapon_name'],
                                     'skin_name': value['skin_name'], 'min_price': value['skin_price'],
                                     'max_price': value['skin_price'], 'timestamp': value['timestamp']})
    except Exception as e:
        print(e)
    finally:
        json_data = json.dumps({'values': (sorted(priced_items, key=lambda x: (x['weapon_name'], x['skin_name'])))})
        export_items('priced_items.json', json_data)


main()
