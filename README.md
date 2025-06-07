# llm_interviewer
LLM chatbot to interview users and assess claimed expertise

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