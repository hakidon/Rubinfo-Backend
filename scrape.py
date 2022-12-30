import requests
from bs4 import BeautifulSoup

# Make a request to the website
response = requests.get('http://www3.lgm.gov.my/mre/daily.aspx')

# Parse the HTML content of the page
soup = BeautifulSoup(response.text, 'html.parser')

# price_date = soup.find('div', {'id': 'languagebarleft'}).find('span', {'class': 'noteright'}).find('span', {'id': '_ctl0_lblDate'}).text
price_date = soup.find('table', {'id': 'tblRubberPrices'}).find('td', {'id': 'Current'}).find('center').find('font', color='maroon').text
print(price_date)
# from datetime import datetime

# # Parse the input date string
# date = datetime.strptime(price_date, "%I:%M:%S %p %A, %d %B %Y")

# # Format the date as "YYYY-MM-DD"
# formatted_date = date.strftime("%Y-%m-%d")

# print(formatted_date)  # Output: "2022-12-29"

# td_element = soup.find('table', {'id': '_ctl0_ContentPlaceHolder1_tblBulkNoon'})
# bulk_latex_price = td_element.find('tr').find('td', {'class': 'gveven'}).find('span', {'id': '_ctl0_ContentPlaceHolder1_lblBulkNoon_S'}).text

#29 December 2022
#turn this into yyyy-mm-dd

# find content with id '_ctl0_ContentPlaceHolder1_lblBulkNoon_S'

# # Find the table containing the exchange rates
# table = soup.find('table', {'id': 'gvRates'})

# # Iterate through the rows of the table
# for row in table.find_all('tr')[1:]:
#     # Get the currency code and name cells
#     code_cell, name_cell, *_ = row.find_all('td')
    
#     # Get the text content of the cells
#     code = code_cell.text
#     name = name_cell.text
    
#     # Print the currency code and name
#     print(f'{code}: {name}')