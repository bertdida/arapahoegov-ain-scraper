import requests
from bs4 import BeautifulSoup
from random import choice

proxies = []
source_url = 'https://www.us-proxy.org/'


def _get_proxies():
    global proxies

    print('Getting  proxies...')

    response = requests.get(source_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find(id='proxylisttable')
    ip_tds = table.find_all('td')[::8]
    port_tds = table.find_all('td')[1::8]

    ips = [td.text for td in ip_tds]
    ports = [td.text for td in port_tds]
    proxies = ['{}:{}'.format(ip, port) for ip, port in zip(ips, ports)]

    print(len(proxies), ' proxies ready')


def get_random():
    proxy = choice(proxies)
    return {'http': proxy, 'https': proxy}


if __name__ != 'main':
    _get_proxies()
