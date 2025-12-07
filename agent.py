import json
from google import generativeai as genai
from get_details import digikey_product_search
from currency_converter import convert_usd_to_pkr
from dotenv import load_dotenv
import os

load_dotenv()
# -----------------------------
# 1. GEMINI TOOL-CALLING WRAPPER
# -----------------------------
class GeminiLLM:

    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
            
        self.model = genai.GenerativeModel(model_name="gemini-2.5-flash",)

    def chat_completion(self, messages, tools=None, tool_choice="auto"):
        converted_messages = [
            {"role": m["role"], "parts": [m["content"]]} for m in messages
        ]

        if tools:
            tool_config = {"function_calling_config": {"mode": "AUTO"}}
        else:
            tool_config = None

        response = self.model.generate_content(
            contents=converted_messages,
            tools=tools,
            tool_config=tool_config
        )

        # Parse tool calls
        tool_calls = []
        content = ""
        
        for part in getattr(response, "parts", []):
            if getattr(part, "function_call", None):
                tool_calls.append({
                    "id": "toolcall-1",
                    "name": part.function_call.name,
                    "arguments": json.dumps(dict(part.function_call.args))
                })
            elif hasattr(part, "text"):
                content = part.text

        return {
            "content": content,
            "tool_calls": tool_calls if tool_calls else None
        }


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
                    }
                ]
            }
        ]

    def run(self, user_message: str) -> str:
        system_msg = (
        "You are a Shopping Agent that helps users find products on Digi-Key. "
        "IMPORTANT: You MUST use the digikey_product_search tool for ANY request to find, search, or look up products. "
        "Extract the key search terms from the user's request and call the tool to search. "
        "When you receive product results from the API, ANALYZE ALL OPTIONS AND RECOMMEND ONLY THE SINGLE BEST PRODUCT. "
        "Base your recommendation on: 1) User's price criteria if mentioned, 2) Availability (quantity available), 3) Best value. "
        "Return ONLY ONE PRODUCT RECOMMENDATION with its details. Do NOT list multiple options. "
        "If results are provided by the API, present the best one regardless of the product category. "
        "Do NOT assume what Digi-Key sells - trust the API results. "
        "If the user asks for prices in PKR, use the convert_usd_to_pkr tool to convert USD prices to PKR. "
        "If no products are found within the price range, recommend the cheapest available option. "
        "Make a professional response to the user"
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
# agent = ShoppingAgent(
#     GeminiLLM(api_key=os.getenv("GEMINI_API_KEY"))
# )

# answer = agent.run("I need an AC to DC converter.")
# print(answer)
