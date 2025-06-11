# API2Spreadsheet

This project contains two Python scripts for:
1. Fetching Shopify orders and exporting them to Excel (`api_to_excel.py`)
2. Fetching data from a generic API and pushing it to Google Sheets (`api2_to_GSheet.py`)

## Table of Contents
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Configuration](#configuration)
- [Usage](#usage)
- [File Descriptions](#file-descriptions)
- [Error Handling](#error-handling)
- [License](#license)

## Features

### api_to_excel.py
- Fetches orders from Shopify API with pagination support
- Transforms order data into a structured format
- Handles various order statuses
- Generates Excel files with timestamped filenames
- Comprehensive error handling and logging

### api_to_GSheet.py
- Connects to a generic REST API
- Parses complex book order data
- Pushes processed data to Google Sheets
- Supports both JSON and string-formatted input
- Clears and updates entire worksheet automatically

## Prerequisites

- Python 3.6+
- Required Python packages:
  ```bash
  pip install pandas requests gspread oauth2client openpyxl python-dotenv


## Setup

1. Clone this repository
2. Install dependencies:
   ```bash
    pip install -r requirements.txt
3. For api_to_excel.py, create a .env file with:
   ```bash
    SHOP_NAME=your-shop-name
    ACCESS_TOKEN=your-access-token
    API_VERSION=api-version

4. For api_to_GSheet.py, obtain Google Service Account credentials and save as credentials.json

## Configuration

### api_to_excel.py

- Configure via environment variables:
  ```bash
    SHOP_NAME=your-shop-name
    ACCESS_TOKEN=your-access-token
    API_VERSION=api-version

### api2_to_Sheet.py

- Configure directly in the script:
  ```bash
    API_URL: Your target API endpoint
    API_HEADERS: Required API headers
    SPREADSHEET_NAME: Target Google Sheet name
    WORKSHEET_NAME: Specific worksheet name
    SERVICE_ACCOUNT_FILE: Path to Google credentials JSON

## Usage

- Run api_to_excel.py
   ```bash
      python api_to_excel.py
Output: Excel file with name pattern Shopify_Orders_YYYYMMDD_HHMM.xlsx

- Run api_to_GSheet.py
  ```bash
    python api_to_GSheet.py
Output: Updates specified Google Sheet with latest API data

## File Descriptions
### api_to_excel.py
1. Fetches Shopify orders via REST API
2. Processes line items and order metadata
3. Generates Excel output with standardized columns:
   - DocNum, LineNum, ItemCode, Quantity, Price
   - Currency, WhsCode, TaxCode, Project, U_E_Order_No

### api_to_GSheet.py
1. Connects to Google Sheets API
2. Parses book order data in multiple formats
3. Updates spreadsheet with columns:
   - Order ID, ISBN, Title, Quantity, Price

## Error Handling

Both scripts include comprehensive error handling:

- API connection timeouts
- Invalid responses
- Data parsing errors
- Google Sheets authentication failures
- File permission issues

Output includes status messages and error details for troubleshooting.

## License
This project is licensed under the MIT License.
