# Route Optimizer UI

An intelligent agentic application that optimizes travel routes using conversational AI, email integration, and multi-agent workflows.

## Overview

**Route Optimizer UI** is a conversational AI application built with LangChain and LangGraph that intelligently optimizes routes between locations. It features multiple specialized agents that work together to:
- Extract route details from emails
- Optimize routes via Google Maps APIs
- Handle complex multi-step workflows with state management
- Provide conversational route optimization assistance

This is a **multi-agent AI automation system** that combines:
- **Agentic Workflows**: Autonomous agents that decide when and how to use tools
- **AI Chatbot Interface**: Conversational UI via Chainlit
- **Workflow Orchestration**: LangGraph-based state management for complex flows

## Key Features

### 1. **Conversational Route Optimization**
- Chat interface for route planning queries
- Natural language understanding of source, destination, and waypoints
- Real-time route optimization suggestions

### 2. **Email Integration**
- Extract route details from emails automatically
- Parse structured route information from unstructured email content
- Support for multi-turn conversations with email context

### 3. **Multi-Agent Architecture**
Three specialized agents work together:
- **Route Agent**: Optimizes routes using Google Maps API
- **Gmail Agent**: Extracts and parses route details from emails
- **Agentic Workflow Agent**: Orchestrates route and Gmail agents as tools

### 4. **LangGraph Orchestration**
- State-based workflow management
- Conditional routing (e.g., ask for missing info vs. optimize route)
- Multi-step execution with error handling
- Structured data validation and merging

### 5. **Intelligent Tool Usage**
- Agents autonomously decide when to invoke tools
- Caching mechanisms to avoid redundant API calls
- Error handling with graceful fallbacks

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Chainlit Chat Interface                     │
└────────────────┬────────────────────────────────────────┘
                 │
     ┌───────────┴──────────────┐
     │                          │
┌────v────────────────┐   ┌────v──────────────────────────┐
│  Route Agent        │   │  Agentic Workflow Agent       │
│  - Route Optim.     │   │  - Orchestrates tools         │
│  - Google Maps API  │   │  - System prompts             │
└────┬────────────────┘   │                               │
     │                    └────┬──────────────────────────┘
     │                         │
     ├─────────────────────────┤
     │                         │
┌────v────────────┐   ┌───────v───────────────────────────┐
│  Gmail Agent    │   │  LangGraph Orchestrator           │
│  - Email parse  │   │  - State management               │
│  - Text extract │   │  - Conditional edges              │
└────────────────┘   │  - Multi-step workflows            │
                     └───────────────────────────────────┘
```

## File Structure

```
route-optimizer-ui/
├── README.md                          # This file
├── pyproject.toml                     # Project dependencies
├── .env                               # Environment variables (create this)
├── main.py                            # Legacy entry point
├── chainlit.md                        # Chainlit welcome message
│
└── src/
    ├── app.py                         # Chainlit chat app (main UI)
    ├── constants.py                   # System prompts
    │
    ├── agents/
    │   ├── route_agent.py            # Route optimization agent
    │   ├── gmail_agent.py            # Email parsing agent
    │   ├── agentic_wrkflw.py         # Multi-agent orchestrator
    │   └── lg_orchestrator.py        # LangGraph workflow engine
    │
    └── clients/
        ├── gmap_api_client.py        # Google Maps API wrapper
        └── gmail_client.py           # Gmail API wrapper
```

## Installation

### Prerequisites
- **Python 3.11+** (3.13+ recommended)
- **API Keys**:
  - Anthropic API key (Claude)
  - Google Maps API key
  - Gmail API credentials (optional, for email integration)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd route-optimizer-ui
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
# OR
pip install -e .
```

Dependencies include:
- `chainlit>=2.10.0` - Chat UI framework
- `langchain>=1.2.12` - Agent framework
- `langchain-anthropic>=1.3.5` - Claude API integration
- `langgraph>=0.0.x` - Workflow orchestration
- `httpx>=0.28.1` - Async HTTP client
- `dotenv>=0.9.9` - Environment variable management

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:

```env
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Google Maps API
GOOGLE_API_KEY=AIza...

# Gmail API (optional)
GMAIL_USER_EMAIL=your-email@gmail.com
GMAIL_CREDENTIALS_JSON=path/to/credentials.json

# Route Optimization API
ROUTE_OPTIMIZE_API_URL=https://route-optimize-api-...

# Optional
LOG_LEVEL=INFO
```

### Step 5: Run the Application
```bash
# Chainlit chat interface
chainlit run src/app.py

# Or with Python
python -m chainlit run src/app.py
```

The app will be available at `http://localhost:8000`

## Usage

### Basic Chat Interface
1. Open the app in your browser
2. Type your route optimization request:
   - "Find the best route from Milton to Toronto with stops at Mississauga and Pearson Airport"
   - "Optimize my route with these waypoints: [addresses]"

### Email-Based Workflow
1. Send an email with route details to your Gmail account
2. Ask the app: "Extract my route from emails"
3. The Gmail agent will parse the email and extract structured data
4. The route agent will optimize the extracted route

### Multi-Agent Workflow
The agentic workflow automatically:
1. Checks if route data is available (from email or user input)
2. Validates required fields (source, destination)
3. Asks for missing information if needed
4. Optimizes the route using Google Maps API
5. Returns formatted itinerary to the user

## API Integration

### Google Maps Route Optimization
- **Endpoint**: `https://route-optimize-api-670264226001.us-central1.run.app/optimize-route`
- **Request Format**:
```json
{
  "source": "34 Finney Terrace, Milton, ON, Canada",
  "destination": "55 Mill St, Toronto, ON M5A 3C4",
  "waypoints": ["6301 Silver Dart Dr", "Toronto Pearson International Airport"],
  "departure_time": "2026-03-18T14:30:00Z"
}
```

### Claude Integration
- **Model**: Claude Sonnet 4.6 (latest)
- **Framework**: LangChain agents with tool-use
- **Temperature**: Default (0.7 recommended)

## Design Patterns

### 1. Agent Caching
Agents are instantiated once and reused:
```python
_agent = None
_agent_lock = asyncio.Lock()

async def get_agent():
    global _agent
    if _agent is not None:
        return _agent
    # Initialize only once
```

### 2. Tool Decoration
Tools are defined as decorated async functions:
```python
@tool("tool_name", description="What it does")
async def my_tool(param: str) -> dict:
    return result
```

### 3. State-Based Workflows
LangGraph manages complex multi-step flows:
```python
workflow.add_node("step1", handler_func)
workflow.add_conditional_edges("step1", router_func, {"branch1": "step2"})
```

### 4. System Prompts
Agent behavior is controlled via detailed system prompts in `constants.py`:
- `Google_Maps_System_Prompt`: Route optimization behavior
- `Agentic_Workflow_System_Prompt`: Multi-agent orchestration
- `Gmail_System_Prompt`: Email parsing instructions

## Configuration

### System Prompts
Modify behavior by editing prompts in `src/constants.py`:
- Controls how agents interpret requests
- Defines tool usage rules
- Sets response formatting

### Model Selection
Change the LLM in agent files:
```python
model = ChatAnthropic(
    model="claude-opus-4-6",  # Change model here
    api_key=ANTHROPIC_API_KEY
)
```

### API Endpoints
Update endpoints in `src/clients/`:
- `gmap_api_client.py`: Google Maps API URL
- `gmail_client.py`: Gmail API configuration

## Development

### Running Tests
```bash
pytest tests/
```

### Debugging
Enable logging in `.env`:
```env
LOG_LEVEL=DEBUG
```

View agent execution flow:
- Check Chainlit UI console
- Monitor print statements in agent files
- Review LangChain debugging logs

### Adding New Agents
1. Create new agent file in `src/agents/`
2. Implement agent initialization and invoke function
3. Add system prompt to `constants.py`
4. Register in orchestrator if part of workflow

### Adding New Tools
1. Define tool function with `@tool` decorator
2. Add to agent tools list
3. Update system prompt with tool description

## Known Issues & Limitations

- Agent creation may be inefficient (creates new agent per invocation in some paths)
- No response caching between identical requests
- Limited error handling in API clients
- No timeout configuration for HTTP requests
- System prompts could be externalized for easier management

## Performance Considerations

1. **Agent Caching**: Agents are cached to avoid repeated initialization
2. **API Calls**: Route optimization API calls are made once per request
3. **Email Parsing**: Gmail agent runs sequentially (not parallelized)
4. **Response Time**: Typically 2-5 seconds depending on API latency

## Security

- **API Keys**: Store in `.env` file (never commit)
- **Email Access**: Uses OAuth2 for Gmail integration
- **Data Privacy**: Route information stored only in memory during session
- **Input Validation**: All user inputs should be validated before tool use

## Troubleshooting

### "Could not generate response"
- Check ANTHROPIC_API_KEY is set correctly
- Verify network connectivity to Anthropic APIs
- Check agent logs for detailed errors

### "Gmail Agent failed"
- Verify Gmail API credentials are valid
- Check email contains route information
- Ensure OAuth2 scopes include email reading

### Route optimization times out
- Check ROUTE_OPTIMIZE_API_URL is correct
- Verify source/destination addresses are valid
- Check Google Maps API quota usage

## Contributing

1. Create a feature branch
2. Make changes following the existing patterns
3. Test with the Chainlit UI
4. Submit a pull request with description

## License

[Add your license information here]

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review agent logs and error messages
3. Verify API keys and environment configuration
4. Open an issue on GitHub

---

**Last Updated**: March 18, 2026
**Version**: 0.1.0
