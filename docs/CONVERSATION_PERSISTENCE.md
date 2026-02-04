# 💬 Conversation Persistence

## Overview

The AI Teaching Assistant now **automatically saves and restores your entire conversation history**. When you return to the application, all your previous messages with the AI will be loaded, allowing you to continue learning exactly where you left off.

## How It Works

### 1. **Automatic Message Storage**
- Every message you send is saved to the database
- Every AI response is also saved
- Messages are stored with timestamps
- Last 100 messages are kept per user (prevents database bloat)

### 2. **Conversation Restoration**
When you enter your name and connect:
- ✅ All previous messages are loaded from database
- ✅ Messages appear in chronological order
- ✅ Markdown formatting is preserved for AI responses
- ✅ You see a system message confirming restoration

### 3. **Database Schema**

Each user now has a `conversation_history` field:

```json
{
  "user_id": "rakesh2310",
  "current_lesson_id": 1,
  "completed_lessons": [],
  "lesson_scores": {},
  "conversation_history": [
    {
      "sender": "user",
      "text": "Explain the main concepts",
      "timestamp": "2026-02-04T17:17:35.123456"
    },
    {
      "sender": "assistant",
      "text": "### Key Concepts\n\n**Communication** is...",
      "timestamp": "2026-02-04T17:17:43.789012"
    }
  ],
  "last_accessed": "2026-02-04T17:17:43.789012",
  "created_at": "2026-02-04T17:09:45.611484"
}
```

## Technical Implementation

### Database Functions

**New Functions in `src/database/progress.py`:**

1. **`save_message(user_id, sender, text)`**
   - Saves individual messages to user's history
   - Automatically adds timestamp
   - Limits history to 100 messages max
   - Thread-safe (uses JSON file locking)

2. **`get_conversation_history(user_id)`**
   - Retrieves all stored messages for a user
   - Returns list of message dictionaries
   - Used during initialization

### WebSocket Integration

**Updates in `src/api/websocket.py`:**

1. **`handle_init()`** - When user connects:
   ```python
   # Get conversation history
   history = get_conversation_history(user_id)
   
   # Send to client
   await websocket.send_json({
       "type": "user_created",
       "conversation_history": history  # Includes all previous messages
   })
   ```

2. **`handle_message()`** - When processing messages:
   ```python
   # Save user message
   save_message(user_id, "user", user_input)
   
   # Process with AI...
   
   # Save AI response
   save_message(user_id, "assistant", response_text)
   ```

### UI Restoration

**Updates in `src/api/templates.py`:**

The UI now handles the `conversation_history` array:

```javascript
if (data.conversation_history && data.conversation_history.length > 0) {
    data.conversation_history.forEach(msg => {
        const emoji = msg.sender === 'user' ? '👤' : '🤖';
        const useMarkdown = msg.sender === 'assistant';
        addMessage(msg.sender, msg.text, emoji, useMarkdown);
    });
    addSystemMessage('✨ Previous conversation restored. Continue learning!');
}
```

## User Experience

### Before (Without Persistence):
```
1. User: "Explain communication styles"
2. AI: [detailed response]
3. User refreshes page
4. 👎 Chat is empty - all context lost
```

### After (With Persistence):
```
1. User: "Explain communication styles"
2. AI: [detailed response]
3. User refreshes page
4. ✅ Previous messages restored
5. User can continue: "Give me more examples"
6. AI has full context from history
```

## Benefits

### 🎯 **For Learners:**
- ✅ Never lose conversation context
- ✅ Can close browser and return later
- ✅ Review previous explanations anytime
- ✅ Seamless learning experience across sessions

### 🔧 **For System:**
- ✅ Thread-safe message storage
- ✅ Automatic history management (100 message limit)
- ✅ Minimal performance impact
- ✅ Works with existing JSON database

### 📊 **For Analytics:**
- ✅ Complete conversation logs per user
- ✅ Timestamp tracking for engagement analysis
- ✅ Message history for debugging/improvement

## Storage Management

### Message Limit
- **Max messages per user:** 100
- **Reason:** Prevents database from growing too large
- **Behavior:** Oldest messages automatically removed when limit reached

### Example:
```python
# In save_message() function
if len(user["conversation_history"]) > 100:
    user["conversation_history"] = user["conversation_history"][-100:]
```

### Storage Size Estimate
- Average message: ~200 bytes
- 100 messages: ~20 KB per user
- 1000 users: ~20 MB total
- Very efficient! 📦

## Testing

### Test Conversation Persistence:

1. **Open the app:** http://localhost:8000
2. **Enter your name:** "testuser"
3. **Send messages:**
   - "Explain the main concepts"
   - "Give me examples"
4. **Close the tab** (or refresh page)
5. **Reopen and enter same name:** "testuser"
6. ✅ **Result:** All previous messages should appear!

### Verify in Database:

Check `database/english_teacher.json`:
```bash
cat database/english_teacher.json | python -m json.tool | grep -A 20 "conversation_history"
```

## Migration Notes

### For Existing Users:
- Old users without `conversation_history` field are automatically upgraded
- First message creates the field
- No data loss for user progress or lesson scores

### Backward Compatibility:
```python
# In save_message() - handles existing users
if "conversation_history" not in user:
    user["conversation_history"] = []
```

## Future Enhancements

Potential improvements:
1. 🔍 **Search history** - Find specific topics in past conversations
2. 📥 **Export chat** - Download conversation as PDF/text
3. 🗑️ **Clear history** - Let users manually reset conversations
4. 🏷️ **Message tags** - Categorize messages by topic/lesson
5. 📊 **Analytics dashboard** - Visualize learning patterns

## Files Modified

1. **`src/database/progress.py`** - Added history functions
2. **`src/api/websocket.py`** - Save/load messages
3. **`src/api/templates.py`** - Render restored messages

## Related Documentation

- [Database Structure](STRUCTURE.md) - Overall architecture
- [Markdown Formatting](MARKDOWN_FORMATTING.md) - Message formatting
- [Logging System](LOGGING.md) - Error tracking

---

**Status:** ✅ Fully Implemented
**Version:** 1.0
**Date:** February 4, 2026
