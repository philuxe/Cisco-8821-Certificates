"""
    Author: Philippe Blavier
    Email : philuxe222@hotmail.com
    Date created: 4/02/2021
    Python Version: 3.8
"""

import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import csv
import logging

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
# https://github.com/psf/requests/issues/1495
# https://www.javaer101.com/en/article/2938774.html

# proxies = {
#    'http': 'http://localhost:8866',
#    'https': 'http://localhost:8866',
# }

proxies = None

logging.basicConfig(format='%(asctime)s - %(levelname) s - %(message)s', level=logging.WARNING, filename='8821.log',
                    filemode='a')

PHONE_USERNAME = "admin"
PHONE_PASSWORD = "PASSWORD"
CERT_PASSWORD = "KEY"

PATH_LOGIN_URL = ":8443/CGI/Java/Serviceability?adapter=loginPost"
PATH_CERT_URL = ":8443/CGI/Java/Serviceability?adapter=certificate"
DEL_CERT_SERVER_URL = ":8443/CGI/Java/Serviceability?adapter=remove_webrootcert"
DEL_CERT_USER_URL = ":8443/CGI/Java/Serviceability?adapter=remove_usercert"
ADD_CERT_USER_URL = ":8443/CGI/Java/Serviceability?adapter=upload_usercert"
headers = dict()


def phone_login(ip_address, user_name, user_password):
    s = requests.session()
    url = 'https://' + ip_address + PATH_LOGIN_URL
    headers['Accept-Language'] = 'en-US,en;q=0.5'
    # FIRST REQUEST IS GETTING CRSF TOKEN
    try:
        r = s.get(url, verify=False, proxies=proxies, headers=headers)
    except requests.exceptions.RequestException:
        return None, None
    logging.warning("Connection Successfull to %s", ip_address)
    # print(s.cookies)
    soup = BeautifulSoup(r.text, "html.parser")
    csrf_token = soup.find('input', {'name': 'CSRFToken'})['value']
    files = {'CSRFToken': (None, csrf_token), 'username': (None, user_name), 'userPassword': (None, user_password)}
    headers['Host'] = ip_address + ':8443'
    headers['Referer'] = 'https://' + ip_address + ':8443/CGI/Java/Serviceability?adapter=device.statistics.device'
    print("Authentication:")
    r2 = s.post(url, headers=headers, files=files, verify=False, proxies=proxies)
    print(r2.status_code)
    return s, csrf_token


def phone_get_certs(session, ip_address):
    # ######### DISPLAY INSTALLED CERTS
    url = 'https://' + ip_address + PATH_CERT_URL
    r = session.get(url, verify=False, proxies=proxies)
    # print(r.text)
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find("table", attrs={"id": "table2"})
    output_rows = []
    for table_row in table.find_all('tr'):
        columns = table_row.findAll('td')
        output_row = []
        for i in columns:
            output_row.append(i.text)
        output_rows.append(output_row)

    # print(output_rows)
    print("Current USER & SERVER Certificates:")
    print(output_rows[4])
    print(output_rows[5])


def phone_del_root_cert(session, csrf_token, ip_address):
    # ## SUPPRESSION DU CERT SERVER
    headers['Referer'] = 'https://' + ip_address + ':8443/CGI/Java/Serviceability?adapter=certificate'
    payload2 = {'CSRFToken': csrf_token}

    r2 = session.post('https://' + ip_address + DEL_CERT_SERVER_URL, files=payload2,
                      proxies=proxies, verify=False)
    print("Removing SERVER Certificate:")
    print(r2.status_code)


def phone_del_user_cert(session, csrf_token, ip_address,sep_name):
    headers['Referer'] = 'https://' + ip_address + ':8443/CGI/Java/Serviceability?adapter=certificate'
    payload2 = {'CSRFToken': csrf_token}
    r2 = session.post('https://' + ip_address + DEL_CERT_USER_URL, files=payload2,
                      proxies=proxies, verify=False)
    print("Removing USER Certificate:")
    print(r2.status_code)
    if r2.status_code == 200:
        logging.warning("User Certificate has been removed on %s", sep_name)
    else:
        logging.warning("User Certificate has been removed on %s", sep_name)


def phone_add_user_cert(session, csrf_token, ip_address, sep_name):
    pfx_file = sep_name + ".pfx"
    headers['Referer'] = 'https://' + ip_address + ':8443/CGI/Java/Serviceability?adapter=install_usercert'
    files = {'CSRFToken': (None, csrf_token), 'usercert': (
        pfx_file, open(pfx_file, 'rb'), 'application/x-pkcs12'),
             'Password': CERT_PASSWORD}
    print("Uploading USER Certificate:")
    r = session.post('https://' + ip_address + ADD_CERT_USER_URL, files=files, headers=headers, verify=False,
                     proxies=proxies)
    print(r.status_code)
    if r.status_code == 200:
        logging.warning("User Certificate has been uploaded for %s", sep_name)
    else:
        logging.warning("User Certificate upload failed for %s", sep_name)


def menu():
    print("[D] -- Display current certificates")
    print("[S] -- Delete Server certificates --> will NOT trigger wifi reauth'")
    print("[U] -- Delete User certificates --> will NOT trigger wifi reauth")
    print("[A] -- Upload User certificates  --> will replace existing certificate, wifi restart")


menu()
choice = input("Enter your option: ")
logging.critical("Program started")

if choice == "D":
    logging.debug("User requested Certificate query and display")
    input_file = input("Enter the filename with complete file path:  ")
    logging.debug("Input file is %s", input_file)
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            phone_name = str(row['PHONE_NAME'])
            line_name = str(row['LINE_NAME'])
            PHONE_IP = str(row['IP_ADDRESS'])
            logging.warning("Processing %s - %s - %s", phone_name, line_name, PHONE_IP)
            my_session, token = phone_login(PHONE_IP, PHONE_USERNAME, PHONE_PASSWORD)
            if my_session and token:
                phone_get_certs(my_session, PHONE_IP)
            else:
                logging.warning("Cannot connect to %s", PHONE_IP)

elif choice == "S":
    logging.debug("User requested Server Certificate suppression")
    input_file = input("Enter the filename with complete file path:  ")
    logging.debug("Input file is %s", input_file)
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            phone_name = str(row['PHONE_NAME'])
            line_name = str(row['LINE_NAME'])
            PHONE_IP = str(row['IP_ADDRESS'])
            logging.warning("Processing %s - %s - %s", phone_name, line_name, PHONE_IP)

            my_session, token = phone_login(PHONE_IP, PHONE_USERNAME, PHONE_PASSWORD)
            if my_session and token:
                phone_del_root_cert(my_session, token, PHONE_IP)
            else:
                logging.warning("Cannot connect to %s", PHONE_IP)

elif choice == "U":
    logging.debug("User requested User Certificate suppression")
    input_file = input("Enter the filename with complete file path:  ")
    logging.debug("Input file is %s", input_file)
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            phone_name = str(row['PHONE_NAME'])
            line_name = str(row['LINE_NAME'])
            PHONE_IP = str(row['IP_ADDRESS'])
            logging.warning("Processing %s - %s - %s", phone_name, line_name, PHONE_IP)

            my_session, token = phone_login(PHONE_IP, PHONE_USERNAME, PHONE_PASSWORD)
            if my_session and token:
                phone_del_user_cert(my_session, token, PHONE_IP, phone_name)
            else:
                logging.warning("Cannot connect to %s", PHONE_IP)

elif choice == "A":
    logging.debug("User requested User Certificate upload")
    input_file = input("Enter the filename with complete file path:  ")
    logging.debug("Input file is %s", input_file)
    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        for row in reader:
            phone_name = str(row['PHONE_NAME'])
            line_name = str(row['LINE_NAME'])
            PHONE_IP = str(row['IP_ADDRESS'])
            logging.warning("Processing %s - %s - %s", phone_name, line_name, PHONE_IP)

            my_session, token = phone_login(PHONE_IP, PHONE_USERNAME, PHONE_PASSWORD)
            if my_session and token:
                phone_add_user_cert(my_session, token, PHONE_IP, phone_name)
            else:
                logging.warning("Cannot connect to %s", PHONE_IP)

else:
    exit("wrong key pressed")


