# PyCon Thailand 2025: How to Transform ML APIs into LLM-Compatible MCP Servers with Python

**Speaker:** Tetsuya Hirata
**Conference:** PyCon Thailand 2025
**Duration:** 30 minutes

## 📝 Overview

This repository contains the code and slides for a PyCon Thailand 2025 presentation demonstrating how to transform traditional machine learning APIs into LLM-compatible MCP (Model Context Protocol) servers using Python.

We compare three different approaches to integrating ML tools with LLMs:

1. **REST API** - Standard approach with manual endpoint management
2. **Function Calling** - LLM-native tool integration (using Gemini)
3. **MCP (Model Context Protocol)** - Standardised protocol for tool discovery and execution

## 🎯 Key Message

**MCP makes your ML tools LLM-discoverable** through a standardised protocol, eliminating URL management and enabling automatic tool discovery while maintaining loose coupling between client and server.

## 📁 Repository Structure

```
pyconthailand2025-public/
├── code/                      # Live demo code implementations
│   ├── client/               # Client implementations (REST, FC, MCP)
│   ├── server/               # Server implementations (REST, FC, MCP)
│   ├── requirements.txt      # Python dependencies
│   └── README.md            # Detailed code documentation
│
└── slide/                     # Presentation slides
    ├── preview.html          # Main presentation (open this!)
    ├── image/               # Architecture diagrams
    └── video/               # Live demo video
```

## 🚀 Quick Start

See [code/README.md](code/README.md) for detailed setup instructions and code documentation.

**TL;DR:**
```bash
# 1. Clone and setup
git clone https://github.com/tetsuya0617/pyconthailand2025-public.git
cd pyconthailand2025-public/code
pip install -r requirements.txt

# 2. Set up Gemini API key
echo "GEMINI_API_KEY=your-key-here" > .env

# 3. Run MCP demo (easiest)
python client/mcp_client.py
```

## 📊 Comparison Summary

| Feature | REST API | Function Calling | MCP |
|---------|----------|------------------|-----|
| **Tool Selection** | ❌ Manual routing | ✅ LLM decides | ✅ LLM decides |
| **URL Management** | ❌ Hardcoded URLs | ❌ Manual HTTP endpoints | ✅ None (protocol-based) |
| **Coupling** | ❌ Tight | ⚠️ Medium | ✅ Loose |
| **Standardisation** | ❌ Custom | ❌ Vendor-specific | ✅ MCP protocol |
| **Discovery** | ❌ Manual | ⚠️ Manual fetch | ✅ Automatic |

## 🎓 View Presentation

Open [slide/preview.html](slide/preview.html) in your browser to view the slides.

**GitHub Pages URL:** https://tetsuya0617.github.io/pyconthailand2025-public/slide/preview.html

## 🛠️ Technologies

- **Python 3.11+**
- **Gemini API** - LLM for intelligent tool selection (free tier: 1,500 req/day)
- **FastAPI** - REST API and Function Calling servers
- **FastMCP** - MCP server framework
- **googletrans** - Free translation API
- **faster-whisper** - Speech-to-text
- **Marp** - Markdown-based slide generation

## 📚 Learn More

### MCP Resources
- [MCP Specification](https://modelcontextprotocol.io) - Official protocol documentation
- [FastMCP Framework](https://github.com/jlowin/fastmcp) - Python framework for MCP servers
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) - Official Python SDK

### Gemini API
- [Gemini API Documentation](https://ai.google.dev/docs) - Official API docs
- [Function Calling Guide](https://ai.google.dev/docs/function_calling) - How to use function calling
- [Get API Key](https://aistudio.google.com/app/apikey) - Free tier available

## 📄 License

MIT License - feel free to use this code for learning and teaching purposes.

## 👤 Author

**Tetsuya Hirata**

- **Conference:** PyCon Thailand 2025
- **Talk:** "How to Transform ML APIs into LLM-Compatible MCP Server with Python"
- **GitHub:** [@tetsuya0617](https://github.com/tetsuya0617)

## 🙏 Acknowledgements

- PyCon Thailand 2025 organisers and community
- Anthropic for the MCP specification
- Google for the Gemini API
- FastMCP framework contributors
- The Python community

---

**Questions?** Open an issue or reach out after the conference session.

**Want to try the demo?** See [code/README.md](code/README.md) for step-by-step instructions.
