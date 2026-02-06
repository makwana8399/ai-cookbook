# AI Cookbook - Workflows & Patterns 🧠

## Overview

~ AI Cookbook is a comprehensive collection of Python workflows and patterns for building intelligent applications using modern AI/ML techniques. This repository provides production-ready examples, utilities, and architectural patterns for AI-powered systems.

## Repository Structure

<img width="963" height="528" alt="image" src="https://github.com/user-attachments/assets/83cc70f7-196e-47ed-a470-56779d6fe8bc" />

# Installation

## Prerequisites

- Python 3.8+
- pip package manager
- OpenAI API key (or other LLM provider)

## Clone the repository

- git clone https://github.com/makwana8399/ai-cookbook.git
- cd ai-cookbook/patterns/workflows

## Create virtual environment

- python -m venv venv
- source venv/bin/activate  # On Windows: venv\Scripts\activate

## Install dependencies

- pip install -r requirements.txt

## Configure environment variables

cp .env.example .env

## Edit .env with your API keys and configuration

- Quick Start
- Basic Workflow
- python

## Run a basic workflow example
python basic-workflows/1-basic.py
Advanced Orchestration
python

## Execute parallel workflow patterns
python advanced-workflows/3-parallizaton.py
Workflow Examples

1. Basic Workflows

- Basic Patterns (1-basic.py): Simple LLM interactions and prompt engineering
- Structured Outputs (2-structured.py): Extracting structured data from LLM responses
- Tool Integration (3-tools.py): Function calling and external tool integration
- Retrieval-Augmented (4-retrieval.py): RAG implementations with vector search

2. Advanced Workflows
- Prompt Chaining (1-prompt-chaining.py): Sequential multi-prompt workflows
- Dynamic Routing (2-routing.py): Conditional workflow execution paths
- Parallel Processing (3-parallizaton.py): Concurrent AI task execution
- Orchestrator Pattern (4-orchestrator.py): Centralized workflow management

## Environment Configuration

- Create a .env file with the following variables:

OPENAI_API_KEY=your_api_key_here
ANTHROPIC_API_KEY=your_key_optional
GROQ_API_KEY=your_key_optional
DATABASE_URL=your_database_url_optional
VECTOR_DB_PATH=./data/embeddings

## Dependencies

Key Python packages include:

openai/anthropic - LLM API clients
langchain/llama-index - Framework integrations
pydantic - Data validation
chromadb/faiss-Vector databases
python-dotenv-Environment management

### Usage Examples :

Example 1: Structured Data Extraction

from workflows.structured import extract_entities

result = extract_entities(
    text="Apple Inc. reported $90B revenue in Q4 2023",
    schema={"company": str, "metric": str, "value": float, "period": str}
)

## Returns structured dictionary

Example 2: Parallel Workflow Execution

from workflows.parallizaton import execute_parallel_tasks

tasks = [
    {"type": "summarize", "content": "long text..."},
    {"type": "classify", "content": "another text..."}
]

results = execute_parallel_tasks(tasks, max_workers=3)

## Knowledge Base

The kb.json file contains sample data, schemas, and examples used in the workflow demonstrations. This includes:

- Example documents for RAG workflows
- Structured data schemas
- Prompt templates
- Configuration examples

## Contributing
We welcome contributions! Please follow these steps:

- Fork the repository
- Create a feature branch
- Add tests for new functionality
- Submit a pull request
- 
## License

MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions:

- Open an issue on GitHub
- Check existing examples in the workflows directory
- Review all-files-cmds.txt for execution commands

## Roadmap

- Add more LLM provider integrations
- Implement streaming workflow support
- Add monitoring and observability patterns
- Create deployment examples (Docker, Kubernetes)

Built with ❤️ by the AI Cookbook community
