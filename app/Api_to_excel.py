import pandas as pd
import requests
from datetime import datetime
import getenv 
import os

# Configuration
SHOP_NAME = os.getenv("SHOP_NAME")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION") 


api_headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def fetch_shopify_orders():
    print(" Attempting API connection...")
    url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/orders.json"
    params = {
        'status': 'any',
        'limit': 250
    }
    
    try:
        # Add timeout to prevent hanging
        response = requests.get(url, headers=api_headers, params=params, timeout=10)
        print(f" API Response Status: {response.status_code}")
        
        if response.status_code != 200:
            print(f" Full error response: {response.text}")
            raise Exception(...)
            
        return response.json().get('orders', [])
        
    except requests.exceptions.Timeout:
        print(" Timeout: Shopify API didn't respond within 10 seconds")
    except Exception as e:
        print(f" Unexpected error: {str(e)}")
    return []

def transform_order_data(orders):
    """Extract and transform required fields"""
    output = []
    
    for order in orders:
        # Extract order metadata
        order_id = order.get('id', '')
        order_number = str(order.get('order_number', ''))
        currency = order.get('currency', 'INR')
        payment_id = order.get('confirmation_number', '')
        project_code = f"{order_number}_{payment_id}"[:35]
        
        
        
        # Process line items
        line_items = order.get('line_items', [])
        if not line_items:
            output.append({
                "DocNum": "",
                "LineNum": "",
                "ItemCode": "",
                "Quantity": 0,
                "Price": 0.0,
                "Currency": currency,
                "WhsCode": "",
                "TaxCode": "",
                "Project": project_code,
                "U_E_Order_No":""
            })
            continue
        
        for idx, item in enumerate(line_items, start=1):
            row = {
                "DocNum": "",
                "LineNum": "",
                "ItemCode": item.get('sku') or f"PID_{item.get('product_id')}",
                "Quantity": int(item.get('quantity', 0)),
                "Price": float(item.get('price', 0)),
                "Currency": currency,
                "WhsCode": "",
                "TaxCode": "",
                "Project": "",
                "U_E_Order_No":""
            }
            # Only on the first line do we set Project and U_E_Order_No
            if idx == 1:
                row["Project"] = project_code
            
            output.append(row)
         
    return output

def main():
    try:
        # Fetch data from Shopify API
        print("Fetching orders from Shopify...")
        orders = fetch_shopify_orders()
        
        if not orders:
            print("No orders fetched!")
            return
        
            
        # Process data
        print("Processing orders...")
        formatted_data = transform_order_data(orders)
        
        # Create DataFrame
        columns = [
            "DocNum", "LineNum", "ItemCode", "Quantity", "Price",
            "Currency", "WhsCode", "TaxCode", "Project", "U_E_Order_No"
        ]
        df = pd.DataFrame(formatted_data, columns=columns)
        
        # Save to Excel
        filename = f"Shopify_Orders_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"Success! Saved {len(formatted_data)} line items to {filename}")
        
    except Exception as e:
        print(f" Error: {str(e)}")
    
    
    print(f" Successfully fetched {len(orders)} orders")


if __name__ == "__main__":
    main()