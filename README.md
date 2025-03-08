# AskWiseAI: AI-Powered Q&A System with Tool Integration

## Table of Contents
1. [Introduction](#introduction)
2. [Thought Process & Design Philosophy](#thought-process--design-philosophy)
3. [System Architecture](#system-architecture)
4. [Core Components](#core-components)
5. [Key Features](#key-features)
6. [Installation & Setup](#installation--setup)
7. [Usage Guide](#usage-guide)
8. [API Reference](#api-reference)
9. [Example Interactions](#example-interactions)
10. [Enterprise Scaling Considerations](#enterprise-scaling-considerations)
11. [Security & Access Control](#security--access-control)
12. [Evaluation & Accuracy](#evaluation--accuracy)
13. [Future Enhancements](#future-enhancements)
14. [Contributing](#contributing)
15. [License](#license)

## Introduction

AskWiseAI is an intelligent question-answering system that combines the reasoning capabilities of Large Language Models (LLMs) with the real-time accuracy of external API tools. This hybrid approach allows the system to provide both general knowledge answers and up-to-date, domain-specific information.

The system intelligently routes user queries to either:
- A pre-trained LLM (like GPT-4) for general knowledge questions
- Specialized external APIs for real-time data (weather, stock prices, etc.)

This approach addresses one of the fundamental limitations of LLMs: their inability to access real-time information beyond their training data cutoff. By integrating external tools, AskWiseAI delivers more accurate, timely, and useful responses.

## Thought Process & Design Philosophy

### The Problem Space

When designing AskWiseAI, I identified several key challenges in building an effective AI assistant:

1. **Knowledge Limitations**: LLMs have fixed knowledge cutoffs and cannot access real-time information.
2. **Hallucination Risk**: LLMs sometimes generate plausible-sounding but incorrect information, especially for questions requiring current data.
3. **Tool Selection**: Determining when to use the LLM versus an external API is non-trivial.
4. **Response Integration**: Combining API data with natural language responses requires careful prompt engineering.
5. **Scalability**: A prototype must be designed with future enterprise scaling in mind.

### My Approach

To address these challenges, I developed a multi-layered architecture with these guiding principles:

#### 1. Intelligent Query Routing

Rather than using simple keyword matching, I leveraged the LLM itself to make the routing decision. This approach has several advantages:

- **Semantic Understanding**: The LLM can understand the intent behind a query, not just keywords.
- **Reasoning Capability**: The LLM can determine if a question requires real-time data or if it can be answered from its knowledge.
- **Adaptability**: As new tools are added, the system can learn to route to them without hard-coded rules.

I implemented this by creating a specialized prompt that instructs the LLM to analyze the query and decide whether to use its knowledge or call an external tool.

#### 2. Tool Integration Framework

I designed a modular tool integration framework with these considerations:

- **Abstraction**: Each tool implements a common interface, making it easy to add new tools.
- **Separation of Concerns**: Tool logic is isolated from routing logic.
- **Error Handling**: Each tool includes robust error handling and input validation.
- **Caching**: Responses are cached to improve performance and reduce API calls.

#### 3. Conversation Memory

To create a more natural interaction experience, I implemented a conversation memory system that:

- Maintains context across multiple turns
- Allows for follow-up questions
- Preserves tool usage history for reference

#### 4. Enterprise Readiness

From the beginning, I designed with enterprise scaling in mind:

- **Caching**: Implemented at multiple levels to reduce latency and API costs
- **Async Processing**: Used async/await patterns for non-blocking operations
- **Error Resilience**: Graceful fallbacks when tools fail
- **Observability**: Comprehensive logging for debugging and monitoring
- **Security**: Input sanitization and API key management

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │
│  User Interface │────▶│  FastAPI Server │────▶│  Query Router   │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │                 │     │                 │
                        │  LLM Service    │◀───▶│  Tool Decision  │
                        │                 │     │                 │
                        └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │                 │     │                 │
                        │  Tool Registry  │────▶│  Tool Execution │
                        │                 │     │                 │
                        └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                        ┌─────────────────┐     ┌─────────────────┐
                        │                 │     │                 │
                        │  Response       │◀────│  External APIs  │
                        │  Generation     │     │                 │
                        │                 │     │                 │
                        └─────────────────┘     └─────────────────┘
```

### Query Processing Flow

1. **User Query Submission**: The user submits a question through the API endpoint.
2. **Conversation Context**: If part of an ongoing conversation, previous context is retrieved.
3. **Query Routing Decision**: The LLM analyzes the query to determine if it needs a tool or can be answered directly.
4. **Tool Selection & Execution**: If a tool is needed, the appropriate tool is selected and executed.
5. **Response Generation**: The LLM generates a natural language response, incorporating tool data if applicable.
6. **Conversation Memory Update**: The interaction is saved to conversation history.
7. **Response Delivery**: The final answer is returned to the user.

### Tool Decision Process

```
┌─────────────────┐
│                 │
│  User Query     │
│                 │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Analyze Query  │
│  with LLM       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Does query need │    No     ┌─────────────────┐
│ real-time data? │──────────▶│ Answer with LLM │
└────────┬────────┘           └─────────────────┘
         │ Yes
         ▼
┌─────────────────┐
│ Select the most │
│ appropriate tool│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Extract required│
│ parameters      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Execute tool    │
│ with parameters │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Format response │
│ with tool data  │
└─────────────────┘
```

## Core Components

### 1. FastAPI Web Server (`app/main.py`)

The entry point for the application, providing:
- RESTful API endpoints for query processing
- Conversation management
- Health checks and monitoring

### 2. Query Router (`app/router.py`)

The brain of the system that:
- Analyzes queries using the LLM
- Decides whether to use the LLM or an external tool
- Orchestrates tool execution and response generation

### 3. LLM Service (`app/llm_service.py`)

Handles all interactions with the language model:
- Sends prompts to the LLM API
- Processes responses
- Implements caching for efficiency

### 4. Tool Framework

#### Base Tool Interface (`app/tools/base.py`)

Defines the contract that all tools must implement:
- Name and description
- Parameter specifications
- Execution logic

#### Tool Registry (`app/tools/__init__.py`)

Maintains a registry of available tools and provides:
- Tool lookup by name
- Tool listing with descriptions
- Tool parameter information

#### Implemented Tools

- **Weather Tool** (`app/tools/weather.py`): Fetches current weather conditions
- **Stock Price Tool** (`app/tools/stocks.py`): Retrieves current stock market data

### 5. Caching System (`app/cache.py`)

Implements a multi-level caching strategy:
- LLM response caching to reduce API costs
- Tool response caching to minimize external API calls
- Time-based expiration for different data types

### 6. Conversation Memory (`app/memory.py`)

Maintains conversation context:
- Stores conversation history
- Provides context for follow-up questions
- Implements automatic cleanup of old conversations

## Key Features

### 1. Intelligent Query Routing

AskWiseAI doesn't use simple keyword matching to decide when to use tools. Instead, it leverages the LLM's understanding of the query to make this decision. The system prompts the LLM with detailed instructions about when to use tools versus answering directly.

```python
# Enhanced routing prompt with better tool descriptions
ROUTING_PROMPT = """
You are an AI assistant that can answer questions directly or use specialized tools when necessary.
Your goal is to provide the most accurate and helpful response to the user.

WHEN TO USE TOOLS:
- Use tools ONLY for real-time or specialized information that you cannot know with certainty
- For general knowledge, opinions, or explanations, answer directly without using tools
- Never make up or guess information that should come from a tool

AVAILABLE TOOLS:
{tool_descriptions}

INSTRUCTIONS:
1. Carefully analyze the user query
2. Determine if you need real-time or specialized information to answer accurately
3. If yes, select the most appropriate tool and specify the exact parameters needed
4. If no, indicate you'll answer directly

Respond with JSON in this format:
{{
  "use_tool": true/false,
  "reasoning": "Brief explanation of your decision",
  "tool_name": "tool_name" (if use_tool is true),
  "tool_input": {{key-value parameters for the tool}} (if use_tool is true)
}}

USER QUERY: {query}
"""
```

### 2. Modular Tool Integration

Tools are implemented as classes that inherit from a common base class, making it easy to add new tools:

```python
class Tool(ABC):
    """Base class for all tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the tool."""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what the tool does."""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Dict[str, Any]]:
        """Return the parameters the tool accepts."""
        pass
    
    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        pass
```

### 3. Multi-Level Caching

The system implements caching at multiple levels to improve performance and reduce costs:

```python
class SimpleCache:
    """A simple in-memory cache with time-based expiration."""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize the cache.
        
        Args:
            default_ttl: Default time-to-live in seconds (5 minutes)
        """
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl
    
    # ... methods for get, set, clear, etc.

# Create cache instances with different TTLs for different data types
llm_cache = SimpleCache(default_ttl=3600)  # 1 hour for LLM responses
tool_cache = SimpleCache(default_ttl=300)  # 5 minutes for tool responses
```

### 4. Conversation Context Management

The system maintains conversation history to provide context for follow-up questions:

```python
class ConversationMemory:
    """Simple in-memory storage for conversation history."""
    
    def __init__(self, max_history: int = 10, ttl: int = 3600):
        """
        Initialize conversation memory.
        
        Args:
            max_history: Maximum number of turns to remember
            ttl: Time-to-live in seconds for conversations (default: 1 hour)
        """
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.max_history = max_history
        self.ttl = ttl
    
    # ... methods for creating conversations, adding messages, etc.
```

### 5. Robust Error Handling

The system implements comprehensive error handling at multiple levels:

```python
try:
    # Execute the tool
    tool_output = await tool.execute(**tool_input)
    
    # Generate a response with the tool output
    response = await get_llm_response(context_prompt)
    
    return {
        "response": response,
        "tool_used": tool_name,
        "tool_input": tool_input,
        "tool_output": tool_output,
        "reasoning": reasoning
    }
except Exception as e:
    # Handle tool execution errors
    error_message = f"Error executing {tool_name} tool: {str(e)}"
    print(error_message)
    
    # Fallback to LLM with error context
    fallback_prompt = f"""
    The user asked: "{query}"
    
    I tried to use the {tool_name} tool, but encountered an error: {str(e)}
    
    Please provide a helpful response that explains the issue and offers an alternative
    answer based on your knowledge, clearly indicating the limitations.
    """
    
    response = await get_llm_response(fallback_prompt)
    
    return {
        "response": response,
        "error": error_message
    }
```

### 6. Input Validation and Sanitization

Tools implement input validation and sanitization to prevent security issues:

```python
# Sanitize input - only allow alphanumeric chars, spaces, and commas
sanitized_location = re.sub(r'[^\w\s,]', '', location)
if sanitized_location != location:
    print(f"Sanitized location from '{location}' to '{sanitized_location}'")
```

## Installation & Setup

### Prerequisites

- Python 3.8 or higher
- API keys for:
  - OpenAI (or other LLM provider)
  - Weather API (e.g., WeatherAPI.com)
  - Stock API (e.g., Alpha Vantage)

### Installation Steps

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/askwiseai.git
cd askwiseai
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
WEATHER_API_KEY=your_weather_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
```

5. **Run the application**

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`.

## Usage Guide

### Using the API

#### Send a Query

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the weather in London right now?"}'
```

Response:

```json
{
  "response": "Currently in London, United Kingdom, the weather is partly cloudy with a temperature of 15°C (59°F). The humidity is at 76% with a wind speed of 11.2 km/h. This information was last updated at 2023-10-15 14:30.",
  "conversation_id": "3a7c8f9e-1d2b-4e5f-8a9b-0c1d2e3f4a5b",
  "tool_used": "weather",
  "tool_input": {
    "location": "London"
  },
  "tool_output": {
    "location": "London, United Kingdom",
    "temperature_c": 15.0,
    "temperature_f": 59.0,
    "condition": "Partly cloudy",
    "humidity": 76,
    "wind_kph": 11.2,
    "last_updated": "2023-10-15 14:30"
  }
}
```

#### Continue a Conversation

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How about in Paris?", "conversation_id": "3a7c8f9e-1d2b-4e5f-8a9b-0c1d2e3f4a5b"}'
```

Response:

```json
{
  "response": "In Paris, France, the current weather is clear with a temperature of 18°C (64.4°F). The humidity is at 65% with a wind speed of 8.6 km/h. This information was last updated at 2023-10-15 14:45.",
  "conversation_id": "3a7c8f9e-1d2b-4e5f-8a9b-0c1d2e3f4a5b",
  "tool_used": "weather",
  "tool_input": {
    "location": "Paris"
  },
  "tool_output": {
    "location": "Paris, France",
    "temperature_c": 18.0,
    "temperature_f": 64.4,
    "condition": "Clear",
    "humidity": 65,
    "wind_kph": 8.6,
    "last_updated": "2023-10-15 14:45"
  }
}
```

#### Check Health Status

```bash
curl "http://localhost:8000/health"
```

Response:

```json
{
  "status": "healthy",
  "timestamp": 1697383245.6789,
  "stats": {
    "active_conversations": 3,
    "expired_conversations_removed": 2,
    "expired_cache_entries_removed": 5
  }
}
```

## API Reference

### Endpoints

#### POST /query

Process a user query and return a response.

**Request Body:**

```json
{
  "query": "string",
  "conversation_id": "string (optional)"
}
```

**Response:**

```json
{
  "response": "string",
  "conversation_id": "string",
  "tool_used": "string (optional)",
  "tool_input": "object (optional)",
  "tool_output": "object (optional)"
}
```

#### GET /health

Check the health status of the service.

**Response:**

```json
{
  "status": "string",
  "timestamp": "number",
  "stats": {
    "active_conversations": "number",
    "expired_conversations_removed": "number",
    "expired_cache_entries_removed": "number"
  }
}
```

#### DELETE /conversations/{conversation_id}

Delete a conversation.

**Response:**

```json
{
  "status": "string",
  "message": "string"
}
```

## Example Interactions

### General Knowledge Question

**User:** Who was Albert Einstein?

**System Processing:**
1. LLM analyzes query and determines it's general knowledge
2. No tool is needed
3. LLM generates response directly

**Response:** Albert Einstein (1879-1955) was a German-born theoretical physicist who developed the theory of relativity, one of the two pillars of modern physics (alongside quantum mechanics). His work is also known for its influence on the philosophy of science. He is best known to the general public for his mass–energy equivalence formula E = mc². Einstein received the 1921 Nobel Prize in Physics "for his services to theoretical physics, and especially for his discovery of the law of the photoelectric effect," a pivotal step in the development of quantum theory.

### Real-Time Data Question

**User:** What's the current price of Apple stock?

**System Processing:**
1. LLM analyzes query and determines it needs real-time data
2. System selects the stocks tool
3. Tool extracts "AAPL" as the ticker parameter
4. API call is made to fetch current stock data
5. LLM formats the response with the retrieved data

**Response:** As of the latest market data, Apple Inc. (AAPL) is trading at $178.72 per share. The stock has changed by +$1.45 today, which is a 0.82% increase. The trading volume today is 48.3 million shares. This information was last updated on October 15, 2023.

### Follow-Up Question

**User:** How does that compare to Microsoft?

**System Processing:**
1. System retrieves conversation context
2. LLM understands this is a follow-up about stock prices
3. System selects the stocks tool again
4. Tool extracts "MSFT" as the ticker parameter
5. API call is made to fetch Microsoft stock data
6. LLM formats a comparative response

**Response:** Microsoft (MSFT) is currently trading at $332.18 per share, which is $153.46 higher than Apple's current price of $178.72. Microsoft's stock has changed by +$2.34 today (0.71% increase), slightly less than Apple's percentage increase of 0.82%. Microsoft's trading volume today is 22.1 million shares, which is lower than Apple's 48.3 million shares. This suggests that Apple's stock has seen more trading activity today.

### Error Handling Example

**User:** What's the weather in Xyzabcville?

**System Processing:**
1. LLM determines this needs the weather tool
2. Weather API returns an error for the non-existent location
3. System catches the error and falls back to LLM

**Response:** I tried to check the weather for "Xyzabcville," but I couldn't find this location in the weather database. It appears to be a fictional or non-existent place. If you're looking for weather information, please provide a valid city name. Alternatively, if you meant a different location, please clarify the name, and I'll be happy to check the weather there for you.

## Enterprise Scaling Considerations

### Performance Optimization

#### 1. Caching Strategy

AskWiseAI implements a multi-level caching system:

- **LLM Response Caching**: Identical prompts return cached responses (1-hour TTL)
- **Tool Response Caching**: API results are cached with appropriate TTLs:
  - Weather data: 30 minutes
  - Stock data: 5 minutes

This significantly reduces:
- API costs
- Response latency
- External API load

#### 2. Asynchronous Processing

The system uses Python's async/await pattern throughout:

- Non-blocking API calls
- Parallel tool execution when possible
- Efficient handling of multiple concurrent requests

#### 3. Resource Management

- Automatic cleanup of expired cache entries
- Conversation TTL to prevent memory leaks
- Connection pooling for external API calls

### Horizontal Scaling

For enterprise deployment, the system can be scaled horizontally:

- Stateless design allows multiple instances behind a load balancer
- Redis or other distributed cache can replace in-memory caching
- Database backend can replace in-memory conversation storage

## Security & Access Control

### API Key Management

- Environment variables for sensitive credentials
- No hardcoded secrets
- Support for key rotation

### Input Validation & Sanitization

- All user inputs are validated
- Tool parameters are sanitized before use
- Regex patterns prevent injection attacks

### Rate Limiting

For enterprise deployment, implement:

- Per-user rate limits
- Global rate limits
- Graduated throttling

### Data Privacy

- No persistent storage of user queries by default
- Conversation data expires automatically
- Tool parameters are logged but can be redacted

## Evaluation & Accuracy

### Measuring System Performance

To evaluate AskWiseAI's effectiveness, consider these metrics:

1. **Tool Selection Accuracy**: How often does the system correctly choose between LLM and tools?
2. **Response Accuracy**: Are the final answers factually correct?
3. **Response Latency**: How quickly does the system respond?
4. **API Efficiency**: How effectively does the system use external APIs?

### Implementing an Evaluation Framework

For enterprise deployment, implement:

1. **Benchmark Test Suite**: A set of queries with known correct responses
2. **A/B Testing**: Compare different routing strategies
3. **User Feedback Loop**: Allow users to rate response quality
4. **Automated Monitoring**: Track error rates and performance metrics

## Future Enhancements

### Short-Term Improvements

1. **Additional Tools**:
   - News API integration
   - Currency conversion
   - Flight status
   - Sports scores

2. **Enhanced Conversation Memory**:
   - Long-term user preferences
   - Entity memory (remembering specific topics)
   - Summarization of long conversations

### Medium-Term Roadmap

1. **Retrieval-Augmented Generation (RAG)**:
   - Vector database integration (FAISS/Pinecone)
   - Document indexing and retrieval
   - Knowledge base integration

2. **Advanced Tool Selection**:
   - Multi-tool orchestration
   - Tool chaining for complex queries
   - Tool output validation

### Long-Term Vision

1. **Autonomous Tool Discovery**:
   - Dynamic API discovery and integration
   - Self-improving tool selection
   - Custom tool creation

2. **Multimodal Capabilities**:
   - Image understanding and generation
   - Audio processing
   - Chart and graph creation from data

## Contributing

Contributions to AskWiseAI are welcome! Here's how you can help:

1. **Add New Tools**: Implement new API integrations following the Tool interface
2. **Improve Prompts**: Enhance the system prompts for better tool selection
3. **Optimize Performance**: Identify and fix bottlenecks
4. **Add Tests**: Increase test coverage and create benchmarks

Please see CONTRIBUTING.md for detailed guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgments

- OpenAI for the GPT models
- WeatherAPI.com and Alpha Vantage for their API services
- The FastAPI team for their excellent framework

---

*AskWiseAI: Combining the power of LLMs with the precision of real-time data.*
