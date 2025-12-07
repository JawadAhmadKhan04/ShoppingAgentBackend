"""
Currency conversion utilities for shopping agent.
"""

def convert_usd_to_pkr(usd_amount: float) -> dict:
    """
    Converts USD to PKR using current exchange rate.
    
    Args:
        usd_amount: Amount in USD to convert
        
    Returns:
        A dictionary with the conversion details
    """
    # Current exchange rate (you can update this or fetch from an API)
    # As of December 2025, approximate rate is 1 USD = 277-280 PKR
    print("Currency converter: Converting USD to PKR.")
    exchange_rate = 278.0
    
    pkr_amount = usd_amount * exchange_rate
    
    return {
        "usd_amount": usd_amount,
        "pkr_amount": round(pkr_amount, 2),
        "exchange_rate": exchange_rate,
        "currency_pair": "USD/PKR"
    }
