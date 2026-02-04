# Discussion - English Teacher AI Assistant

## Project Overview
This document tracks discussions and decisions related to the English Teacher AI Assistant project.

## Conversation History

### January 27, 2026

**Initial Conversation:**
- Started discussion about the English Teacher AI Assistant project
- User greeted and initiated conversation context setup

## Requirements (Simplified)
1. **RAG-Based Learning** - Use lesson transcriptions as knowledge base, retrieve relevant content via RAG
2. **Conversational Teaching** - AI teaches through natural conversation, not rigid workflows
3. **Sequential Progress** - Track which lesson user is on (Lesson 1 → 2 → 3...)
4. **Quiz After Each Lesson** - Generate quiz questions based on lesson content
5. **Resume Capability** - Continue from last position when user returns

## Simplified Architecture

### System Overview
```
User Input
    ↓
Check Progress → Load current lesson
    ↓
RAG Retrieval → Fetch lesson content from transcriptions
    ↓
Conversational LLM → Teach + Answer questions
    ↓
User says "ready for quiz" or lesson complete
    ↓
Quiz Generation → Create 5 questions from lesson
    ↓
Collect Answers → User responds
    ↓
Grade & Feedback → Evaluate (70% to pass)
    ↓
Update Progress → Save score, move to next lesson if passed
```

### Core Components
1. **Vector Store (ChromaDB)** - Stores lesson transcriptions with embeddings
2. **RAG Retriever** - Fetches relevant lesson chunks based on query
3. **Conversation Agent** - Single LLM that teaches naturally
4. **Progress Tracker** - SQLite database tracking user progress
5. **Quiz Generator** - LLM creates quiz from lesson content

### State Management (Minimal)
```python
class ConversationState(TypedDict):
    user_id: str
    current_lesson_id: int
    lesson_title: str
    messages: List[Dict]  # Conversation history
    phase: str  # "teaching" or "quiz"
    quiz_questions: List[Dict]
    quiz_answers: List[str]
    quiz_score: Optional[float]
```

### Technical Stack
- **LangChain** - LLM interactions and RAG
- **LangGraph** - Simple state machine
- **ChromaDB** - Vector database for transcriptions
- **OpenAI GPT-4** - Conversational teaching
- **SQLite** - Progress tracking only
- **Pydantic** - Data validation

---

## Implementation Phases (6 Total)

### Phase 1: Project Setup ✅ (Partial)
**Objective**: Basic project structure and dependencies

**Tasks**:
- ✅ Create folder structure: `src/`, `src/rag/`, `src/utils/`, `data/transcriptions/`, `database/`
- ✅ Update `requirements.txt` with simplified dependencies
- ✅ Configure `.env` with API keys
- ✅ Create `config.py` for settings
- ✅ Setup logger utility

**Deliverables**:
- Clean folder structure
- Dependencies installed
- Config ready

---

### Phase 2: RAG System
**Objective**: Load transcriptions and create searchable knowledge base

**Tasks**:
- Create `src/rag/loader.py`:
  - Load lesson transcription files
  - Split into chunks
  - Create embeddings
- Create `src/rag/vector_store.py`:
  - Initialize ChromaDB
  - Store lesson chunks with metadata (lesson_id, lesson_title)
  - Create retriever
- Create sample transcriptions:
  - `data/transcriptions/lesson_1.txt`
  - `data/transcriptions/lesson_2.txt`
  - `data/transcriptions/lesson_3.txt`
- Test retrieval with queries

**Deliverables**:
- RAG system functional
- 3+ lesson transcriptions loaded
- Retrieval tested and working

---

### Phase 3: Simple Database
**Objective**: Track user progress only (no complex schema)

**Tasks**:
- Create `database/schema.sql`:
  - `user_progress` table only (user_id, current_lesson_id, completed_lessons, scores)
- Create `src/database/connection.py`:
  - Simple SQLite connection
- Create `src/database/progress.py`:
  - `get_user_progress(user_id)`
  - `update_progress(user_id, lesson_id, score)`
  - `get_or_create_user(user_id)`
- Initialize database

**Deliverables**:
- Minimal SQLite database
- Progress CRUD operations
- Tested and working

---

### Phase 4: Conversational Agent
**Objective**: Build RAG-powered teaching agent

**Tasks**:
- Create `src/state.py`:
  - Define `ConversationState` TypedDict
- Create `src/agent/teacher.py`:
  - Load user progress
  - Retrieve lesson content via RAG
  - Conversational LLM with context
  - Detect when user wants quiz
- Create `src/prompts.py`:
  - System prompt for teaching
  - Quiz detection logic
- Test conversational flow

**Deliverables**:
- Agent teaches using RAG content
- Natural conversation flow
- Quiz readiness detection

---

### Phase 5: Quiz System
**Objective**: Generate and grade quizzes from lesson content

**Tasks**:
- Create `src/agent/quiz_generator.py`:
  - Retrieve lesson content
  - Generate 5 questions (3 MCQ, 1 fill-blank, 1 short answer)
  - Return structured questions
- Create `src/agent/quiz_evaluator.py`:
  - Compare user answers to correct answers
  - Calculate score
  - Generate feedback
  - Determine pass/fail (70% threshold)
- Integrate with conversation flow

**Deliverables**:
- Quiz generation working
- Grading accurate
- Feedback provided

---

### Phase 6: Integration & Resume
**Objective**: Connect everything and add session resume

**Tasks**:
- Create `src/graph.py`:
  - Build LangGraph workflow
  - Connect: Progress Check → Teaching → Quiz → Update
  - Add conditional routing
- Create `src/main.py`:
  - CLI interface
  - Session management
  - Resume capability using checkpoints
- Add LangGraph checkpointer:
  - Save state after each interaction
  - Resume from last checkpoint
- End-to-end testing

**Deliverables**:
- Complete working system
- CLI interface
- Resume functionality
- Full lesson flow functional

---

## Folder Structure (Simplified)

```
english-teacher-ai-assistant/
├── .env                          # API keys
├── .gitignore
├── requirements.txt              # Simplified dependencies
├── discussion.md
│
├── src/
│   ├── __init__.py
│   ├── config.py                 # Settings
│   ├── state.py                  # State schema
│   ├── prompts.py                # LLM prompts
│   ├── graph.py                  # LangGraph workflow
│   ├── main.py                   # Entry point
│   │
│   ├── rag/                      # RAG system
│   │   ├── __init__.py
│   │   ├── loader.py             # Load transcriptions
│   │   └── vector_store.py       # ChromaDB operations
│   │
│   ├── agent/                    # Core agents
│   │   ├── __init__.py
│   │   ├── teacher.py            # Conversational teacher
│   │   ├── quiz_generator.py    # Quiz creation
│   │   └── quiz_evaluator.py    # Quiz grading
│   │
│   ├── database/                 # Simple progress DB
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── progress.py
│   │
│   └── utils/
│       ├── __init__.py
│       └── logger.py
│
├── data/
│   └── transcriptions/           # Your lesson transcriptions
│       ├── lesson_1.txt
│       ├── lesson_2.txt
│       └── lesson_3.txt
│
├── database/
│   ├── schema.sql
│   └── progress.db               # SQLite database
│
└── tests/
    └── test_rag.py
```

---

## Current Status
- **Completed**: Phase 1 (Partial - basic setup done)
- **Next**: Complete Phase 1, then move to Phase 2 (RAG Setup)

---

## Next Steps
1. Clean up existing complex files (models.py, database/ folder)
2. Update requirements.txt with simplified dependencies
3. Prepare 3 lesson transcription files
4. Start Phase 2: RAG System

---

## Notes
- **Data Source**: You provide lesson transcriptions (text files)
- **No pre-structured JSON**: Just raw transcription text
- **Conversational**: AI teaches naturally, not step-by-step
- **Simple Progress**: Only track current lesson and scores
- **6 phases**: Much simpler than original 10-phase plan