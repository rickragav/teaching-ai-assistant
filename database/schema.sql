-- Simplified database schema for progress tracking only
-- SQLite version

-- User Progress Table (simplified)
CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT UNIQUE NOT NULL,
    current_lesson_id INTEGER NOT NULL DEFAULT 1,
    completed_lessons TEXT NOT NULL DEFAULT '[]',  -- JSON array: [1, 2, 3]
    lesson_scores TEXT NOT NULL DEFAULT '{}',      -- JSON object: {"1": 0.8, "2": 0.9}
    last_accessed TEXT NOT NULL,
    created_at TEXT NOT NULL
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
