import httpx
from langchain_core.tools import tool
from langchain_community.utilities.tavily_search import TavilySearchAPIWrapper
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

load_dotenv()

@tool
def http_request_tool(method: str, url: str, headers: dict = None, body: dict = None) -> str:
    """
    Executes an HTTP request.
    
    Args:
        method: The HTTP method (GET, POST, PUT, DELETE, etc.).
        url: The URL to send the request to.
        headers: Optional dictionary of headers.
        body: Optional dictionary for the JSON body.
        
    Returns:
        The response text or error message.
    """
    try:
        # Auto-inject LENA API Key if applicable
        lena_url = os.getenv("LENA_API_URL")
        lena_key = os.getenv("LENA_API_KEY")
        
        if lena_url and url.startswith(lena_url) and lena_key:
            # Append key parameter
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}key={lena_key}"
            
        response = httpx.request(method, url, headers=headers, json=body, timeout=10.0)
        return f"Status Code: {response.status_code}\nResponse: {response.text}"
    except Exception as e:
        return f"Error executing request: {str(e)}"

# Initialize Tavily Search Tool with domain restrictions
tavily_wrapper = TavilySearchAPIWrapper()
tavily_search_tool = TavilySearchResults(
    api_wrapper=tavily_wrapper,
    include_domains=["docs.lenalab.org", "solution.lgcns.com"]
)
