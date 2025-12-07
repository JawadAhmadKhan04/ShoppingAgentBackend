# Shopping Agent Backend

An intelligent AI-powered shopping agent backend built with FastAPI and Google's Gemini API. This agent helps users find products on Digi-Key with smart recommendations, tool calling capabilities, and currency conversion support.

## 🎯 Features

- **AI-Powered Product Search**: Uses Google Gemini 2.5 Flash to understand user requests and search for products
- **Digi-Key Integration**: Direct integration with Digi-Key API for real-time product information
- **Smart Recommendations**: Analyzes multiple product options and recommends the best match based on price, availability, and value
- **Currency Conversion**: Automatic USD to PKR conversion for Pakistani users
- **Tool Calling**: Leverages Gemini's function calling capabilities for autonomous decision-making
- **RESTful API**: Built with FastAPI for high performance and easy integration

## 📋 Project Structure

```
shopping_agent_backend/
├── main.py                    # FastAPI application entry point
├── agent.py                   # Shopping agent and LLM wrapper
├── get_details.py             # Digi-Key API integration
├── currency_converter.py      # USD to PKR conversion utility
├── pyproject.toml             # Project metadata and dependencies
├── .env                       # Environment variables (secrets)
├── requirements.txt           # Pinned dependencies
└── README.md                  # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.10 or higher
- Digi-Key API credentials (CLIENT_ID and CLIENT_SECRET)
- Google Gemini API key

### Setup Steps

1. **Clone the repository** (or navigate to the project directory)
   ```bash
   cd shopping_agent_backend
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   # Or using requirements.txt
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   
   Create a `.env` file in the root directory with:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   CLIENT_ID=your_digikey_client_id
   CLIENT_SECRET=your_digikey_client_secret
   ```

## 🚀 Usage

### Starting the Server

Run the FastAPI server:
```bash
uvicorn main:app --reload
```

The server will start at `http://localhost:8000`

### API Endpoints

#### Search Products
- **Endpoint**: `POST /search`
- **Request Body**:
  ```json
  {
    "output": "I need a 10k resistor"
  }
  ```
- **Response**:
  ```json
  {
    "result": "I found the best option for you: [product details with price, availability, etc.]"
  }
  ```

### Example Requests

```bash
# Search for a resistor
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"output": "I need a 10k ohm resistor"}'

# Search for AC to DC converter
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"output": "I need an AC to DC converter with 12V output"}'

# Search with price criteria
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{"output": "I need a capacitor under 500 PKR"}'
```

## 📚 Architecture

### Components

#### 1. **main.py** - FastAPI Application
- Initializes the FastAPI server
- Defines the Query model with Pydantic
- Implements the `/search` endpoint
- Orchestrates requests between API and the ShoppingAgent

#### 2. **agent.py** - Shopping Agent & LLM Wrapper
- **GeminiLLM Class**: Wraps Google's Generative AI API
  - Handles model initialization with `gemini-2.5-flash`
  - Implements chat completion with tool calling
  - Parses function calls from Gemini responses
  
- **ShoppingAgent Class**: Main shopping logic
  - Manages tool definitions for `digikey_product_search` and `convert_usd_to_pkr`
  - Executes the agent loop with:
    - Initial user query
    - Tool execution
    - Follow-up response generation
  - Analyzes all product options and recommends the single best match

#### 3. **get_details.py** - Digi-Key API Integration
- Authenticates with Digi-Key OAuth2
- Implements `digikey_product_search()` function
- Handles API requests and response parsing
- Returns product details including:
  - Product name and manufacturer
  - Available quantity
  - Pricing (USD)
  - Product specifications
  - Supplier information

#### 4. **currency_converter.py** - Currency Conversion
- Provides `convert_usd_to_pkr()` function
- Converts USD prices to Pakistani Rupees
- Uses current exchange rates (configurable)
- Returns conversion details with exchange rate information

## 🔧 Configuration

### Dependencies

The project uses the following key dependencies:

```
fastapi>=0.124.0           # Web framework
google-generativeai>=0.8.5 # Gemini API client
python-dotenv>=1.2.1       # Environment variable management
requests>=2.32.5           # HTTP requests
uvicorn>=0.38.0            # ASGI server
```

See `pyproject.toml` for complete dependency list.

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |
| `CLIENT_ID` | Digi-Key API client ID | Yes |
| `CLIENT_SECRET` | Digi-Key API client secret | Yes |

## 🤖 Agent Behavior

The shopping agent follows these principles:

1. **Product Search**: Automatically uses the Digi-Key search tool for any product request
2. **Analysis**: Evaluates all results based on:
   - User's price criteria (if specified)
   - Product availability
   - Overall value and quality
3. **Single Recommendation**: Returns ONE best product, not multiple options
4. **Price Awareness**: Converts prices to PKR when requested
5. **Fallback Behavior**: If no products match criteria, recommends the cheapest available

## 🔐 Security

- API credentials are stored in `.env` file (never commit to version control)
- Add `.env` to `.gitignore`
- Use environment variables for all sensitive data
- Gemini API key is securely configured during LLM initialization

## 🐛 Troubleshooting

### Common Issues

**Issue**: Pydantic schema generation error
- **Solution**: Ensure type annotations use proper types (e.g., `str`, `dict`, `Any`) not module names

**Issue**: Token acquisition failed
- **Solution**: Verify Digi-Key CLIENT_ID and CLIENT_SECRET in `.env`

**Issue**: Gemini API errors
- **Solution**: Check GEMINI_API_KEY is valid and has proper API quota

**Issue**: No products found
- **Solution**: Try different search keywords or check Digi-Key availability

## 📈 Future Enhancements

- [ ] Add product caching to reduce API calls
- [ ] Implement user preference learning
- [ ] Support for multiple supplier integrations (Amazon, AliExpress, etc.)
- [ ] Advanced filtering and comparison features
- [ ] Price history and trend analysis
- [ ] Wishlist and comparison functionality
- [ ] Support for multiple currencies
- [ ] Rate limiting and usage analytics

## 🤝 Contributing

To contribute improvements:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📝 License

This project is provided as-is for educational and commercial use.

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review API documentation for Digi-Key and Gemini
- Check the code comments for implementation details

---

**Last Updated**: December 7, 2025  
**Version**: 0.1.0  
**Python Version**: 3.10+  
**Author**: Shopping Agent Team
