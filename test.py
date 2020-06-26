import requests
import bs4
import json
import time
import logging

logging.basicConfig(level=logging.INFO, filename='yad2.log')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
}

# Change to your user key
user_key = 'USER_KEY'
push_headers = {'Access-Token': user_key,
                'Content-Type': 'application/json'}

page_by_id = dict()


def get_ids(text, pgnum):
    global page_by_id
    found_ids = set()
    soup = bs4.BeautifulSoup(text)
    for i in range(1, 50):
        try:
            item_id = soup.find("div", {"id": f'feed_item_{str(i)}'}).get('item-id')
            found_ids.add(item_id)
            page_by_id[item_id] = pgnum
        except Exception as e:
            logging.info(f'parsing error {e}')
            pass
    return found_ids


def get_known_ids():
    with open('known_ids.json') as f:
        a = json.load(f)['ids']
    return set(a)


def send_captcha(url):
    data2 = {"body": "Got captcha!", "title": "Captcha :[", 'url': url,
             "type": "link"}
    resp3 = requests.post(url='https://api.pushbullet.com/v2/pushes', headers=push_headers,
                          data=json.dumps(data2))


def get_new_ids():
    new_ids = set()
    known_ids = get_known_ids()
    resp = requests.get(
        'https://www.yad2.co.il/realestate/rent?city=5000&rooms=2-3&price=4000-6000&EnterDate=15-7-2020',
        headers=headers)
    logging.info(f'Got page {resp.url}')
    if resp.url.startswith('https://validate.perfdrive.com'):
        send_captcha(resp.url)
        return set()
    for page in range(2, 6):
        time.sleep(20)
        if not resp.url.startswith('https://www.yad2.co.il/realestate/rent?city=5000'):
            logging.info(f'Breaking because of {str(resp.url)}')
            break
        found_ids = get_ids(resp.text, page - 1)
        new_ids.update(found_ids.difference(known_ids))
        resp = requests.get(
            f'https://www.yad2.co.il/realestate/rent?city=5000&rooms=2-3&price=4000-6000&EnterDate=15-7-2020&page={page}',
            headers=headers)
        logging.info(f'Got page {resp.url}')
        if resp.url.startswith('https://validate.perfdrive.com'):
            send_captcha(resp.url)
            return new_ids
        if resp.history:
            logging.info(f'Breaking because of {str(resp.history)}')
            break

    return new_ids


def save_new_ids(new_ids):
    with open('known_ids.json') as f:
        old_ids = set(json.load(f)['ids'])
    old_ids.update(new_ids)
    with open('known_ids.json', 'w') as f:
        json.dump(dict(ids=list(old_ids)), f)


if __name__ == '__main__':
    minutes_interval = 15
    while True:
        new_ids = get_new_ids()
        for new_id in new_ids:
            new_link = f'https://www.yad2.co.il/item/{new_id}'
            # notification data
            data = {"body": "Found new app!", "title": "New Apartment", 'url': new_link,
                    "type": "link"}
            resp2 = requests.post(url='https://api.pushbullet.com/v2/pushes', headers=push_headers,
                                  data=json.dumps(data))
        save_new_ids(new_ids)
        page_by_id = dict()
        logging.info(time.asctime())
        time.sleep(60 * minutes_interval)

