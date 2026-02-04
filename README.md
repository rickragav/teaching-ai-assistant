# English Teacher AI Assistant (LangGraph)

An intelligent AI-powered English teacher built with **LangGraph** state machine architecture. Provides interactive lessons using your lesson transcriptions as the knowledge base, with proper workflow orchestration, state management, and conditional routing.

## Architecture

**LangGraph State Machine:**
```
START → retrieve_content → generate_response → [quiz/continue/exit]
     → generate_quiz → evaluate_quiz → update_progress → [next_lesson/retry/continue]
     → END
```

## Features

- **LangGraph StateGraph**: 5 workflow nodes with conditional routing
- **Typed State Management**: TypedDict with `add_messages` annotation
- **RAG-based Learning**: ChromaDB vector store for semantic retrieval
- **Interactive Teaching**: Conversational AI using OpenAI GPT-4o-mini
- **Dynamic Quiz Generation**: Automated quiz creation (70% passing threshold)
- **Progress Tracking**: SQLite database for lesson progress and quiz scores

## Tech Stack

- **LangGraph 0.2.0+** - State machine orchestration
- **LangChain** - LLM interactions
- **ChromaDB** - Vector database
- **OpenAI GPT-4o-mini** - Language model
- **SQLite** - Progress tracking
- **Python 3.11+**

## Setup

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set OpenAI API Key:**
```bash
export OPENAI_API_KEY='your-api-key-here'
```

3. **Add lesson transcriptions:**
Place your `.txt` lesson files in `data/lessons/` or use samples in `data/transcriptions/`

## Usage

**Run the LangGraph CLI:**
```bash
python -m src.main
```

**Interactive Commands:**
- Chat with the teacher about the current lesson
- Type `quiz` to take a quiz (5 questions, 70% to pass)
- Type `exit` to quit

## Testing

```bash
python tests/test_langgraph.py
```

## Key Files

- **[src/workflow.py](src/workflow.py)** - LangGraph state machine with 5 nodes
- **[src/state.py](src/state.py)** - TypedDict state definition
- **[src/main.py](src/main.py)** - CLI interface
- **[tests/test_langgraph.py](tests/test_langgraph.py)** - Workflow tests

## LangGraph Components

**Nodes:** retrieve_content, generate_response, generate_quiz, evaluate_quiz, update_progress

**Conditional Edges:** route_after_response, route_after_progress

**State:** messages, user_id, lesson info, quiz data, workflow control

## License

MIT
