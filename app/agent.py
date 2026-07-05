import datetime
import os
import sys
from zoneinfo import ZoneInfo

from typing import Any
from google.adk.tools.long_running_tool import LongRunningFunctionTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types
from dotenv import load_dotenv
from google.adk import Workflow
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.genai import types
from mcp import StdioServerParameters

# Load GOOGLE_API_KEY (and any other vars) from the project .env file
load_dotenv(override=True)

# Use the standard Gemini API — no Vertex AI / GCP billing required
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

# Validate the key is present so failures surface early with a clear message
if not os.getenv("GOOGLE_API_KEY"):
    raise EnvironmentError(
        "GOOGLE_API_KEY is not set. "
        "Add it to your .env file: GOOGLE_API_KEY=your_key_here"
    )


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


Liaison_Agent = Agent(
    name="Liaison_Agent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Ceres Liaison. Communicate with farmers via SMS/Whatsapp. "
        "Keep responses under 160 characters. Extract Crop, Weight, and Region from their message. "
        "Output a JSON block: {\"intent\": \"emergency_harvest\", \"crop\": \"...\", \"weight\": ..., \"region\": \"...\"}. "
        "You MUST strip out any phone numbers or exact street addresses to protect PII."
    ),
)

mcp_server_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_server.py")

Logistics_Agent = Agent(
    name="Logistics_Agent",
    model=Gemini(
        model="gemini-3.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are the Ceres Logistics Engine. "
        "Use your MCP tools to check the weather, fetch market prices, and get vetted buyers. "
        "Apply the fair-trade-negotiation skill: calculate floor_price = market_price * 0.85. "
        "If ALL buyer bids are below floor_price, output 'No fair trade bids available.' and stop. "
        "If a buyer is selected, attempt to book_freight. "
        "CRITICAL FAILOVER: If book_freight returns an error (no trucks), you must gracefully degrade "
        "by calling find_warehouse_storage to secure the crop temporarily. "
        "Finally, call create_escrow_payment and output the full transaction summary."
    ),
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command=sys.executable,
                    args=[mcp_server_path ],
                )
            )
        )
    ],
)


def ask_farmer_approval(summary: str, tool_context: ToolContext) -> dict[str, Any]:
    """Sends the transaction summary to the farmer and tracks the unique session."""
    
    return {
        'status': 'pending_sms_reply',
        'ticketId': 'unique_ticket_id',
        'summary_sent': summary
    }
    

Security_Agent = Agent(
    name="Security_Agent",
    model=Gemini(
        model="gemini-3.5-flash", 
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a Security Guardrail. Review the transaction summary provided. "
        "Rule 1: Ensure absolutely no PII (phone numbers or exact coordinates) is exposed to the buyer. "
        "Rule 2: Verify the final crop price is greater than 0. "
        "If valid, rewrite the summary into a friendly, professional SMS and CALL the `ask_farmer_approval` tool. "
        "When the tool returns a 'pending' status, inform the system that we are waiting for the farmer's confirmation. "
        "If invalid, output ERROR: Security Violation."
    ),
    tools=[LongRunningFunctionTool(func=ask_farmer_approval)]
)

root_agent = Workflow(
    name="root_agent",
    edges=[
        ("START", Liaison_Agent),
        (Liaison_Agent, Logistics_Agent),
        (Logistics_Agent, Security_Agent)
        # We stop the edges here. Security_Agent is the end of the line.
    ],
)


app = App(
    root_agent=root_agent,
    name="app",
)
