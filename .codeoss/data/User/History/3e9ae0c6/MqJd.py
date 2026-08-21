import os
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from .tools import paint_coverage_calculator
from .....callback_logging import log_query_to_model, log_model_response


load_dotenv()

RETRY_OPTIONS = types.HttpRetryOptions(initial_delay=1, max_delay=3, attempts=30)

# 


# coverage_calculator_agent = Agent(
#     model=Gemini(model=os.getenv("MODEL")),
#     name="coverage_calculator",
#     instruction="""
#         You are a coverage calculator agent.
#         Your job is to calculate the amount of paint needed.
        
#         The user has selected the paint: {SELECTED_PAINT?}.
#         The coverage rate for this paint is: {COVERAGE_RATE?}.
        
#         Use these values to calculate the total gallons needed based on the room dimensions.
#     """,
#     tools=[calculate_volume],
# )
