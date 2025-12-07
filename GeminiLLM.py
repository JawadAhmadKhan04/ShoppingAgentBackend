import json
from google import generativeai as genai
from get_details import digikey_product_search
from currency_converter import convert_usd_to_pkr, convert_pkr_to_usd
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