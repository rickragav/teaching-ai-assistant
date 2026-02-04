# Markdown Response Format

## Overview

The LLM now automatically returns responses in **Markdown format** when requests come from the UI. This provides better formatting and readability.

## Features Enabled

### 1. Automatic Detection
- UI requests are flagged with `source: "ui"`
- LLM receives markdown formatting instructions
- Responses are rendered using marked.js library

### 2. Supported Markdown Syntax

#### Text Formatting
```markdown
**Bold text** - For key concepts and important terms
*Italic text* - For emphasis
`Code text` - For technical terms or code snippets
```

#### Headers
```markdown
### Section Header
Use for organizing content into sections
```

#### Lists
```markdown
Bullet points:
- Point 1
- Point 2
- Point 3

Numbered lists:
1. First step
2. Second step
3. Third step
```

#### Blockquotes
```markdown
> This is a quote or example
> Multiple lines are supported
```

#### Code Blocks
```markdown
```
Multi-line code blocks
with syntax highlighting
```
```

#### Links
```markdown
[Link text](https://example.com)
```

## Visual Styling

### Color Scheme
- **Headers**: Indigo (#6366f1)
- **Bold text**: Indigo (#6366f1)
- **Italic text**: Purple (#8b5cf6)
- **Code inline**: Light indigo background
- **Code blocks**: Dark background with border
- **Blockquotes**: Left border with italic text

### Typography
- **Body text**: Inter font
- **Code**: Fira Code monospace font
- **Line height**: 1.6 for better readability

## Example Output

### Before (Plain Text)
```
Hello! Let me explain the main concepts. Present simple tense is used for habits and facts. For example, I eat breakfast every day. You should remember these key points: Use base form for I/you/we/they and add -s for he/she/it.
```

### After (Markdown Rendered)
```markdown
Hello! Let me explain the **main concepts**.

Present simple tense is used for:
- Habits and routines
- General facts and truths
- Permanent situations

**Example**: *I eat breakfast every day.*

### Key Points
1. Use **base form** for I/you/we/they
2. Add **-s** for he/she/it

> Remember: Practice makes perfect!
```

## Configuration

### LLM Prompt Enhancement
When `source: "ui"`, the system prompt includes:
```
FORMATTING (IMPORTANT):
- Use markdown formatting in your responses
- Use **bold** for key concepts and important terms
- Use *italics* for emphasis
- Use bullet points (- ) for lists
- Use numbered lists (1. 2. 3.) for steps
- Use > for quotes or examples
- Use `code` for technical terms
- Use ### for section headers if needed
- Keep paragraphs separated with blank lines
```

### HTML Rendering
- **Library**: marked.js v11.1.1
- **Options**: GitHub Flavored Markdown (GFM), line breaks enabled
- **Styling**: Custom CSS for dark mode compatibility

## How It Works

### 1. Request Flow
```
User → UI → WebSocket → Add source:"ui" → LangGraph → LLM
```

### 2. Response Flow
```
LLM (Markdown) → LangGraph → WebSocket → marked.parse() → HTML → UI
```

### 3. Code Changes

**State Definition** ([src/state.py](../src/state.py)):
```python
source: Optional[str]  # "ui", "voice", "cli"
```

**Workflow** ([src/workflow.py](../src/workflow.py)):
```python
is_ui_request = state.get('source') == 'ui'
markdown_instruction = "..." if is_ui_request else ""
```

**WebSocket** ([src/api/websocket.py](../src/api/websocket.py)):
```python
state = {
    ...
    "source": "ui"  # Flag for markdown formatting
}
```

**HTML Template** ([src/api/templates.py](../src/api/templates.py)):
```javascript
// Render markdown
if (useMarkdown && typeof marked !== 'undefined') {
    bubble.innerHTML = marked.parse(text);
}
```

## Benefits

✅ **Better Readability** - Structured content with headers and lists  
✅ **Visual Hierarchy** - Important terms stand out  
✅ **Code Highlighting** - Technical terms clearly distinguished  
✅ **Professional Look** - Modern, clean formatting  
✅ **Easy Scanning** - Bullet points and numbered lists  
✅ **Enhanced Learning** - Better organization helps retention  

## Testing

To see markdown in action:

1. Open http://localhost:8000
2. Enter your name
3. Ask: "Explain the main concepts with examples"
4. Watch the response render with:
   - **Bold** key terms
   - *Italic* emphasis
   - Bullet point lists
   - Code formatting
   - Section headers

## Browser Compatibility

- ✅ Chrome/Edge: Full support
- ✅ Firefox: Full support
- ✅ Safari: Full support
- ✅ Mobile: Responsive on all devices

## Performance

- **Fast**: Markdown parsing is near-instantaneous
- **Light**: marked.js is only 24KB minified
- **Cached**: CDN delivery with browser caching
- **No lag**: Rendering happens client-side
