# AI Interviewer

A production-ready AI-powered technical interview system built with LangGraph and Streamlit.

```
llm-interviewer/
├── .env                    # Environment variables (gitignored)
├── .gitignore             # Git ignore file
├── .pre-commit-config.yaml # Pre-commit hooks configuration
├── README.md              # Project documentation
├── pyproject.toml         # Project configuration and dependencies
├── src/
│   └── llm_interviewer/   # Main package directory
│       ├── __init__.py
│       ├── config.py      # Configuration management
│       ├── prompts/       # Prompt templates
│       │   ├── __init__.py
│       │   └── templates.py
│       ├── conversation/  # Conversation management
│       │   ├── __init__.py
│       │   ├── flow.py
│       │   └── memory.py
│       ├── verification/  # Answer verification
│       │   ├── __init__.py
│       │   └── consistency.py
│       └── utils/         # Utility functions
│           ├── __init__.py
│           └── helpers.py
├── tests/                 # Test directory
│   ├── __init__.py
│   ├── conftest.py       # Test configuration
│   └── test_conversation/
│       └── test_flow.py
└── examples/             # Example usage
    └── basic_interview.py
```


## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   make setup
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your OpenAI API key
   ```

4. Run the application:
   ```bash
   streamlit run streamlit_app.py
   ```

## Deployment Options

### Local Development
```bash
streamlit run streamlit_app.py
```

### Docker Deployment
A Dockerfile has been  provided for containerised deployment.

### Streamlit Cloud
1. Push to GitHub
2. Connect repository to Streamlit Cloud
3. Add environment variables in Streamlit Cloud settings
4. Deploy

### Other Options
- **Heroku**: Add `Procfile` with `web: streamlit run streamlit_app.py --server.port=$PORT`
- **AWS/GCP/Azure**: Use container services with the Docker image