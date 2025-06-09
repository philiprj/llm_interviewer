# 🤖 AI Technical Interviewer

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/dependency%20management-poetry-blue.svg)](https://python-poetry.org/)
[![Streamlit](https://img.shields.io/badge/web%20framework-streamlit-red.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/workflow-langgraph-green.svg)](https://www.langchain.com/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready AI-powered technical interview system that conducts structured technical assessments using LangGraph workflows and Streamlit.

## 🌟 Features

- **Structured Interviews**: Systematic technical interviews with predefined taxonomies
- **Adaptive Questioning**: AI adapts follow-up questions based on candidate responses
- **Real-time Evaluation**: Immediate feedback and performance scoring
- **Multiple Topics**: Covers LLM Architecture, Development, and Applications
- **Progress Tracking**: Visual progress indicators and conversation history

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Poetry (recommended)
- OpenAI API key

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd llm-interviewer
   make setup  # or poetry install && poetry run pre-commit install
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Add your OpenAI API key to .env file
   ```

3. **Launch**
   ```bash
   make streamlit  # App available at http://localhost:8501
   ```

## 🔧 Development

### Key Commands
```bash
make help           # See all available commands
make streamlit      # Launch app
make streamlit-dev  # Launch with auto-reload
make docker-build   # Build Docker image
make docker-run     # Run in container
make qa            # Run quality checks
```

## 🎯 Usage

1. Click "Start Interview" in the sidebar
2. Answer questions in the text area
3. Submit responses for real-time feedback
4. Track progress through sidebar metrics

**Interview Topics**: LLM Architecture & Theory, LLM Development & Applications

## 🐳 Deployment

### Local
```bash
make streamlit
```

### Docker
```bash
# Development
docker-compose up

# Production
docker-compose -f docker-compose.prod.yml up
```

### Cloud
- **Streamlit Cloud**: Connect GitHub repo, add `OPENAI_API_KEY`
- **Container Services**: Use Docker image with AWS ECS, Google Cloud Run, or Azure Container Instances

## ⚙️ Configuration

Required environment variables:
```bash
OPENAI_API_KEY=your_openai_api_key

# Optional (for LangSmith tracing)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
```

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes and run `make qa`
4. Submit Pull Request

**Code Quality**: Uses Black, isort, flake8, mypy, and pre-commit hooks.

## 📋 Dependencies

**Core**: LangChain 0.3.25, LangGraph 0.3.10, Streamlit 1.28+, OpenAI 1.68+, Pydantic 2.6+

**Dev**: pytest, black, mypy, pre-commit

See `pyproject.toml` for complete list.

## 📄 License

MIT License - see [LICENSE](LICENSE) file.

## 🔮 Roadmap

- [ ] Improved response analysis and automated taxonomy extraction
- [ ] Interview analytics and reporting
- [ ] Audio/video capabilities
- [ ] HR system integrations

---

**Built with ❤️ using LangGraph and Streamlit**
