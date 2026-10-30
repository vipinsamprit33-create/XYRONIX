
import os

import requests
from dotenv import load_dotenv


load_dotenv()


def search_web(query, max_results=5):
    """
    Search the web using the Tavily API.

    Requires TAVILY_API_KEY in .env.
    Returns structured results or an error message.
    """

    if not isinstance(query, str) or not query.strip():
        return {
            "status": "error",
            "message": "Search query cannot be empty."
        }

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return {
            "status": "unavailable",
            "message": (
                "Web search is not configured. "
                "Add TAVILY_API_KEY to your .env file."
            ),
            "results": []
        }

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "max_results": max(
                    1, min(int(max_results), 10)
                )
            },
            timeout=20
        )

        response.raise_for_status()
        data = response.json()

        results = []

        for item in data.get("results", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("url", ""),
                "content": item.get("content", "")
            })

        return {
            "status": "completed",
            "query": query,
            "results": results
        }

    except requests.RequestException as exc:
        return {
            "status": "error",
            "message": (
                "Search request failed: "
                + type(exc).__name__
            ),
            "results": []
        }
