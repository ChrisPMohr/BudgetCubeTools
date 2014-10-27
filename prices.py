"""Fetches card prices from mtggoldfish"""
import csv
import time
import requests
from bs4 import BeautifulSoup

PRICING_URL = 'http://www.mtggoldfish.com/tools/deck_pricer'
MAX_CARD_LIST_SIZE = 100
SLEEP_TIME = 30

def submit_card_list(card_list):
    """Sends cards to website"""
    values = {'deck': '\n'.join(card_list),
              'commit': 'Submit',
              'utf8': '✓',
              'authenticity_token': '/0gEKI+9LK2oOrUs8pynq75iQ5Ci8diXsfl1ajTNZOk='}
    response = requests.post(PRICING_URL, data=values)
    return response

def save_page(response):
    """Saves entire web response"""
    with open("my_response_page.html", 'w') as response_file:
        text = response.text
        response_file.write(text.encode('utf-8', 'ignore').decode('utf-8'))

def parse_html(html):
    """parse the html to get card name, mana cost, and price"""
    card_data = list()
    TYPE_NAME_MAP = {'Creatures': 'Creature',
                     'Spells': 'Spell',
                     'Lands': 'Land'}

    soup = BeautifulSoup(html)
    paper_prices_el = soup.find(id='paper')
    type_name = ''
    for row_el in paper_prices_el.find_all('tr'):
        card_name_el = row_el.find('td', class_='card-name')
        if card_name_el:
            card_data.append(parse_card_html(row_el, card_name_el, type_name))
        else:
            header_el = row_el.find('td', class_='header')
            if header_el:
                header_text = header_el.text.strip()
                header_type_name = header_text.split()[0]
                if header_type_name in TYPE_NAME_MAP:
                    type_name = TYPE_NAME_MAP[header_type_name]

    return card_data


def parse_card_html(row_el, card_name_el, type_name):
    """parse the html for a single card"""
    card_name = card_name_el.text.strip()

    mana_cost_el = row_el.find('span', class_='manacost')
    mana_cost_symbols = list()
    for img_el in mana_cost_el.find_all('img'):
        mana_cost_symbols.append(img_el['alt'])
    mana_cost = ''.join(mana_cost_symbols)

    price_el = row_el.find('td', class_='price')
    price = price_el.text.strip()

    return (card_name, type_name, mana_cost, price)


def write_card_data(card_data, file_name):
    """Write the elements of card_data as rows in a csv to file_name"""
    with open(file_name, 'w') as csvfile:
        card_data_writer = csv.writer(csvfile, lineterminator='\n')
        for row in card_data:
            card_data_writer.writerow(row)

def split_card_list(card_list):
    """
    Lookup a list of card by splitting into smaller chunks and
    waiting between them.
    """
    card_list_copy = list(card_list)
    card_data = list()
    first = True
    counter = 0
    while card_list_copy:
        if first:
            first = False
        else:
            time.sleep(SLEEP_TIME)

        small_card_list = list()
        while len(small_card_list) < MAX_CARD_LIST_SIZE and card_list_copy:
            small_card_list.append(card_list_copy.pop(0))
        print("Sending {} cards.".format(len(small_card_list)))
        response = submit_card_list(small_card_list)
        small_card_data = parse_html(response.text)
        print("Got back data for {} cards.".format(len(small_card_data)))
        if len(small_card_list) != len(small_card_data):
            file_name = "parse_error_" + counter + ".html"
            print("Saving response that caused error to {}.".format(file_name))
            try:
                with open(file_name, 'w') as parse_error_file:
                    parse_error_file.write(response.text)
            except UnicodeEncodeError:
                with open(file_name, 'w') as parse_error_file:
                    parse_error_file.write(response.text.encode('utf-8', 'ignore').decode('utf-8'))
        csv_file_name = "combined_csv_file_{}.csv".format(counter)
        counter += 1
        write_card_data(small_card_data, csv_file_name)
        card_data.extend(small_card_data)
    return card_data

def save_card_prices(card_list, file_name):
    """Look up card list and save all prices to a csv at file_name"""
    card_data = split_card_list(card_list)
    write_card_data(card_data, file_name)

def run_script():
    """Do the default thing for the script"""
    cards = ["1 White Sun's Zenith", "1 Gideon Jura"]
    file_name = "sample.csv"
    save_card_prices(cards, file_name)

if __name__ == '__main__':
    run_script()
