
from dotenv import load_dotenv
import os
import requests
import json

load_dotenv()

# 1. Get secrets
GLOBAL_CLIENT_ID = os.getenv("CLIENT_ID")
GLOBAL_CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"


import requests
import json

def digikey_product_search(search_keyword: str, record_count: int = 5) -> str:
    """
    Searches the Digi-Key API for product details based on a single keyword.
    
    Args:
        search_keyword: The component name (e.g., "resistor 10k ohm").
        record_count: The maximum number of results to retrieve (default is 5).
        
    Returns:
        A JSON string containing the search results, which the LLM will analyze.
    """
    # 2. Get Access Token once
    try:
        token_response = requests.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials"},
            auth=(GLOBAL_CLIENT_ID, GLOBAL_CLIENT_SECRET)
        )
        token_response.raise_for_status()
        GLOBAL_ACCESS_TOKEN = token_response.json()["access_token"]
        print("✅ Digi-Key Agent: Token acquired for all subsequent tool calls.")
    except Exception as e:
        print(f"❌ Digi-Key Agent Fatal Error: Token acquisition failed. {e}")
        # You would typically exit or log a critical error here
        GLOBAL_ACCESS_TOKEN = None

    # Check if authentication was successful during setup
    if not GLOBAL_ACCESS_TOKEN:
        return "ERROR: Digi-Key API token is missing or expired. Cannot proceed."
        
    URL = "https://api.digikey.com/products/v4/search/keyword"

    headers = {
        "X-DIGIKEY-Client-Id": GLOBAL_CLIENT_ID,
        "Authorization": f"Bearer {GLOBAL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "Keywords": search_keyword,
        "RecordCount": record_count
    }

    try:
        response = requests.post(URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        
        # Extract relevant fields from the response
        api_response = response.json()
        
        # Parse and format the results for the LLM
        results = []
        if "Products" in api_response and api_response["Products"]:
            for product in api_response["Products"]:
                product_info = {
                    "part_number": product.get("DigiKeyPartNumber", "N/A"),
                    "manufacturer_part_number": product.get("ManufacturerPartNumber", "N/A"),
                    "product_description": product.get("ProductDescription", "N/A"),
                    "category": product.get("Category", {}).get("CategoryName", "N/A"),
                    "unit_price": product.get("PriceBreaks", [{}])[0].get("UnitPrice", "N/A") if product.get("PriceBreaks") else "N/A",
                    "quantity_available": product.get("QuantityAvailable", 0),
                    "manufacturer": product.get("Manufacturer", {}).get("Name", "N/A") if product.get("Manufacturer") else "N/A",
                }
                results.append(product_info)
        
        # Return formatted results for LLM to analyze
        formatted_response = {
            "search_keyword": search_keyword,
            "total_products_found": len(results),
            "products": results,
            "api_response_summary": {
                "has_products_key": "Products" in api_response,
                "status": "success" if results else "no_results",
                "raw_response_keys": list(api_response.keys())
            }
        }
        
        print(f"✅ Digi-Key Agent: Retrieved {len(results)} products for '{search_keyword}'.")

        return json.dumps(formatted_response)
    
    except requests.exceptions.HTTPError as e:
        return f"API ERROR ({response.status_code}): Could not retrieve results for '{search_keyword}'. Details: {response.text}"
    except Exception as e:
        return f"TOOL EXECUTION ERROR: An unexpected error occurred: {e}"