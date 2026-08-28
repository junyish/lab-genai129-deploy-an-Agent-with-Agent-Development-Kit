# Comprehensive Step-by-Step Instruction Guide: Deploy an Agent with Agent Development Kit (ADK) on Vertex AI

> **Lab Reference:** `GENAI129` | **Challenge Lab Track:** Deploy an Agent with Agent Development Kit (ADK)  
> **Business Scenario:** Cymbal Shops Paint Department AI Assistant  
> **Repository:** [`lab-genai129-deploy-an-Agent-with-Agent-Development-Kit`](https://github.com/junyish/lab-genai129-deploy-an-Agent-with-Agent-Development-Kit)  
> **Target Framework:** Google ADK (`google-adk`), Vertex AI Search / Discovery Engine, Vertex AI Reasoning Engine / Agent Runtime, Chainlit Streaming UI.

---

## 🎯 Architectural Overview & Multi-Agent Topology

```mermaid
flowchart TD
    User["Customer (Chainlit UI / Vertex AI SDK)"] <--> PaintAgent["<b>1. paint_agent (Root Coordinator)</b><br/>Orchestrates dialogue & state flow"]

    subgraph ToolCalling ["Agent-as-a-Tool Pattern (Synchronous Data Lookup)"]
        PaintAgent -- "1. Tool Call: Query Catalog" --> SearchAgentTool["<b>AgentTool(search_agent)</b><br/>skip_summarization=False"]
        SearchAgentTool --> SearchAgent["<b>search_agent</b>"]
        SearchAgent --> VertexSearch["<b>VertexAiSearchTool</b><br/>Vertex AI Search Datastore"]
        VertexSearch -- "Specs & Pricing" --> SearchAgent
        SearchAgent -- "12 sq m/L, $45.00/can" --> SearchAgentTool
        SearchAgentTool -- "Synthesized Info" --> PaintAgent
    end

    subgraph StateMemory ["Shared Session Memory (ToolContext.state)"]
        PaintAgent -- "2. set_session_value" --> StateStore[("State Store:<br/>SELECTED_PAINT='EcoGreen'<br/>COVERAGE_RATE='12 sq m/L'<br/>PRICE='$45.00'")]
    end

    subgraph ConversationalHandoff ["Conversational Sub-Agents (Handoff Flow)"]
        PaintAgent -- "3. Handoff Control" --> RoomPlanner["<b>2. room_planner_agent</b><br/>Intake room count & swatch display"]
        RoomPlanner -- "4. Handoff Control" --> CoverageCalc["<b>3. coverage_calculator_agent</b><br/>Computes wall area & paint cans"]
        CoverageCalc -- "Geometric Tool" --> CalcTool["<b>paint_coverage_calculator</b><br/>(Deterministic Python Tool)"]
        StateStore -. "Read Context {SELECTED_PAINT?}" .-> RoomPlanner
        StateStore -. "Read Context {COVERAGE_RATE?}" .-> CoverageCalc
    end
```

---

## ⚡ The Core Dilemma: `search_agent` as Sub-Agent vs. Tool

One of the most frequent points of failure in **GENAI129** is misunderstanding the architectural difference between **Conversational Delegation (`sub_agents`)** and **Functional Tool Execution (`AgentTool`)**.

### ❌ The Flawed Anti-Pattern: Putting `search_agent` in `sub_agents`

```python
# ❌ INCORRECT / BROKEN PATTERN
root_agent = Agent(
    name="paint_agent",
    sub_agents=[search_agent, room_planner_agent],  # <-- ERROR!
    tools=[set_session_value],
)
```

#### Why This Breaks:
1. **Conversational Takeover:** In Google ADK, any agent listed in `sub_agents` is treated as a **conversation handoff target**. When the user asks, *"What paints do you offer?"*, `paint_agent` delegates control completely to `search_agent`.
2. **Loss of Control & State Blindness:** `search_agent` only has `VertexAiSearchTool`. It does **NOT** have `set_session_value` or a reference to `room_planner_agent`.
3. **Dead End in State Machine:** Once `search_agent` finishes answering the user's question, it cannot transition the user to the room planner or store the chosen paint. The conversational pipeline becomes stuck.

---

### ✅ The Solution: Wrapping `search_agent` as an `AgentTool`

```python
# ✅ CORRECT PRODUCTION PATTERN
from google.adk.tools import AgentTool
from .sub_agents.search_agent.agent import search_agent
from .sub_agents.room_planner.agent import room_planner_agent
from .tools import set_session_value

root_agent = Agent(
    name="paint_agent",
    model=Gemini(model=os.getenv("MODEL"), retry_options=RETRY_OPTIONS),
    instruction="""
    You represent the paint department of Cymbal Shops.

    Information about Cymbal Shops paint, including prices, is available to you
    through the 'search_agent' tool.

    - At the start of a conversation, let the user know you're here to
      help them find the right paint for their project. Ask them if they'd
      like to learn more about the different paint products offered by
      Cymbal Shops.
    - If they say yes, include information about all paint products including
      coverage rate and price.
    - If price and coverage rate aren't returned for some products, look them
      up individually.
    - After they have selected a paint product, use your set_session_value tool
      to store their selection in the session dictionary with the key
      'SELECTED_PAINT', its coverage rate in 'COVERAGE_RATE', and its price
      per 2.5L container in 'PRICE'.
    - Transfer to the 'room_planner_agent'
    """,
    sub_agents=[room_planner_agent],  # Only room_planner is a conversational sub-agent
    tools=[
        AgentTool(agent=search_agent, skip_summarization=False),  # search_agent is a TOOL
        set_session_value,
    ],
)
```

### 📊 Comparative Matrix: `sub_agents` vs. `AgentTool`

| Dimension | `sub_agents=[agent]` (Handoff) | `AgentTool(agent=agent)` (Tool Call) |
| :--- | :--- | :--- |
| **Execution Model** | **Asynchronous Handoff:** Control is transferred to child agent. | **Synchronous Query:** Parent calls child in the background and gets return text. |
| **User Interaction** | User directly talks with the child agent persona. | User continues talking to parent agent; parent summarizes child's output. |
| **State Retention** | Child must manage its own transitions or bubble back up. | Parent maintains uninterrupted session state and workflow ownership. |
| **Role in Lab** | Used for `room_planner_agent` & `coverage_calculator_agent`. | Used exclusively for `search_agent` (paint product catalog retrieval). |

---

## 📋 Task-by-Task Step-by-Step Lab Walkthrough

---

### 📋 Task 1: Environment Setup & Cloud Configuration

1. Open Google Cloud Shell and configure your environment variables:

```bash
# Export active project and region
export GOOGLE_CLOUD_PROJECT=$(gcloud config get-value project 2>/dev/null)
export GOOGLE_CLOUD_LOCATION="us-central1"
export MODEL="gemini-2.5-flash"
export GOOGLE_GENAI_USE_VERTEXAI="true"

# Verify variables
echo "Project:  ${GOOGLE_CLOUD_PROJECT}"
echo "Location: ${GOOGLE_CLOUD_LOCATION}"
echo "Model:    ${MODEL}"
```

2. Enable the required Google Cloud service APIs:

```bash
gcloud services enable \
    aiplatform.googleapis.com \
    discoveryengine.googleapis.com \
    storage.googleapis.com \
    logging.googleapis.com \
    --project "${GOOGLE_CLOUD_PROJECT}"
```

3. Initialize the Python environment:

```bash
# Clone the repository
git clone https://github.com/junyish/lab-genai129-deploy-an-Agent-with-Agent-Development-Kit.git
cd lab-genai129-deploy-an-Agent-with-Agent-Development-Kit/adk_challenge_lab

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

---

### 📋 Task 2: Retrieve Vertex AI Search Engine ID

The lab provisions a **Vertex AI Search Engine** containing Cymbal Shops paint specifications.

1. Fetch your search engine ID:

```bash
# List search engines to locate your engine ID
gcloud alpha discovery-engine engines list \
    --location="global" \
    --collection="default_collection" \
    --project="${GOOGLE_CLOUD_PROJECT}"
```

*(Alternatively, navigate to **Vertex AI Search and Conversation** in the Google Cloud Console, select **Data Stores / Search Engines**, and copy the Engine ID).*

2. Create your `.env` file:

```bash
cat << EOF > .env
GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}
GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION}
MODEL=${MODEL}
SEARCH_ENGINE_ID=your_search_engine_id_here
GOOGLE_GENAI_USE_VERTEXAI=true
EOF
```

---

### 📋 Task 3: Implement `search_agent` with `VertexAiSearchTool`

Open `adk_challenge_lab/paint_agent/sub_agents/search_agent/agent.py` and configure the search agent:

```python
# adk_challenge_lab/paint_agent/sub_agents/search_agent/agent.py
import os
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools import VertexAiSearchTool
from google.genai import types

load_dotenv()

RETRY_OPTIONS = types.HttpRetryOptions(initial_delay=1, max_delay=3, attempts=30)

SEARCH_ENGINE_PATH = (
    f"projects/{os.getenv('GOOGLE_CLOUD_PROJECT')}/"
    f"locations/global/collections/default_collection/"
    f"engines/{os.getenv('SEARCH_ENGINE_ID')}"
)

paint_search_tool = VertexAiSearchTool(search_engine_id=SEARCH_ENGINE_PATH)

search_agent = Agent(
    name="search_agent",
    model=Gemini(model=os.getenv("MODEL"), retry_options=RETRY_OPTIONS),
    instruction="""
    If the user asked for specific paints, look up information on requested paints.
    Otherwise, provide the user information about all Cymbal Shops paints, including price
    and coverage rate.
    """,
    tools=[paint_search_tool],
)
```

---

### 📋 Task 4: Implement Session State Tool (`tools.py`)

Open `adk_challenge_lab/paint_agent/tools.py` and implement the session state writer:

```python
# adk_challenge_lab/paint_agent/tools.py
from google.adk.tools import ToolContext

def set_session_value(key: str, value: str, tool_context: ToolContext) -> str:
    """Stores a key-value pair in the shared session state dictionary.

    Args:
        key: The state variable name (e.g. 'SELECTED_PAINT', 'COVERAGE_RATE', 'PRICE').
        value: The string value to assign.
        tool_context: The ADK runtime tool context.

    Returns:
        Confirmation message indicating the key has been updated.
    """
    tool_context.state[key] = value
    return f"Successfully saved session state: {key} = {value}"
```

---

### 📋 Task 5: Implement `room_planner_agent` & `coverage_calculator_agent`

1. **Room Planner Agent (`paint_agent/sub_agents/room_planner/agent.py`):**
   - Ingests number of rooms.
   - Dynamically resolves `{SELECTED_PAINT?}` from session state and renders paint swatch URLs.
   - Delegates to `coverage_calculator_agent`.

```python
# adk_challenge_lab/paint_agent/sub_agents/room_planner/agent.py
import os
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.genai import types
from .sub_agents.coverage_calculator.agent import coverage_calculator_agent

RETRY_OPTIONS = types.HttpRetryOptions(initial_delay=1, max_delay=3, attempts=30)

room_planner_agent = Agent(
    name="room_planner_agent",
    model=Gemini(model=os.getenv("MODEL"), retry_options=RETRY_OPTIONS),
    instruction="""
    You help customers plan the rooms they wish to paint.
    - Ask the user how many rooms they would like to paint.
    - Based on the {SELECTED_PAINT?}, display the corresponding color swatch image:
      - EcoGreen: https://storage.googleapis.com/paint-assets/ecogreen.png
      - SkyBlue: https://storage.googleapis.com/paint-assets/skyblue.png
      - SunBurst: https://storage.googleapis.com/paint-assets/sunburst.png
    - Once the room details are gathered, transfer to 'coverage_calculator_agent'.
    """,
    sub_agents=[coverage_calculator_agent],
)
```

2. **Coverage Calculator Tool & Agent:**
   - Implement deterministic geometric formula in `coverage_calculator/tools.py`:

```python
# adk_challenge_lab/paint_agent/sub_agents/room_planner/sub_agents/coverage_calculator/tools.py
import math

async def paint_coverage_calculator(
    length_m: float,
    width_m: float,
    height_m: float,
    doors: int = 0,
    windows: int = 0
) -> dict:
    """Calculates paint required for room walls excluding standard doors/windows."""
    DOOR_AREA = 1.95  # sq meters
    WINDOW_AREA = 1.50 # sq meters
    
    total_wall_area = 2 * (length_m + width_m) * height_m
    deductions = (doors * DOOR_AREA) + (windows * WINDOW_AREA)
    net_wall_area = max(0.0, total_wall_area - deductions)
    
    return {
        "net_wall_area_sq_m": round(net_wall_area, 2),
        "two_coats_area_sq_m": round(net_wall_area * 2, 2)
    }
```

---

### 📋 Task 6: Local Multi-Turn Testing

Test the agent locally to verify tool execution and session state flow:

```bash
python test_adk.py
```

**Verification Checkpoints:**
- `search_agent` returns all 3 paint varieties with price and coverage.
- Setting `SELECTED_PAINT="EcoGreen"` writes to `tool_context.state`.
- Transfer to `room_planner_agent` executes without exceptions.

---

### 📋 Task 7: Deploy Agent to Vertex AI Reasoning Engine

Deploy the complete multi-agent system to Vertex AI:

```python
# deploy.py
import vertexai
from vertexai.preview import reasoning_engines
from paint_agent.agent import root_agent
import os

vertexai.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    staging_bucket=f"gs://{os.getenv('GOOGLE_CLOUD_PROJECT')}-bucket"
)

remote_agent = reasoning_engines.ReasoningEngine.create(
    root_agent,
    requirements=[
        "google-adk>=2.7.0",
        "google-genai>=1.0.0",
        "google-cloud-logging>=3.11.0",
        "pydantic>=2.0.0"
    ],
    display_name="cymbal-paint-assistant"
)

print(f"Agent successfully deployed! Resource Name: {remote_agent.resource_name}")
```

Run the deployment script:
```bash
python deploy.py
```

---

### 📋 Task 8: Launch Chainlit Streaming UI

Update the deployed resource name in `chainlit_ui/app.py`:

```python
# chainlit_ui/app.py
agent = client.agent_engines.get(name="projects/YOUR_PROJECT_NUMBER/locations/us-central1/reasoningEngines/YOUR_ENGINE_ID")
```

Launch the interactive UI:

```bash
cd chainlit_ui
chainlit run app.py -w --port 8080
```

---

## 🏆 Summary Checklist for Passing Lab 129

| Item | Requirement | Verified? |
| :---: | :--- | :---: |
| 1 | `search_agent` is wrapped in `AgentTool(search_agent)` inside `paint_agent.tools` | ✅ |
| 2 | `room_planner_agent` is the ONLY child in `paint_agent.sub_agents` | ✅ |
| 3 | `SELECTED_PAINT`, `COVERAGE_RATE`, and `PRICE` are written via `set_session_value` | ✅ |
| 4 | Color swatch URLs are rendered in Markdown/HTML by `room_planner_agent` | ✅ |
| 5 | Wall coverage and required 2.5L cans are calculated deterministically by `paint_coverage_calculator` | ✅ |
| 6 | Agent is packaged and deployed to Vertex AI Reasoning Engine / Agent Engine | ✅ |
