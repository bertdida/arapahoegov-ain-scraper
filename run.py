import csv

import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

import proxies

prev_working_proxy = None
ains = [line.rstrip() for line in open('ains.txt')]


def get_request(ain):
    global prev_working_proxy
    url = 'https://parcelsearch.arapahoegov.com/PPINum.aspx?PPINum=' + ain

    while True:
        proxy = prev_working_proxy
        if proxy is None:
            proxy = proxies.get_random()
        try:
            prev_working_proxy = proxy
            return requests.get(url, proxies=proxy, timeout=5)
        except RequestException:
            prev_working_proxy = None


with open('results.csv', 'w', encoding='utf8', newline='') as results_file, \
        open('failed_ains.txt', 'a') as failed_ains_file:
    result_headers = [
        'AIN',
        'PARCEL ID',
        'SITE ADDRESS',
        'SITE CITY',
        'OWNER NAME',
        'MAILING ADDRESS',
        'MAIL CITY STATE ZIP',
        'LAND USE',
        'LEGAL DESC',
        'JUST VALUE',
        'BLDG VALUE',
        'LAND VALUE',
        'SALE DATE',
        'SALE PRICE',
        'LAND USE 2',
        'YEAR BUILT',
    ]

    dict_writer = csv.DictWriter(results_file, fieldnames=result_headers)
    dict_writer.writeheader()

    for index, ain in enumerate(ains):
        print(index + 1, ain)

        response = get_request(ain)
        soup = BeautifulSoup(response.content, 'html.parser')

        if soup.find(lambda tag: 'No matching records were found' in tag.text):
            failed_ains_file.write(ain + '\n')
            continue  # not found, skip

        parcel_id = soup.find('span', {'id': 'ucParcelHeader_lblPinTxt'})
        site_address = soup.find('span', {'id': 'ucParcelHeader_lblSitusAddressTxt'})
        site_city = soup.find('span', {'id': 'ucParcelHeader_lblSitusCityTxt'})
        owner_name = soup.find('span', {'id': 'ucParcelHeader_lblFullOwnerListTxt'})
        mailing_address = soup.find('span', {'id': 'ucParcelHeader_lblOwnerAddressTxt'})
        mail_city_state_zip = soup.find('span', {'id': 'ucParcelHeader_lblOwnerCSZTxt'})
        land_use = soup.find('span', {'id': 'ucParcelHeader_lblLandUseTxt'})
        legal_description = soup.find('span', {'id': 'ucParcelHeader_lblLegalDescTxt'})
        just_value = soup.find('span', {'id': 'ucParcelValue_lblApprTotal'})
        building_value = soup.find('span', {'id': 'ucParcelValue_lblApprBuilding'})
        land_value = soup.find('span', {'id': 'ucParcelValue_lblApprLand'})

        sale_title = soup.find('span', {'id': 'ucParcelSale_rptrSale_lblSaleTitle'})
        if sale_title:
            sale_title_tr_1 = sale_title.find_parent('tr')  # column header
            sale_title_tr_2 = sale_title_tr_1.find_next('tr')
            sale_date = sale_title_tr_2.select('td:nth-child(3)')[0]
            sale_price = sale_title_tr_2.select('td:nth-child(4)')[0]
        else:
            sale_date = None
            sale_price = None

        year_built_title = soup.find('span', {'id': 'ucParcelResdBuild_rptrResdBuild_lblYearBuiltTitle_0'})
        if year_built_title:
            year_built_td = year_built_title.find_parent('td')
            year_built = year_built_td.find_next('td')
        else:
            year_built = None

        land_use_2 = soup.select('td[colspan="3"]')
        land_use_2 = land_use_2[0] if land_use_2 else None

        result_dict = {
            'AIN': ain,
            'PARCEL ID': parcel_id.text,
            'SITE ADDRESS': site_address.text,
            'SITE CITY': site_city.text,
            'OWNER NAME': owner_name.text,
            'MAILING ADDRESS': mailing_address.text,
            'MAIL CITY STATE ZIP': mail_city_state_zip.text,
            'LAND USE': land_use.text,
            'LEGAL DESC': legal_description.text,
            'JUST VALUE': just_value.text,
            'BLDG VALUE': building_value.text,
            'LAND VALUE': land_value.text,
            'SALE DATE': sale_date.text if sale_date else '',
            'SALE PRICE': sale_price.text if sale_price else '',
            'LAND USE 2': land_use_2.text if land_use_2 else '',
            'YEAR BUILT': year_built.text if year_built else ''
        }

        result_dict_stripped = {key: value.strip() for key, value in result_dict.items()}
        dict_writer.writerow(result_dict_stripped)
