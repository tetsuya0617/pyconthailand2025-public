# Tool Integration Patterns: REST vs Function Calling vs MCP

This repository demonstrates different approaches to integrating AI tools with LLMs, comparing their architectures, benefits, and trade-offs.

## 🎯 What This Demonstrates

Three different patterns for LLM-tool integration:

1. **REST API** - Traditional approach with manual endpoint management
2. **Function Calling** - LLM-native tool integration (Gemini SDK)
3. **MCP (Model Context Protocol)** - Standardized protocol for tool discovery and execution

## 📁 Project Structure

```
code/
├── client/                 # Client-side implementations
│   ├── rest.py            # REST API client (manual endpoint mapping)
│   ├── fc.py              # Function Calling client (manual execution)
│   └── mcp.py             # MCP client (with Gemini LLM)
│
├── server/                 # Server-side implementations
│   ├── rest.py            # REST API server
│   ├── fc.py              # Function Calling server
│   └── mcp.py             # MCP server
│
├── examples/               # Reference examples (not used in presentation)
│   └── fc_integrated.py   # Function Calling integrated (SDK auto-execution)
│
└── requirements.txt
```

## 🚀 Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Get free API key: https://aistudio.google.com/app/apikey
2. Create `.env` file in project root:
   ```bash
   GEMINI_API_KEY=your-key-here
   ```

**Free tier limits:**
- 15 requests per minute
- 1,500 requests per day
- 1 million tokens per day

## 📖 Pattern Comparison

### 1. REST API Pattern

**Architecture:**
```
User Input → Client (keyword routing) → REST API endpoint → Result
```

**Problems:**
- ❌ Client must maintain `ENDPOINT_MAP` (URL hardcoding)
- ❌ Tight coupling between client and server
- ❌ Endpoint changes require client code updates
- ❌ No intelligent tool selection

**Run:**
```bash
# Terminal 1: Start server
python server/rest.py

# Terminal 2: Run client
python client/rest.py
```

**Example:**
```python
# ❌ Client must hardcode URLs
ENDPOINT_MAP = {
    "translate": "http://localhost:8000/api/translate",
    "stt": "http://localhost:8000/api/stt"
}

# If server changes URL, client breaks
url = ENDPOINT_MAP.get(action)  # Manual mapping required
```

### 2. Function Calling Pattern

**Architecture:**
```
User Input → Gemini (tool selection) → HTTP request → Server (tool execution) → Result
```

**Benefits:**
- ✅ Scalable (tools run on separate server)
- ✅ LLM decides which tool to call
- ✅ Language-agnostic server implementation
- ⚠️ Still requires endpoint management

**Run:**
```bash
# Terminal 1: Start server
python server/fc.py

# Terminal 2: Run client
python client/fc.py
```

**How it works:**
```python
# 1. Fetch tool metadata from server
tools_metadata = fetch_tools_from_server()

# 2. Gemini decides which tool to call (no auto-execution)
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=user_input,
    config=types.GenerateContentConfig(
        tools=[types.Tool(function_declarations=gemini_tools)]
        # No automatic_function_calling - manual execution
    )
)

# 3. Execute tool on server via HTTP
if response.candidates[0].content.parts[0].function_call:
    func_call = response.candidates[0].content.parts[0].function_call
    result = execute_tool_on_server(func_call.name, dict(func_call.args))
```

### 3. MCP (Model Context Protocol) Pattern

**Architecture:**
```
User Input → Gemini (tool selection) → MCP Protocol → Server (tool execution) → Result
```

**Benefits:**
- ✅ Standardized protocol (no custom endpoint mapping)
- ✅ `call_tool(name, args)` - no URL management
- ✅ Automatic tool discovery
- ✅ LLM handles tool selection
- ✅ Loose coupling between client and server

**Run:**
```bash
python client/mcp_client.py
```
(Client automatically manages server lifecycle via stdio)

**Note:** Server file is `server/mcp_server.py` (automatically started by client)

**How it works:**
```python
# 1. MCP client discovers tools automatically
tools = (await session.list_tools()).tools

# 2. Gemini decides which tool to call
tool_decision = llm_decide_tool(user_input, tools)

# 3. Call tool via MCP protocol (no URL needed!)
result = await session.call_tool(
    tool_decision["name"],
    tool_decision.get("arguments", {})
)
# ✅ No ENDPOINT_MAP, no URL management, no tight coupling
```

## 📊 Comparison Table

| Feature | REST API | Function Calling | MCP |
|---------|----------|------------------|-----|
| **Endpoint Management** | ❌ Manual `ENDPOINT_MAP` | ❌ Manual HTTP endpoints | ✅ None (protocol handles it) |
| **Tool Selection** | ❌ Hardcoded logic | ✅ LLM (manual flow) | ✅ LLM |
| **Coupling** | ❌ Tight | ⚠️ Medium | ✅ Loose |
| **Scalability** | ✅ Server can scale | ✅ Server can scale | ✅ Server can scale |
| **URL Changes** | ❌ Breaks client | ❌ Breaks client | ✅ No impact |
| **Complexity** | Medium | High | Medium |
| **Standard Protocol** | ❌ Custom | ❌ Custom | ✅ MCP standard |

## 🎬 Expected Output

### REST API
```
🌐 REST API Client
============================================================
❌ Problems with REST API:
   1. Client must maintain endpoint URLs (ENDPOINT_MAP)
   2. Tight coupling with server implementation
   3. Endpoint changes require client code updates
============================================================

> hello
🔧 Action selected: translate
📡 Calling REST endpoint: http://localhost:8000/api/translate
✅ Result: สวัสดี
```

### Function Calling
```
🎯 Function Calling Client (Client-Server Separated)
============================================================
📡 Connecting to server: http://localhost:8000
✅ Discovered 2 tools from server:
  - translate: Translates the given text to Thai language.
  - stt: Transcribes audio to text.
============================================================

> hello
🔧 Tool selected: translate
📡 Calling server endpoint: /tools/translate
✅ Result: สวัสดี
```

### MCP
```
🚀 Starting MCP Client with Gemini Integration
============================================================
MCP server: Provides tool discovery and execution
Gemini LLM: Decides which tool to call (like Claude Desktop)
============================================================

📋 Discovered 2 tools from MCP server:
  - translate: Translates the given text to Thai language.
  - stt: Transcribes audio data to text.
============================================================

> hello
🤔 LLM deciding which tool to use...
🔧 Tool selected: translate
✅ Result: สวัสดี
```

## 🔑 Key Takeaways

### Why REST API has limitations:
```python
# ❌ Problem: Hardcoded endpoint management
ENDPOINT_MAP = {
    "translate": "http://localhost:8000/api/translate",  # If URL changes?
    "stt": "http://localhost:8000/api/stt"              # Must update client
}
```

### Why MCP is better:
```python
# ✅ Solution: No URL management, protocol-based
result = await session.call_tool("translate", {"text": "hello"})
# Works regardless of server implementation details
```

### Function Calling Trade-offs:
- **Client-Server Separated**: Scalable, but requires manual HTTP handling
- **MCP**: Best approach - scalable AND standardized protocol

## 🛠️ Tools Used

- **Google Translate** (via googletrans 4.0.2) - Free translation
- **faster-whisper** - Lightweight, fast speech-to-text
- **Gemini API** - LLM for intelligent tool selection
- **FastAPI** - REST API and Function Calling servers
- **FastMCP** - MCP server framework

## 🐛 Troubleshooting

### Port already in use:
```bash
lsof -ti:8000 | xargs kill -9
```

### API quota exceeded (429 error):
- Free tier: 1,500 requests/day
- Wait or upgrade to paid tier

### Import errors:
```bash
pip install -r requirements.txt --upgrade
```

## 📚 Learn More

- [Gemini API Documentation](https://ai.google.dev/docs)
- [MCP Specification](https://modelcontextprotocol.io)
- [FastMCP Framework](https://github.com/jlowin/fastmcp)

## 🤔 When Do You Actually Need Client-Server Architecture?

### For Inference-Only ML Products: Client-Server May Be Unnecessary

This demo shows three patterns for **client-server separation**, but it's important to ask: **Do we actually need this architecture for ML products?**

**Key Insight:**
- Traditional web apps need client-server separation because of **database access**
- ML inference is typically **stateless**: `input → model → output`
- No database = No need for server-side state management

**Why This Matters:**
- Models are becoming increasingly **lightweight** (quantization, distillation, edge models)
- Modern devices can run inference locally (on-device LLMs, quantized models)
- Client-server adds complexity for **no functional benefit** in pure inference scenarios

**When Client-Server IS Needed:**
- ✅ **Tool Reusability**: Multiple clients need the same tools (e.g., corporate translation API)
- ✅ **External Service Integration**: Tools access external APIs, databases, or cloud services
- ✅ **Model Too Large**: Model cannot run on client device
- ✅ **Centralized Control**: Need to update model/logic without updating clients

**When Client-Server Is NOT Needed:**
- ❌ **Pure Local Inference**: Model runs on user's device with no external dependencies
- ❌ **Lightweight Models**: Model is small enough for local execution (Gemini Flash, Whisper, small LLMs)
- ❌ **No Shared State**: No database, no multi-user coordination

**This Demo's Purpose:**
These patterns (REST/FC/MCP) are useful for **understanding architectural options**, but recognize that for many ML use cases, a simpler integrated approach (like [examples/fc_integrated.py](examples/fc_integrated.py)) may be better. The trend toward lighter models makes local execution increasingly viable.

## 🎓 Presentation Focus

**Main Message:**
1. **REST API**: Traditional but requires manual endpoint management
2. **Function Calling**: LLM-native, but still requires custom HTTP handling
3. **MCP**: Combines standardization with LLM intelligence - no endpoint management, loose coupling, automatic tool discovery
4. **Architectural Consideration**: For stateless ML inference with lightweight models, client-server separation may be unnecessary

**Demo Flow:**
1. Show REST client with `ENDPOINT_MAP` problem
2. Show Function Calling with LLM tool selection but still manual HTTP
3. Show MCP eliminating endpoint management while keeping LLM intelligence
4. Discuss when these patterns are actually needed vs when local execution suffices
