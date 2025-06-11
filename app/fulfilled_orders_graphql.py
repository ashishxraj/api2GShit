'''import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import openpyxl
import os

# Shopify credentials
SHOP_URL = os.getenv("SHOP_NAME")
API_VERSION = os.getenv("API_VERSION") 
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
GRAPHQL_URL = f"https://{SHOP_URL}/admin/api/{API_VERSION}/graphql.json"
HEADERS = {
    "X-Shopify-Access-Token": ACCESS_TOKEN,
    "Content-Type": "application/json"
}

def fetch_fulfilled_orders_graphql():
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)
    
    orders = []
    has_next_page = True
    cursor = None

    while has_next_page:
        query = f"""
        query {{
            orders(first: 50, query: "fulfillment_status:fulfilled"{', after: "%s"' % cursor if cursor else ''}) {{
                pageInfo {{
                    hasNextPage
                }}
                edges {{
                    cursor
                    node {{
                        id
                        name
                        orderNumber
                        currencyCode
                        confirmationNumber
                        lineItems(first: 10) {{
                            edges {{
                                node {{
                                    sku
                                    quantity
                                    price
                                    product {{
                                        id
                                    }}
                                }}
                            }}
                        }}
                        fulfillments {{
                            processedAt
                        }}
                    }}
                }}
            }}
        }}
        """

        response = requests.post(GRAPHQL_URL, json={"query": query}, headers=HEADERS)
        response.raise_for_status()
        response_json = response.json()
        print("GRAPHQL RESPONSE:", response_json)

        if "errors" in response_json:
            raise Exception(f"GraphQL Errors: {response_json['errors']}")

        if "data" not in response_json or "orders" not in response_json["data"]:
            raise Exception("Missing 'orders' data in response.")

        data = response_json["data"]["orders"]

        
    for edge in data["edges"]:
            order = edge["node"]
            cursor = edge["cursor"]
            
            # Only add if fulfillment is processed today
            for fulfillment in order["fulfillments"]:
                processed_at = datetime.fromisoformat(fulfillment["processedAt"].replace("Z", "+00:00"))
                if today_start <= processed_at <= today_end:
                    orders.append({
                        "id": order["id"],
                        "order_number": order["orderNumber"],
                        "currency": order.get("currencyCode", "INR"),
                        "confirmation_number": order.get("confirmationNumber", ""),
                        "line_items": [
                            {
                                "sku": li["node"].get("sku"),
                                "quantity": li["node"].get("quantity", 0),
                                "price": li["node"].get("price", 0),
                                "product_id": li["node"].get("product", {}).get("id", "")
                            }
                            for li in order["lineItems"]["edges"]
                        ]
                    })
                    break  # skip re-checking other fulfillments
        
            has_next_page = data["pageInfo"]["hasNextPage"]

    return orders

def transform_order_data(orders):
    output = []
    
    for order in orders:
        order_id = order.get('id', '')
        order_number = str(order.get('order_number', ''))
        currency = order.get('currency', 'INR')
        payment_id = order.get('confirmation_number', '')
        project_code = f"{order_number}_{payment_id}"[:35]
        
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
                "U_E_Order_No": ""
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
                "U_E_Order_No": ""
            }
            if idx == 1:
                row["Project"] = project_code
            output.append(row)
         
    return output

def main():
    try:
        print(" Fetching fulfilled orders (GraphQL)...")
        orders = fetch_fulfilled_orders_graphql()
        
        if not orders:
            print(" No fulfilled orders found for today!")
            return
        
        print(" Transforming data...")
        formatted_data = transform_order_data(orders)
        
        columns = [
            "DocNum", "LineNum", "ItemCode", "Quantity", "Price",
            "Currency", "WhsCode", "TaxCode", "Project", "U_E_Order_No"
        ]
        df = pd.DataFrame(formatted_data, columns=columns)
        
        #  Update (not create new) Excel file
        file_path = "Fulfilled_Orders.xlsx"
        if not os.path.exists(file_path):
            df.to_excel(file_path, index=False, engine='openpyxl')
        else:
            existing = pd.read_excel(file_path)
            updated = pd.concat([existing, df], ignore_index=True)
            updated.to_excel(file_path, index=False, engine='openpyxl')
        
        print(f" Saved {len(formatted_data)} rows to {file_path}")
    
    except Exception as e:
        print(f" Error: {str(e)}")

if __name__ == "__main__":
    main()'''


import requests
import pandas as pd
import os
import dotenv
from datetime import datetime, timedelta, timezone

SHOP_URL = os.getenv("SHOP_NAME")
API_VERSION = os.getenv("API_VERSION") 
SHOPIFY_ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

GRAPHQL_URL = f"https://{SHOP_URL}/admin/api/{API_VERSION}/graphql.json"

headers = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": SHOPIFY_ACCESS_TOKEN
}

# Daily timeframe: from 00:00 to now
today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
today_end = datetime.now(timezone.utc).isoformat()

# Query to get fulfilled orders created *anytime*, fulfilled today
QUERY = """
query ($cursor: String) {
  orders(first: 50, after: $cursor, query: "fulfillment_status:fulfilled") {
    pageInfo {
      hasNextPage
    }
    edges {
      cursor
      node {
        id
        name
        currencyCode
        confirmationNumber

        lineItems(first: 10) {
          edges {
            node {
              sku
              quantity
              product {
                id
              }
              originalTotalSet {
                presentmentMoney {
                  amount
                }
              }
            }
          }
        }

        fulfillments {
          createdAt
        }
      }
    }
  }
}
"""

def fetch_fulfilled_orders():
    print("Fetching fulfilled orders (GraphQL)...")
    
    orders = []
    cursor = None

    while True:
        variables = {"cursor": cursor}
        response = requests.post(GRAPHQL_URL, headers=headers, json={"query": QUERY, "variables": variables})
        result = response.json()

        if "errors" in result:
            raise Exception(f"GraphQL Errors: {result['errors']}")

        data = result.get("data", {}).get("orders", {})
        edges = data.get("edges", [])

        for edge in edges:
            order = edge["node"]
            ''' Check if any fulfillment happened today'''
            fulfillments = order.get("fulfillments", [])
            #if fulfillments:
            if any(today_start <= f["createdAt"] <= today_end for f in fulfillments):
                orders.append(order)

        if not data.get("pageInfo", {}).get("hasNextPage"):
            break

        cursor = edges[-1]["cursor"]

    return orders



def fetch_payment_id(order_id):
    url = f"https://{SHOP_URL}/admin/api/{API_VERSION}/orders/{order_id.split('/')[-1]}/transactions.json"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch transaction for order {order_id}")
        return ""
    data = response.json().get("transactions", [])

    for txn in data:
        if txn.get("status") == "success":
            return txn.get("payment_id","")  

    return ""


def transform_order_data(orders):
    """Extract and transform required fields"""
    output = []

    for order in orders:
        order_number = order.get("name", "")
        currency = order.get("currencyCode", "")
        raw_order_id = order.get("id", "")
        order_id = raw_order_id.split("/")[-1]  # Extract the numeric ID
        payment_id = fetch_payment_id(order_id)
        project_code = f"{order_number}_{payment_id}"[:35]

        line_items = order.get("lineItems", {}).get("edges", [])
        if not line_items:
            output.append({
                "DocNum": "", "LineNum": "", "ItemCode": "", "Quantity": 0,
                "Price": 0.0, "Currency": currency, "WhsCode": "", "TaxCode": "",
                "Project": project_code, "U_E_Order_No": ""
            })
            continue

        for idx, item_edge in enumerate(line_items, start=1):
            item = item_edge["node"]
            row = {
                "DocNum": "",
                "LineNum": "",
                "ItemCode": item.get("sku") or f"PID_{item.get('product', {}).get('id')}",
                "Quantity": int(item.get("quantity", 0)),
                "Price": float(item.get("originalTotalSet", {}).get("presentmentMoney", {}).get("amount", 0)),
                "Currency": currency,
                "WhsCode": "",
                "TaxCode": "",
                "Project": "",
                "U_E_Order_No": ""
            }
            if idx == 1:
                row["Project"] = project_code
            output.append(row)

    return output


def update_excel(data, filename="fulfilled_orders_daily.xlsx"):
    """Update the same Excel sheet daily"""
    try:
        df_old = pd.read_excel(filename)
    except FileNotFoundError:
        df_old = pd.DataFrame(columns=[
            "DocNum", "LineNum", "ItemCode", "Quantity", "Price",
            "Currency", "WhsCode", "TaxCode", "Project", "U_E_Order_No"
        ])

    df_new = pd.DataFrame(data)
    df_updated = pd.concat([df_old, df_new], ignore_index=True)

    df_updated.to_excel(filename, index=False)
    print(f" Updated {filename} with {len(df_new)} new rows.")


def main():
    try:
        orders = fetch_fulfilled_orders()
        if not orders:
            print(" No fulfilled orders found today.")
            return

        transformed = transform_order_data(orders)
        update_excel(transformed)

    except Exception as e:
        print(f" Error: {str(e)}")


if __name__ == "__main__":
    main()

