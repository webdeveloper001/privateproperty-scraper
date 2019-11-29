# coding=utf-8
import requests
import csv
import json
import sys
from bs4 import BeautifulSoup 

token = ['', '03AOLTBLRdSxa5iykZVwR4Fl8AVrptAXmMAXIddiLhubFjHqP3gnq_PhDPxLO0JW_MXtU96aE9YypfYPi7O2P-MwLV0x4yRjL_bYxeNLEP6GdVZw59blN-P8gOVHKWb4aTmQzMP8_MFtpWioufCZrrDgUF9Ngw15P3ipkvo2iF5akdpqHld_IJv6bUITMcX8FLaMZw-ChaWoOhtKcA7XJSDo1AV7Fhe3c-c-7JW9S5AaL6f3ftN2AMwuxtZCG6zDBfXvESj2GrSGxK3o1-ZnaKX5WE7P3Xo06N7dEU-7VpZYC9J1cfi9QhlPRkiQtP1xtI9lL-3kNNeWvbfse_Zn9DZ_5fZFaquVV3hQ', '03AOLTBLSHXZM8CfOEm5EX4u1BQypTfoC91_r9OatzwVIQcqb5_ntq0v9GrQDdrSaM-U7Krn7zOyxRyNMW1A4hOa7hCHUqHRMMAngIeH-Z_x5CDRGUbj4g74aXCzH2RDwLpbFfTbtKUUGgWVKM5u8Za2GM212WxN1Gb6tnsCEbqJYK0LVtMajdSTQ6a2apJZUPio8pWoeq4q6seq1rMrM0VTfXUZhqk63HkaiUS5A0UUtNmMvAr8eenmuFV1_oIyE1Tpps0R3q0keEHgZxblrdHKTRyfoZFsPIpIY311dweejsYTstDINDTMxKWyq1Lw14UIet4Ub4Mt4rzhU5Ppewos43-SFwqFyMOg']
def get_soup(url, show=False):
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
    })
    r = session.get(url)
    if show:
        display(r.content, 'temp.html')

    if r.status_code != 200: # not OK
        print('[get_soup] status code:', r.status_code)
    else:
        return BeautifulSoup(r.text, 'html.parser')

def post_soup(url, params, show=False):
    '''Read HTML from server and convert to Soup'''
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0',
    })
    r = session.post(url, data=params)
    
    if show:
        display(r.content, 'temp.html')

    if r.status_code != 200: # not OK
        print('[post_soup] status code:', r.status_code)
    else:
        return BeautifulSoup(r.text, 'html.parser')
def exportOnePage(soup, writer, listingType):
  for result in soup.find_all('a', class_='listingResult'):
    if result.find('div', class_='privateSellersText'):
      title = result.find('div', class_='infoHolder').find('div', class_='title')
      if title:
        title = title.text
      else:
        title = ''
      name = result.find('div', class_='agentBankOrPrivateSellerName')
      if name:
        name = name.text.strip()
      else:
        name = ''
      link = "https://www.privateproperty.co.za{}".format(result.attrs['href'])
      address = result.find('div', class_='address')
      if address:
        address = address.text
      else:
        address = ''

      description = ''
      features = result.find('div', class_='features')
      if features:
        number = result.find_all('div', class_='number')
        target = result.find_all('div', class_='icon')
        for i in range(len(number)):
          description += "{} {}, ".format(target[i].attrs['class'][1], number[i].text)
      uspsString = result.find('div', class_='uspsString')
      if uspsString:
        description += uspsString.text

      detail = get_soup(link)
      listingId = detail.find('div', class_='wishlistButton')
      if listingId:
        listingId = listingId.attrs['data-listing-id']
      else:
        listingId = ''
      payload = {
          'listingId': listingId,
          'listingType': listingType,
          'token': token[listingType],
          'rt': 'Listing_AgentPanel'
      }
      contactURL = 'https://www.privateproperty.co.za/Portal/Contact/GetAllListingContactNumber'
      contactNumbers = post_soup(contactURL, payload)
      contactNumbers = json.loads(str(contactNumbers))['contactNumbers']
      cell = ''
      home = ''
      work = ''
      if len(contactNumbers) > 0:
        cell = contactNumbers[0]["Cell"]
        home = contactNumbers[0]["Home"]
        work = contactNumbers[0]["Work"]

      else:
        contactNumber = ''

      item = [name.encode('utf-8'), cell.encode('utf-8'), home.encode('utf-8'), work.encode('utf-8'), link.encode('utf-8'), title.encode('utf-8'), address.encode('utf-8'), description.encode('utf-8')]
      print(item)
      writer.writerow(item)
  pass
def privateproperty(url):
    
    # pageNumbers[len(pageNumbers) - 2].text
    headers=['Name', 'Cell', 'Home', 'Work', 'Link', 'Title', 'Address', 'Description']
    csv.register_dialect('myDialect',
      quoting=csv.QUOTE_ALL,
      skipinitialspace=True)
    # url = 'https://www.privateproperty.co.za/for-sale/gauteng/pretoria/moot/882'
    if url.split('/')[3] == 'for-sale':
      listingType = 1
    elif url.split('/')[3] == 'to-rent':
      listingType = 2
    file_name = "{}_{}.csv".format(url.split('/')[3], url.split('/')[len(url.split('/')) - 2])
    with open(file_name, 'w') as f:
        

        soup = get_soup(url)
        pageNumber = soup.find_all('a', class_='pageNumber')
        pageNumber = pageNumber[len(pageNumber) - 2].text
        writer = csv.writer(f, dialect='myDialect')
        writer.writerow(headers)
        exportOnePage(soup, writer, listingType)
        for page in range(int(pageNumber) - 1):
          pageUrl = '{}?page={}'.format(url, page + 2)
          print(pageUrl)

          pageSoup = get_soup(pageUrl)
          exportOnePage(pageSoup, writer, listingType)

    f.close()        
    # print(get_soup(url))
  
    pass
if __name__ == '__main__':
  privateproperty(sys.argv[1])