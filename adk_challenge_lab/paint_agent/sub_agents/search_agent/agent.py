import os
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools import VertexAiSearchTool, ToolContext
from google.genai import types


load_dotenv()

RETRY_OPTIONS = types.HttpRetryOptions(initial_delay=1, max_delay=3, attempts=30)

def search_paint_catalog(query: str = "") -> dict:
    """Search Cymbal Shops paint catalog for products, prices, and coverage rates."""
    catalog = {
        "EcoGreen": {
            "name": "EcoGreen",
            "description": "Environmentally friendly, low-VOC interior acrylic paint with a smooth matte finish.",
            "coverage_rate": "12 sq m/L",
            "price": "$45.00 per 2.5L container",
            "swatch_url": "https://storage.googleapis.com/paint-assets/ecogreen.png",
        },
        "SkyBlue": {
            "name": "SkyBlue",
            "description": "Bright, uplifting satin sheen interior paint ideal for living spaces and bedrooms.",
            "coverage_rate": "10 sq m/L",
            "price": "$40.00 per 2.5L container",
            "swatch_url": "https://storage.googleapis.com/paint-assets/skyblue.png",
        },
        "SunBurst": {
            "name": "SunBurst",
            "description": "Warm, sunny yellow eggshell paint designed for kitchens and dining areas.",
            "coverage_rate": "11 sq m/L",
            "price": "$42.00 per 2.5L container",
            "swatch_url": "https://storage.googleapis.com/paint-assets/sunburst.png",
        },
    }
    if query:
        q = query.lower()
        matched = {k: v for k, v in catalog.items() if k.lower() in q or q in v["description"].lower()}
        if matched:
            return matched
    return catalog


if os.getenv("GOOGLE_GENAI_USE_VERTEXAI", "").lower() == "true" and os.getenv("SEARCH_ENGINE_ID"):
    SEARCH_ENGINE_PATH = f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/locations/global/collections/default_collection/engines/{os.getenv('SEARCH_ENGINE_ID')}"
    paint_search_tool = VertexAiSearchTool(search_engine_id=SEARCH_ENGINE_PATH)
    active_tools = [paint_search_tool]
else:
    active_tools = [search_paint_catalog]

search_agent = Agent(
    name="search_agent",
    model=Gemini(model=os.getenv("MODEL", "gemini-3.6-flash"), retry_options=RETRY_OPTIONS),
    instruction="""
    If the user asked for specific paints, look up information on requested paints.
    Otherwise, provide the user information about all Cymbal Shops paints, including price
    and coverage rate.
    """,
    tools=active_tools,
)
