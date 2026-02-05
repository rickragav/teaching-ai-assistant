# 📱 Flutter AI English Teacher App - Design Document

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Project Structure](#project-structure)
4. [Technology Stack](#technology-stack)
5. [Screen Design & Flow](#screen-design--flow)
6. [Data Models](#data-models)
7. [API Integration](#api-integration)
8. [State Management (BLoC)](#state-management-bloc)
9. [Implementation Plan](#implementation-plan)

---

## Overview

**App Name:** AI English Teacher Mobile App  
**Platform:** Flutter (iOS + Android)  
**Backend:** LangGraph Teaching Engine + FastAPI  
**Primary Focus:** Chat-based English learning with voice integration  

### Key Features
- ✅ User authentication (Phone + Name)
- ✅ Chat-based learning
- ✅ Real-time WebSocket communication
- ✅ Message persistence (SQLite)
- ✅ Voice learning (Phase 2)
- ✅ User progress tracking

---

## Architecture

### Pattern: **Clean Architecture + BLoC**

```
┌─────────────────────────────────────────────────────┐
│         PRESENTATION LAYER (UI + BLoC)              │
│  ┌──────────────────────────────────────────────┐   │
│  │  Screens  │  Widgets  │  BLoC  │  Pages     │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│          DOMAIN LAYER (Business Logic)              │
│  ┌──────────────────────────────────────────────┐   │
│  │  Entities  │  Repositories  │  UseCases      │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│         DATA LAYER (Data Sources)                   │
│  ┌──────────────────────────────────────────────┐   │
│  │ Remote (API) │ Local (SQLite) │ Models       │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

### Benefits
- **Separation of Concerns**: Each layer has a specific responsibility
- **Testability**: Easy to unit test each layer independently
- **Scalability**: Easy to add new features without breaking existing code
- **Maintainability**: Clear structure makes it easy to navigate
- **Reusability**: Components can be reused across features

---

## Project Structure

```
english_teacher_app/
│
├── lib/
│   ├── core/
│   │   ├── constants/
│   │   │   └── app_constants.dart          # API URLs, app configuration
│   │   ├── errors/ 
│   │   │   ├── exceptions.dart             # Custom exception classes
│   │   │   └── failures.dart               # Failure response classes
│   │   ├── network/
│   │   │   ├── websocket_client.dart       # WebSocket wrapper
│   │   │   └── http_client.dart            # HTTP client wrapper
│   │   ├── utils/
│   │   │   ├── validators.dart             # Input validation logic
│   │   │   ├── logger.dart                 # Logging utility
│   │   │   └── extensions.dart             # Dart extensions
│   │   └── widgets/
│   │       └── common_widgets.dart         # Reusable widgets
│   │
│   ├── features/
│   │   │
│   │   ├── auth/                           # Authentication Feature
│   │   │   ├── data/
│   │   │   │   ├── datasources/
│   │   │   │   │   └── auth_local_datasource.dart
│   │   │   │   ├── models/
│   │   │   │   │   └── user_model.dart
│   │   │   │   └── repositories/
│   │   │   │       └── auth_repository_impl.dart
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   └── user.dart
│   │   │   │   ├── repositories/
│   │   │   │   │   └── auth_repository.dart
│   │   │   │   └── usecases/
│   │   │   │       ├── login_usecase.dart
│   │   │   │       └── get_user_usecase.dart
│   │   │   └── presentation/
│   │   │       ├── bloc/
│   │   │       │   ├── auth_bloc.dart
│   │   │       │   ├── auth_event.dart
│   │   │       │   └── auth_state.dart
│   │   │       ├── pages/
│   │   │       │   └── login_screen.dart
│   │   │       └── widgets/
│   │   │           ├── phone_input_field.dart
│   │   │           └── name_input_field.dart
│   │   │
│   │   ├── mode_selection/                 # Mode Selection Feature
│   │   │   ├── presentation/
│   │   │   │   ├── bloc/
│   │   │   │   │   ├── mode_bloc.dart
│   │   │   │   │   ├── mode_event.dart
│   │   │   │   │   └── mode_state.dart
│   │   │   │   ├── pages/
│   │   │   │   │   └── mode_selection_screen.dart
│   │   │   │   └── widgets/
│   │   │   │       └── mode_card.dart
│   │   │   └── domain/
│   │   │       └── entities/
│   │   │           └── mode.dart
│   │   │
│   │   └── chat/                           # Chat Feature (Main Focus)
│   │       ├── data/
│   │       │   ├── datasources/
│   │       │   │   ├── remote_chat_datasource.dart  # WebSocket
│   │       │   │   └── local_chat_datasource.dart   # SQLite
│   │       │   ├── models/
│   │       │   │   ├── message_model.dart
│   │       │   │   └── chat_model.dart
│   │       │   └── repositories/
│   │       │       └── chat_repository_impl.dart
│   │       ├── domain/
│   │       │   ├── entities/
│   │       │   │   ├── message.dart
│   │       │   │   └── chat_session.dart
│   │       │   ├── repositories/
│   │       │   │   └── chat_repository.dart
│   │       │   └── usecases/
│   │       │       ├── send_message_usecase.dart
│   │       │       ├── get_messages_usecase.dart
│   │       │       └── stream_messages_usecase.dart
│   │       └── presentation/
│   │           ├── bloc/
│   │           │   ├── chat_bloc.dart
│   │           │   ├── chat_event.dart
│   │           │   └── chat_state.dart
│   │           ├── pages/
│   │           │   └── chat_screen.dart
│   │           └── widgets/
│   │               ├── message_bubble.dart
│   │               ├── message_list.dart
│   │               ├── chat_input_field.dart
│   │               └── typing_indicator.dart
│   │
│   ├── main.dart                           # App entry point
│   └── service_locator.dart                # Dependency injection setup
│
├── test/
│   ├── features/
│   │   ├── auth/
│   │   │   ├── bloc_test.dart
│   │   │   ├── repository_test.dart
│   │   │   └── usecase_test.dart
│   │   └── chat/
│   │       ├── bloc_test.dart
│   │       └── repository_test.dart
│   └── core/
│       └── network_test.dart
│
├── pubspec.yaml
├── analysis_options.yaml
└── README.md
```

---

## Technology Stack

### Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  
  # ========== STATE MANAGEMENT ==========
  flutter_bloc: ^8.1.0              # BLoC state management
  bloc: ^8.1.0                      # Core BLoC package
  
  # ========== NETWORKING ==========
  http: ^1.1.0                      # HTTP client
  web_socket_channel: ^2.4.0        # WebSocket communication
  
  # ========== DEPENDENCY INJECTION ==========
  get_it: ^7.5.0                    # Service locator
  
  # ========== FUNCTIONAL PROGRAMMING ==========
  dartz: ^0.10.1                    # Either/Fold for error handling
  
  # ========== LOCAL STORAGE ==========
  sqflite: ^2.3.0                   # SQLite database
  path_provider: ^2.1.0             # File system paths
  shared_preferences: ^2.1.0        # Key-value storage
  
  # ========== UI ==========
  flutter_spinkit: ^5.2.0           # Loading spinners
  intl: ^0.18.0                     # Date/time formatting
  
  # ========== VALIDATION ==========
  form_validator: ^0.8.0            # Form validation
  
  # ========== ENVIRONMENT ==========
  flutter_dotenv: ^5.1.0            # Environment variables

dev_dependencies:
  flutter_test:
    sdk: flutter
  
  # ========== TESTING ==========
  mockito: ^5.4.0                   # Mocking library
  bloc_test: ^9.1.0                 # BLoC testing utilities
  build_runner: ^2.4.0              # Code generation
```

---

## Screen Design & Flow

### Screen 1: Login Screen

```
┌──────────────────────────────┐
│                              │
│      🎓 Logo                 │
│                              │
│ AI English Teacher           │
│ Learn English with AI        │
│                              │
├──────────────────────────────┤
│                              │
│ 📱 Enter Phone Number        │
│ [____________________]       │
│ (10 digits required)         │
│                              │
│ 👤 Enter Your Name           │
│ [____________________]       │
│ (2+ characters required)     │
│                              │
│ [    Continue →    ]         │
│ (Disabled until valid)       │
│                              │
│ ────────────────────────────  │
│ Powered by LangGraph AI       │
│                              │
└──────────────────────────────┘
```

**Flow:**
1. User enters phone number (validation: 10 digits)
2. User enters name (validation: 2+ characters)
3. Continue button enabled when both fields valid
4. On continue: Save to SharedPreferences + Navigate to Mode Selection

---

### Screen 2: Mode Selection Screen

```
┌──────────────────────────────┐
│                              │
│  Welcome, John Doe! 👋       │
│                              │
│ Choose Your Learning Mode    │
│                              │
├──────────────────────────────┤
│                              │
│ ┌────────────────────────┐   │
│ │        💬              │   │
│ │    Text Chat Mode      │   │
│ │                        │   │
│ │  Type and chat with    │   │
│ │  AI for learning       │   │
│ │                        │   │
│ │  [  Start Chat  ]      │   │
│ └────────────────────────┘   │
│                              │
│ ┌────────────────────────┐   │
│ │        🎤              │   │
│ │    Voice Mode          │   │
│ │                        │   │
│ │  Speak and listen to   │   │
│ │  AI (Coming Soon)      │   │
│ │                        │   │
│ │  [  Coming Soon  ]     │   │
│ └────────────────────────┘   │
│                              │
└──────────────────────────────┘
```

**Flow:**
1. Display user greeting with name
2. Show two mode cards: Chat (active) and Voice (disabled)
3. On Chat tap: Navigate to Chat Screen
4. On Voice tap: Show "Coming Soon" message

---

### Screen 3: Chat Screen (MAIN FOCUS)

```
┌──────────────────────────────┐
│ ← | AI Teacher    🔄 Switch │  Header
├──────────────────────────────┤
│                              │
│ 👋 Hello! I'm your English   │
│    teacher. How can I help?  │  Bot Message
│                              │
│                      You:    │
│               Hi there!      │  User Message
│                              │
│ Great! What topic would you  │
│ like to learn about?         │
│ 1. Grammar                   │  Bot Message
│ 2. Vocabulary                │  with Options
│ 3. Pronunciation             │
│                              │
│ ⚪⚪⚪                    ← Typing Indicator
│                              │
├──────────────────────────────┤
│ [________Type message...___] │  Input Area
│                          [↗] │  Send Button
└──────────────────────────────┘
```

**Features:**
- ✅ Message bubbles (user right, bot left)
- ✅ Real-time message streaming
- ✅ Typing indicator animation
- ✅ Send button with loading state
- ✅ Pull to refresh for history
- ✅ Auto-scroll to latest message
- ✅ Message timestamps

---

## Data Models

### User Entity (Domain)
```dart
class User {
  final String phoneNumber;
  final String name;
  final DateTime createdAt;
  
  User({
    required this.phoneNumber,
    required this.name,
    required this.createdAt,
  });
}
```

### User Model (Data)
```dart
class UserModel extends User {
  UserModel({
    required String phoneNumber,
    required String name,
    required DateTime createdAt,
  }) : super(
    phoneNumber: phoneNumber,
    name: name,
    createdAt: createdAt,
  );
  
  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      phoneNumber: json['phone_number'],
      name: json['name'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
  
  Map<String, dynamic> toJson() => {
    'phone_number': phoneNumber,
    'name': name,
    'created_at': createdAt.toIso8601String(),
  };
}
```

### Message Entity (Domain)
```dart
class Message {
  final String id;
  final String sender;        // 'user' or 'bot'
  final String text;
  final DateTime timestamp;
  final MessageStatus status; // sending, sent, failed
  
  Message({
    required this.id,
    required this.sender,
    required this.text,
    required this.timestamp,
    this.status = MessageStatus.sent,
  });
}

enum MessageStatus { sending, sent, failed }
```

### Message Model (Data)
```dart
class MessageModel extends Message {
  MessageModel({
    required String id,
    required String sender,
    required String text,
    required DateTime timestamp,
    MessageStatus status = MessageStatus.sent,
  }) : super(
    id: id,
    sender: sender,
    text: text,
    timestamp: timestamp,
    status: status,
  );
  
  factory MessageModel.fromJson(Map<String, dynamic> json) {
    return MessageModel(
      id: json['id'],
      sender: json['sender'],
      text: json['text'],
      timestamp: DateTime.parse(json['timestamp']),
      status: MessageStatus.values.byName(json['status']),
    );
  }
  
  Map<String, dynamic> toJson() => {
    'id': id,
    'sender': sender,
    'text': text,
    'timestamp': timestamp.toIso8601String(),
    'status': status.name,
  };
}
```

---

## API Integration

### Backend Endpoints

#### REST Endpoints
```
GET  /api/health              Check server health
GET  /api/lessons             Get available lessons
GET  /api/user/{user_id}      Get user progress
```

#### WebSocket Endpoint
```
WS   /ws                      Real-time chat connection
```

### API Communication Flow

#### 1. Login Flow (REST)
```
Client                          Server
  │                               │
  ├─── POST /api/login ────────→ │
  │    {phone, name}              │
  │                               │
  │ ←─── 200 OK ────────────────┤ │
  │      {user_id, token}         │
  │                               │
  └─ Save to SharedPreferences    │
```

#### 2. Chat Flow (WebSocket)
```
Client                          Server
  │                               │
  ├─── WS Connect ─────────────→ │
  │                               │
  ├─── Init Message ────────────→ │
  │    {type: 'init',             │
  │     user_id: 'xxx'}           │
  │                               │
  ├─── Send Message ────────────→ │
  │    {type: 'message',          │
  │     text: 'Hello'}            │
  │                               │
  │ ←─── Message Response ──────┤ │
  │      {type: 'response',       │
  │       text: 'Hi there!'}      │
  │                               │
  └─── Disconnect ──────────────→ │
```

### Error Handling
```
Success Response:
{
  "status": "success",
  "data": {...}
}

Error Response:
{
  "status": "error",
  "message": "User already exists",
  "code": "USER_EXISTS"
}
```

---

## State Management (BLoC)

### BLoC Pattern Flow

```
User Action → Event → BLoC → UseCase → Repository → DataSource
                        ↓
                      State
                        ↓
                       UI Updates
```

### Auth BLoC

**Events:**
- `LoginEvent(phoneNumber, name)`
- `LogoutEvent()`
- `GetUserEvent()`

**States:**
- `AuthInitial()`
- `AuthLoading()`
- `AuthSuccess(user)`
- `AuthFailure(message)`

### Chat BLoC

**Events:**
- `SendMessageEvent(text)`
- `ReceiveMessageEvent(message)`
- `LoadMessagesEvent()`
- `ClearChatEvent()`

**States:**
- `ChatInitial()`
- `ChatLoading()`
- `ChatLoaded(messages)`
- `MessageSending()`
- `MessageSent()`
- `ChatError(message)`

---

## Implementation Plan

### Phase 1: Setup & Core Infrastructure
- [ ] Create Flutter project structure
- [ ] Setup dependency injection (GetIt)
- [ ] Create error handling & exceptions
- [ ] Create API constants & configuration
- [ ] Setup logger utility

### Phase 2: Authentication Feature
- [ ] Create auth entities & models
- [ ] Create auth repository & datasources
- [ ] Create auth usecases
- [ ] Create auth BLoC (events, states)
- [ ] Create login screen UI
- [ ] Create input validation

### Phase 3: Mode Selection Feature
- [ ] Create mode selection BLoC
- [ ] Create mode selection screen
- [ ] Create mode card widget

### Phase 4: Chat Feature - Data Layer
- [ ] Create message entities & models
- [ ] Create websocket client wrapper
- [ ] Create remote chat datasource
- [ ] Create local chat datasource (SQLite)
- [ ] Create chat repository

### Phase 5: Chat Feature - Domain Layer
- [ ] Create chat repository interface
- [ ] Create send message usecase
- [ ] Create get messages usecase
- [ ] Create stream messages usecase

### Phase 6: Chat Feature - Presentation
- [ ] Create chat BLoC (events, states)
- [ ] Create chat screen UI
- [ ] Create message bubble widget
- [ ] Create message list widget
- [ ] Create chat input field widget
- [ ] Create typing indicator widget

### Phase 7: Testing & Polish
- [ ] Unit tests for repositories
- [ ] BLoC tests
- [ ] Integration tests
- [ ] UI Polish & animations
- [ ] Performance optimization

### Phase 8: Voice Feature (Future)
- [ ] Create voice datasources
- [ ] Create voice BLoC
- [ ] Create voice screen UI
- [ ] Integration with Web Speech API / native audio

---

## Key Implementation Details

### WebSocket Connection Strategy
```dart
// Establish WebSocket connection on chat screen entry
// Maintain connection for entire chat session
// Handle reconnection automatically on connection loss
// Implement heartbeat to keep connection alive
```

### Message Persistence
```dart
// Save messages to SQLite after receiving
// Load messages from SQLite on chat screen load
// Sync with server when connection established
```

### State Management Flow
```
Login → Authenticated User → Mode Selection → Chat Session
         (BLoC manages auth state)
                                 → Chat BLoC manages messages
                                   (send/receive via WebSocket)
```

### Error Handling Strategy
```
API Error → Failure Object → BLoC → Error State → UI Error Message
Network Error → Failure Object → BLoC → Error State → Retry Option
Validation Error → Failure Object → UI Shows Validation Error
```

---

## Next Steps

1. ✅ Create Flutter project with proper structure
2. ✅ Setup dependency injection
3. ✅ Create core infrastructure (errors, network, utils)
4. ✅ Implement auth feature
5. ✅ Implement chat feature
6. ✅ Test with backend
7. ✅ Polish UI & add animations

---

## References

- [BLoC Pattern Documentation](https://bloclibrary.dev)
- [Clean Architecture in Flutter](https://resocoder.com/flutter-clean-architecture)
- [WebSocket in Flutter](https://pub.dev/packages/web_socket_channel)
- [SQLite in Flutter](https://pub.dev/packages/sqflite)

---

**Document Version:** 1.0  
**Last Updated:** February 5, 2026  
**Status:** Ready for Implementation
