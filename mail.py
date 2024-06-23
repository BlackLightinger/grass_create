import requests
from bs4 import BeautifulSoup


def get_email():
    response = requests.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1')
    temp_email = response.json()[0]
    return temp_email


def get_code(email):
    email_data = email.split('@')
    while True:
        response = requests.get(
            f'https://www.1secmail.com/api/v1/?action=getMessages&login={email_data[0]}&domain={email_data[1]}').json()
        if len(response) != 0:
            email_id = response[0]['id']
            break

    response = requests.get(
        f'https://www.1secmail.com/api/v1/?action=readMessage&login={email_data[0]}&domain={email_data[1]}&id={email_id}').json()

    soup = BeautifulSoup(response['body'], 'html.parser')
    verification_code = soup.find('div', style='padding: 10px 40px 35px 40px;').text.strip()
    return verification_code
