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
        "You are a Shopping Agent that helps users find products on Digi-Key. "
        "You will receive a JSON object containing 'product_name', 'budget', and 'features'. "
        "Your goal is to use these specific details to find the best matching product. "

        "IMPORTANT: You MUST use the digikey_product_search tool. "
        "1. Parse the input JSON. Construct a search query combining the 'product_name' and key 'features' (e.g., 'Battery AA 1.5V'). "
        "2. Call digikey_product_search with these terms. "
        "3. When you receive results: ANALYZE them against the 'budget' and 'features' from the input JSON. "
        "4. RECOMMEND ONLY THE SINGLE BEST PRODUCT. "

        "CURRENCY CONVERSION TOOLS:\n"
        "- Use convert_usd_to_pkr tool for PKR conversion. "
        "- Always provide both USD and PKR prices.\n"

        "ERROR HANDLING:\n"
        "- If the search returns no results, broaden your search terms (remove specific features) and try again. "
        "- If no products are found within the budget, recommend the cheapest available option and explain the price difference."
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
