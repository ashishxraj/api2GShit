import pandas as pd
import requests
from datetime import datetime
import os
import getenv

# Configuration
SHOP_NAME = os.getenv("SHOP_NAME")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
API_VERSION = os.getenv("API_VERSION") 


api_headers = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def fetch_shopify_orders():
    """Fetch orders with pagination handling"""
    all_orders = []
    page = 1
    
    while True:
        url = f"https://{SHOP_NAME}/admin/api/{API_VERSION}/orders.json"
        response = requests.get(url, headers=api_headers)
        
        if response.status_code != 200:
            raise Exception(f"API request failed: {response.status_code} - {response.text}")
            
        data = response.json()
        orders = data.get('orders', [])
        
        if not orders:
            break
            
        all_orders.extend(orders)
        page += 1
        
    return all_orders

def transform_order_data(orders):
    """Extract and transform required fields"""
    output = []
    
    for order in orders:
        # Extract order metadata
        order_id = order.get('id', '')
        order_number = str(order.get('order_number', ''))
        currency = order.get('currency', 'INR')
        
        # Generate formatted fields
        project_code = f"#{order_number}_{order_id}"[:35]  # Truncate to 35 chars
        u_e_order_no = order.get('name', f"#{order_number}")
        
        # Process line items
        for idx, item in enumerate(order.get('line_items', []), start=1):
            output.append({
                "DocNum": "",
                "LineNum": idx,
                "ItemCode": item.get('sku') or f"PID_{item.get('product_id')}",
                "Quantity": int(item.get('quantity', 0)),
                "Price": float(item.get('price', 0)),
                "Currency": currency,
                "WhsCode": "",
                "TaxCode": "",
                "Project": project_code,
                "U_E_Order_No": u_e_order_no if idx == 1 else ""
            })
            
    return output

def main():
    try:
        # Fetch data from Shopify API
        print("Fetching orders from Shopify...")
        orders = fetch_shopify_orders()
        
        if not orders:
            print("No orders found!")
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

if __name__ == "__main__":
    main()