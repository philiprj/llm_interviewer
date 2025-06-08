# 🤖 AI Technical Interviewer

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Poetry](https://img.shields.io/badge/dependency%20management-poetry-blue.svg)](https://python-poetry.org/)
[![Streamlit](https://img.shields.io/badge/web%20framework-streamlit-red.svg)](https://streamlit.io/)
[![LangGraph](https://img.shields.io/badge/workflow-langgraph-green.svg)](https://www.langchain.com/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A production-ready AI-powered technical interview system that conducts structured technical assessments using LangGraph workflows and presents them through an intuitive Streamlit interface.

## 🌟 Features

- **Structured Interviews**: Conducts systematic technical interviews with predefined taxonomies
- **Adaptive Questioning**: AI adapts follow-up questions based on candidate responses
- **Real-time Evaluation**: Provides immediate feedback and performance scoring
- **Multiple Topics**: Covers LLM Architecture, Development, and Applications
- **Progress Tracking**: Visual progress indicators and performance metrics
- **Conversation History**: Complete interview transcript with timestamps
- **Flexible Deployment**: Support for local, Docker, and cloud deployments

## 🏗️ Project Structure

```
llm-interviewer/
├── 📄 Configuration Files
│   ├── pyproject.toml         # Poetry configuration and dependencies
│   ├── .pre-commit-config.yaml # Git hooks for code quality
│   ├── .gitignore            # Git ignore patterns
│   └── .python-version       # Python version specification
│
├── 🐳 Deployment Files
│   ├── Dockerfile            # Container configuration
│   ├── docker-compose.yml    # Local development setup
│   ├── docker-compose.prod.yml # Production deployment
│   └── .dockerignore         # Docker ignore patterns
│
├── 📦 Dependencies
│   ├── requirements.txt      # Production dependencies
│   ├── requirements-dev.txt  # Development dependencies
│   └── poetry.lock          # Locked dependency versions
│
├── 🛠️ Development Tools
│   ├── Makefile             # Development automation commands
│   └── scripts/             # Utility scripts
│
├── 📱 Application
│   ├── streamlit_app.py     # Main Streamlit application
│   └── src/llm_interviewer/ # Core package
│       ├── models/          # Data models and schemas
│       ├── workflows/       # LangGraph interview workflows
│       ├── config/          # Configuration management
│       └── utils/           # Utility functions
│
├── 🧪 Testing & Examples
│   ├── tests/               # Test suite
│   ├── notebooks/           # Jupyter notebooks for experimentation
│   └── data/                # Sample data and configurations
│
└── 📚 Documentation
    ├── README.md            # This file
    └── LICENSE              # MIT License
```

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Poetry (recommended) or pip
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd llm-interviewer
   ```

2. **Set up the environment** (using Poetry - recommended)
   ```bash
   make setup
   ```

   Or manually:
   ```bash
   poetry install
   poetry run pre-commit install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file and add your OpenAI API key:
   # OPENAI_API_KEY=your_api_key_here
   ```

4. **Launch the application**
   ```bash
   make streamlit
   ```

   The application will be available at `http://localhost:8501`

## 🔧 Development Commands

This project uses a comprehensive Makefile for development automation:

### Setup & Installation
```bash
make install        # Install dependencies with lock
make install-dev    # Install with development dependencies
make setup          # Complete initial project setup
```

### Development Server
```bash
make streamlit      # Launch Streamlit dashboard
make streamlit-dev  # Launch with auto-reload (development mode)
make notebook       # Launch Jupyter notebook
```

### Docker Development
```bash
make docker-build   # Build Docker image
make docker-run     # Run Docker container
```

Run `make help` to see all available commands.

## 🎯 Usage

### Starting an Interview

1. **Launch the application** using `make streamlit`
2. **Click "Start Interview"** in the sidebar
3. **Answer questions** in the text area provided
4. **Submit responses** and receive real-time feedback
5. **Track progress** through the sidebar metrics

### Interview Topics

The system covers two main domains:

- **LLM Architecture & Theory**: Core concepts, model structures, training processes
- **LLM Development & Applications**: Practical implementation, fine-tuning, deployment

Each topic includes up to 3 adaptive questions based on your responses.

## 🐳 Deployment Options

### Local Development
```bash
make streamlit
# or
poetry run streamlit run streamlit_app.py
```

### Docker Deployment

**Development environment:**
```bash
docker-compose up
```

**Production environment:**
```bash
docker-compose -f docker-compose.prod.yml up
```

**Manual Docker build:**
```bash
docker build -t llm-interviewer .
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key llm-interviewer
```

### Cloud Deployment

#### Streamlit Cloud
1. Push to GitHub
2. Connect repository to [Streamlit Cloud](https://share.streamlit.io/)
3. Add `OPENAI_API_KEY` in environment variables
4. Deploy

#### AWS/GCP/Azure
Use the provided Docker image with your cloud provider's container services:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
OPENAI_API_KEY=your_openai_api_key

# Optional
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=llm-interviewer
```

### Interview Customization

The interview taxonomy and questions can be customized by modifying the configuration files in `src/llm_interviewer/config/`.

## 🧪 Testing

!TODO!

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run quality checks (`make qa`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Setup

```bash
make setup          # Initial setup
make qa             # Run all quality checks
```

The project uses:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking
- **pre-commit** hooks for automated checks

## 📋 Requirements

### Core Dependencies
- **Python 3.12+**
- **LangChain 0.3.25** - LLM application framework
- **LangGraph 0.3.10** - Workflow orchestration
- **Streamlit 1.28+** - Web interface
- **OpenAI 1.68+** - GPT model integration
- **Pydantic 2.6+** - Data validation

### Development Dependencies
- **pytest** - Testing framework
- **black** - Code formatting
- **mypy** - Type checking
- **pre-commit** - Git hooks

See `pyproject.toml` for complete dependency list.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

If you encounter any issues or have questions:

1. Check the [Issues](../../issues) page
2. Review the documentation
3. Create a new issue with detailed information

## 🔮 Roadmap

- [ ] Improved Response Analysis
- [ ] Automated Taxonomy Extraction
- [ ] Interview analytics and reporting
- [ ] Audio/video interview capabilities
- [ ] Integration with HR systems

---

**Built with ❤️ using LangGraph and Streamlit**
