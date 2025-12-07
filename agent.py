import json
from google import generativeai as genai
from get_details import digikey_product_search
from currency_converter import convert_usd_to_pkr, convert_pkr_to_usd
from dotenv import load_dotenv
import os
from GeminiLLM import GeminiLLM

load_dotenv()

# -----------------------------
# 2. SHOPPING AGENT
# -----------------------------
class ShoppingAgent:

    def __init__(self, llm):
        self.llm = llm

    def get_tools(self):
        return [
            {
                "function_declarations": [
                    {
                        "name": "digikey_product_search",
                        "description": "Search the Digi-Key API for items to shop. Use this tool whenever the user asks to find products, parts, or components.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "search_keyword": {
                                    "type": "STRING",
                                    "description": "The product to search for. Example: '10k resistor', '100uF capacitor', 'LED'."
                                },
                                "record_count": {
                                    "type": "INTEGER",
                                    "description": "Number of results to fetch. Default is 5."
                                }
                            },
                            "required": ["search_keyword"]
                        }
                    },
                    {
                        "name": "convert_usd_to_pkr",
                        "description": "Convert prices from USD (US Dollars) to PKR (Pakistani Rupees). Use this when you need to help users understand prices in their local currency.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "usd_amount": {
                                    "type": "NUMBER",
                                    "description": "The amount in USD to convert to PKR. Example: 10.50, 100.00"
                                }
                            },
                            "required": ["usd_amount"]
                        }
                    },
                    {
                        "name": "convert_pkr_to_usd",
                        "description": "Convert prices from PKR (Pakistani Rupees) to USD (US Dollars). Use this when you need to help users understand prices in USD.",
                        "parameters": {
                            "type": "OBJECT",
                            "properties": {
                                "pkr_amount": {
                                    "type": "NUMBER",
                                    "description": "The amount in PKR to convert to USD. Example: 1000.00, 5000.50"
                                }
                            },
                            "required": ["pkr_amount"]
                        }
                    }
                ]
            }
        ]

    def run(self, user_message: str) -> str:
        system_msg = (
        "You are a Shopping Agent that helps users find products on Digi-Key and understand pricing in multiple currencies. "
        "IMPORTANT: You MUST use the digikey_product_search tool for ANY request to find, search, or look up products. "
        "Extract the key search terms from the user's request and call the tool to search. "
        "When you receive product results from the API, ANALYZE ALL OPTIONS AND RECOMMEND ONLY THE SINGLE BEST PRODUCT. "
        "Base your recommendation on: 1) User's price criteria if mentioned, 2) Availability (quantity available), 3) Best value. "
        "Return ONLY ONE PRODUCT RECOMMENDATION with its details. Do NOT list multiple options. "
        "If results are provided by the API, present the best one regardless of the product category. "
        "Do NOT assume what Digi-Key sells - trust the API results. "
        "\n"
        "CURRENCY CONVERSION TOOLS:\n"
        "- Use convert_usd_to_pkr tool: When you need to convert USD prices to Pakistani Rupees (PKR). "
        "- Use convert_pkr_to_usd tool: When you need to convert Pakistani Rupees (PKR) prices to USD. "
        "- Always provide both USD and PKR prices in your final response for clarity.\n"
        "\n"
        "EXAMPLE CHAIN-OF-THOUGHT:\n"
        "User: 'Find me a 10k resistor and tell me the price in PKR'\n"
        "1. Search for '10k resistor' using digikey_product_search\n"
        "2. Receive product: unit_price = 0.05 USD, quantity = 1000\n"
        "3. Convert 0.05 USD to PKR using convert_usd_to_pkr(0.05)\n"
        "4. Response: 'I found a 10k Resistor at 0.05 USD (≈13.90 PKR). With 1000 units available, it's a reliable choice.'\n"
        "\n"
        "If no products are found within the price range, recommend the cheapest available option. "
        "Make a professional response to the user."
        )


        messages = [
            {"role": "user", "content": system_msg + "\n\n" + user_message}
        ]

        response = self.llm.chat_completion(
            messages=messages,
            tools=self.get_tools(),
            tool_choice="auto"
        )

        if response["tool_calls"]:
            tool_call = response["tool_calls"][0]
            tool_name = tool_call["name"]
            tool_args = json.loads(tool_call["arguments"])

            print(f"🛠️ ShoppingAgent → Executing tool: {tool_name}, args={tool_args}")

            if tool_name == "digikey_product_search":
                tool_result = digikey_product_search(**tool_args)
            elif tool_name == "convert_usd_to_pkr":
                conversion_result = convert_usd_to_pkr(**tool_args)
                tool_result = json.dumps(conversion_result)
            elif tool_name == "convert_pkr_to_usd":
                conversion_result = convert_pkr_to_usd(**tool_args)
                tool_result = json.dumps(conversion_result)
            else:
                return "ERROR: Unrecognized tool."

            followup_messages = messages + [
                {"role": "model", "content": response["content"]},
                {
                    "role": "user",
                    "content": f"Tool result: {tool_result}"
                }
            ]

            final_response = self.llm.chat_completion(
                messages=followup_messages,
                tools=self.get_tools(),
                tool_choice="none"
            )

            return final_response["content"]

        return response["content"]


# -----------------------------
# 3. USAGE
# -----------------------------
agent = ShoppingAgent(
    GeminiLLM(api_key=os.getenv("GEMINI_API_KEY"))
)

answer = agent.run("Find me a 10k resistor and tell me the price in PKR")
print(answer)
