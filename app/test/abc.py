import requests
import pandas as pd
import os
import getenv

SHOP_NAME = os.getenv("SHOP_NAME")  
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

api_headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}



#API data fetching
'''api_url = f"https://{SHOP_NAME}/admin/api/2025-01/orders.json"

response = requests.get(api_url, headers=api_headers)
if response.status_code != 200:
        raise Exception(f"API request failed: {response.status_code}")
api_data = response.json()
orders = api_data.get('orders', [])
if orders:
        first_order = orders[0]
        print(first_order)
else:
        print("No orders found in the response.")'''

#API fulfilled orders fetching
'''response = requests.get(
    f"https://{SHOP_NAME}/admin/api/2025-01/orders.json?status=any&fulfillment_status=fulfilled",
    headers=api_headers
)

'''

response = requests.get(f"https://{SHOP_NAME}/admin/api/2025-01/orders/{11419821900144}/transactions.json", headers=api_headers)
orders = response.json()
 

print(orders)





# Mock API data
"""api_data = [
    {
        "project": "#1001_ProjectAlpha",
        "u_e_order_no": "ORD001_xYZ123abc",
        "books": [
            {"isbn": "978819364688", "quantity": 1, "price": 446.00, "currency": "INR"},
            {"isbn": "9789363860384", "quantity": 1, "price": 432.62, "currency": "INR"},
        ]
    },
    {
        "project": "#1002_ProjectBeta",
        "u_e_order_no": "ORD002_abcXYZ456",
        "books": [
            {"isbn": "9781203514710", "quantity": 2, "price": 141.62, "currency": "INR"}
        ]
    }
]
"""

# Final column layout
'''columns = [
    "DocNum", "LineNum", "ItemCode", "Quantity", "Price", "Currency",
    "WhsCode", "TaxCode", "Project", "U_E_Order_No"
]

rows = []

for order in api_data:
    books = order["books"]
    for i, book in enumerate(books):
        row = {
            "DocNum": "",  # to be filled by others
            "LineNum": "",  # to be filled by others
            "ItemCode": book["isbn"],
            "Quantity": book["quantity"],
            "Price": book["price"],
            "Currency": book["currency"],
            "WhsCode": "",  # to be filled by others
            "TaxCode": "",  # to be filled by others
            "Project": order["project"] if i == 0 else "",
            "U_E_Order_No": order["u_e_order_no"] if i == 0 else ""
        }
        rows.append(row)

# Create DataFrame
df = pd.DataFrame(rows, columns=columns)

# Export to Excel for testing
df.to_excel("formatted_orders_exact.xlsx", index=False, engine="openpyxl")
print("Excel created!")

'''