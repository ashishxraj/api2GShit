import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuration
API_URL = 'https://api.example.com/orders'
API_HEADERS = {'Authorization': 'Bearer YOUR_API_KEY'}
SPREADSHEET_NAME = 'Book Orders'
WORKSHEET_NAME = 'Orders'
SERVICE_ACCOUNT_FILE = 'credentials.json'

def main():
    # Set up Google Sheets connection
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(
        SERVICE_ACCOUNT_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).worksheet(WORKSHEET_NAME)

    # Fetch data from API
    response = requests.get(API_URL, headers=API_HEADERS)
    if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}")
    orders = response.json()

    # Process data
    rows = []
    for order in orders:
        order_id = order.get('order_id')
        books = parse_books(order.get('books', []))
        
        for book in books:
            rows.append([
                order_id,
                book.get('isbn'),
                book.get('title'),
                book.get('quantity'),
                book.get('price')
            ])

    # Update Google Sheet
    if rows:
        sheet.clear()
        sheet.append_rows([['Order ID', 'ISBN', 'Title', 'Quantity', 'Price']] + rows)
        print(f"Successfully updated {len(rows)} book entries")
    else:
        print("No data to update")

def parse_books(books_data):
    """Parse books data which could be a list or a string"""
    if isinstance(books_data, str):
        return parse_books_from_string(books_data)
    return books_data  # Assume it's already a list of dictionaries

def parse_books_from_string(books_str):
    """Parse books from a semicolon-separated string"""
    books = []
    for book_str in books_str.split(';'):
        parts = [part.strip() for part in book_str.split(',')]
        if len(parts) >= 4:
            books.append({
                'isbn': parts[0],
                'title': parts[1],
                'quantity': parts[2],
                'price': parts[3]
            })
    return books

if __name__ == '__main__':
    main()