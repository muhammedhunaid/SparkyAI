# SparkyAI API Documentation

## Overview
SparkyAI is a comprehensive Discord bot designed to assist Arizona State University students with access to resources including news, events, scholarships, courses, and more. The system uses a sophisticated agent-based architecture with Retrieval-Augmented Generation (RAG) capabilities.

## Agent System Architecture

SparkyAI is built on a multi-agent architecture where specialized agents handle different aspects of Arizona State University student services. The system uses a hierarchical approach with a superior agent that coordinates other specialized agents.

### Core Components

- **Superior Agent**: Master coordinator that routes queries to appropriate specialized agents
- **Specialized Agents**: Domain-specific agents for courses, clubs, events, scholarships, etc.
- **Agent Tools**: Utility functions that agents use to perform specific tasks
- **RAG System**: Retrieval-Augmented Generation for intelligent document search and response

## RAG System Components

The Retrieval-Augmented Generation (RAG) system is the backbone of SparkyAI's intelligent responses. It consists of several key components:

### Vector Store
- **Purpose**: Stores document embeddings for semantic search
- **Technology**: Qdrant vector database
- **Features**: Similarity search, filtering, metadata storage

### Data Processor
- **Purpose**: Processes and chunks documents for optimal retrieval
- **Features**: 
  - Content-aware chunking
  - Async batch processing
  - Performance caching with TTL
  - Enhanced text cleaning
  - Semantic and paragraph-based chunking strategies

### RAPTOR Retriever
- **Purpose**: Hierarchical document retrieval using tree structures
- **Features**:
  - Multi-level clustering
  - Performance metrics tracking
  - Query caching with TTL
  - Priority queue processing
  - Similarity-based ranking

## Web Scraping Engine

The web scraping engine handles data collection from various ASU platforms:

### SunDevilSync Integration (Legacy)
- Student organization data
- Event information
- Club details and membership

### SunDevilCentral Integration (New Platform)
```python
def scrape_sundevil_central(self, base_url="https://sundevilcentral.asu.edu", max_pages=5):
    """
    Scrape organizations and events from SunDevilCentral platform
    
    Args:
        base_url: Base URL for SunDevilCentral
        max_pages: Maximum pages to scrape
        
    Returns:
        Dict containing organizations and events data
    """
```

### Multi-Platform Support
- Automatic platform detection
- Fallback mechanisms
- Data normalization across platforms

## Architecture Overview

### Core Components

1. **Agents System**: Multi-agent architecture with specialized agents for different ASU resources
2. **RAG Pipeline**: Advanced retrieval system with RAPTOR tree structure and similarity search
3. **Web Scraping**: Selenium-based scraping for dynamic ASU platforms
4. **Vector Database**: Qdrant-based vector storage for semantic search
5. **Data Processing**: Multi-stage document processing with AI-powered summarization

## Agent System

### Superior Agent (`SuperiorModel`)
The main orchestration agent that determines which specialized agent to use.

**Key Methods:**
- `determine_action(instruction: str) -> str`: Routes queries to appropriate agents
- `access_*_agent(instruction: str, special_instructions: str)`: Access methods for each specialized agent

## Agent Tools

### Campus Agent Tools
- Campus map navigation
- Building information
- Parking and transportation

### Courses Agent Tools  
- Course catalog search
- Schedule information
- Prerequisites and requirements

### Student Clubs Events Tools
- Organization discovery
- Event listings
- Dual platform support (SunDevilSync/SunDevilCentral)

### Scholarship Agent Tools
- Scholarship search and matching
- Application requirements
- Deadline tracking

### Library Agent Tools
- Study room availability
- Resource search
- Library hours and services

### Sports Agent Tools
- Game schedules
- Team information
- Athletic events

### News Media Agent Tools
- University news
- Social media updates
- Announcements

### Specialized Agents

#### 1. Shuttle Status Agent (`Shuttle_Status_Model`)
Handles ASU campus shuttle information.

**Tools:**
- `get_shuttle_status(route: str, location: str) -> str`

**Supported Routes:**
- Tempe-Downtown
- Tempe-West  
- Mercado
- Polytechnic

#### 2. Discord Agent (`DiscordModel`)
Manages Discord server interactions.

**Tools:**
- `create_announcement(title: str, content: str, channel: str) -> str`
- `create_poll(question: str, options: list, channel: str) -> str`
- `get_user_roles(user_id: str) -> str`

#### 3. Courses Agent (`CoursesModel`)
Provides course catalog information.

**Tools:**
- `search_courses(query: str, campus: str, subject: str) -> str`

**Supported Parameters:**
- Campus: Tempe, Downtown, West, Polytechnic, Online
- Subject: All ASU subjects (CS, MAT, ENG, etc.)

#### 4. Library Agent (`LibraryModel`)
Access to ASU library resources.

**Tools:**
- `get_library_hours(library: str, date: str) -> str`
- `search_library_catalog(query: str) -> str`
- `get_study_room_availability(library: str, date: str) -> str`

**Supported Libraries:**
- Hayden Library (Tempe)
- Noble Library (Tempe)
- Fletcher Library (West)
- Downtown Library
- Polytechnic Library

#### 5. News Media Agent (`NewsMediaModel`)
ASU news and social media content.

**Tools:**
- `search_news(query: str, campus: str) -> str`
- `get_social_media_updates(account: str, query: str) -> str`

**Supported Social Media Accounts:**
- @ArizonaState
- @SunDevilAthletics  
- @SparkySunDevil
- @ASUFootball
- @ASUAlumni

#### 6. Scholarship Agent (`ScholarshipModel`)
Scholarship search and information.

**Tools:**
- `search_scholarships(query: str, filters: dict) -> str`

**Supported Filters:**
- Academic Level
- Citizenship Status
- GPA Requirements
- College/School

#### 7. Sports Agent (`SportsModel`)
ASU athletics information.

**Tools:**
- `get_sports_schedule(sport: str, date: str) -> str`
- `get_ticket_info(sport: str, game_date: str) -> str`

#### 8. Student Clubs Events Agent (`StudentClubsEventsModel`)
Student organizations and events (SunDevilSync).

**Tools:**
- `get_club_information(query: str, category: list, campus: list) -> str`
- `get_event_updates(query: str, category: list, campus: list) -> str`

**Organization Categories:**
- Academic, Barrett, Creative/Performing Arts, Cultural/Ethnic
- Professional, Religious/Faith/Spiritual, Service, Sports/Recreation
- Technology, International, LGBTQIA+, and more

**Event Categories:**
- ASU Sync, Club Meetings, Community Service, Cultural
- Career Development, Graduate, International, Social

#### 9. Student Jobs Agent (`StudentJobsModel`)
ASU Workday job search.

**Tools:**
- `get_student_jobs(keyword: str, max_results: int) -> str`

#### 10. Campus Agent (`CampusAgentModel`)
Campus locations and maps.

**Tools:**
- `get_campus_location(keyword: str) -> str`

## RAG System

### Vector Store (`VectorStore`)
Manages document storage and retrieval using Qdrant.

**Key Methods:**
- `similarity_search(query: str, k: int, categories: list) -> List[Document]`
- `store_documents(documents: List[Document]) -> bool`
- `store_to_vector_db() -> bool`

### RAPTOR Retriever (`RaptorRetriever`)
Advanced hierarchical document retrieval system.

**Key Methods:**
- `retrieve(query: str, top_k: int) -> List[Document]`
- `build_raptor_tree() -> dict`
- `update_raptor_tree() -> bool`
- `rerank_results(query: str, results: List, top_k: int) -> List[Document]`

### Data Processor (`DataPreprocessor`)
Document processing and summarization.

**Key Methods:**
- `process_documents(documents: List[Dict], search_context: str) -> List[Document]`
- `clean_and_structure_text(text: str) -> str`

**Processing Pipeline:**
1. Text cleaning and normalization
2. AI-powered summarization and refinement
3. Semantic chunking with overlap
4. Metadata annotation
5. Vector embedding generation

## Web Scraping System

### ASU Web Scraper (`ASUWebScraper`)
Selenium-based scraping for ASU platforms.

**Key Methods:**
- `engine_search(search_url: str, optional_query: str) -> List[Dict]`
- `scrape_static_content(url: str) -> bool`
- `login_user_credentials(user_id: str, asurite: str, password: str) -> WebDriver`

**Supported Platforms:**
- asu.campuslabs.com (SunDevilSync)
- catalog.apps.asu.edu (Course Catalog)
- lib.asu.edu (Library Hours)
- search.lib.asu.edu (Library Catalog)
- asu-shuttles.rider.peaktransit.com (Shuttle Status)
- myworkday.com/asu (Student Jobs)
- sundevils.com/tickets (Sports Tickets)
- goglobal.asu.edu & onsa.asu.edu (Scholarships)

## Database Integration

### Middleware (`Middleware`)
Firestore database integration and state management.

**Key Methods:**
- `push_message() -> str`: Store conversation messages
- `check_user_session_timeout(user_id: str) -> bool`
- `login_user_session_credentials(user_id: str, asurite: str, driver: WebDriver)`

## Utility Classes

### Utils (`Utils`)
Core utility functions for search and data management.

**Key Methods:**
- `perform_web_search(url: str, query: str, title: str, category: str) -> str`
- `perform_database_search(query: str, categories: list) -> List[Document]`
- `perform_similarity_search(query: str, categories: list) -> List[Document]`
- `merge_search_results(raptor_results: List, similarity_results: List) -> List[Dict]`

### Group Chat (`GroupChat`)
Multi-agent conversation management for complex queries.

## Configuration

### App Config (`AppConfig`)
Centralized configuration management.

**Key Methods:**
- `get_*_agent_instruction()`: Agent system instructions
- `get_*_agent_prompt()`: Agent prompts
- `get_api_key()`: API keys and credentials

## Error Handling

The system implements comprehensive error handling:

1. **Retry Mechanisms**: Multiple attempts for web scraping and API calls
2. **Fallback Systems**: Graceful degradation when services are unavailable
3. **Logging**: Detailed logging throughout all components
4. **Timeout Management**: Configurable timeouts for all operations

## Rate Limiting

- Discord API: Respects Discord rate limits
- Web Scraping: Implements delays between requests
- AI Models: Request throttling for Gemini API

## Security

- **Authentication**: ASUrite integration for user verification
- **Session Management**: Secure browser session handling
- **Data Privacy**: User data protection and session cleanup
- **Input Validation**: Comprehensive input sanitization

## Performance Optimizations

1. **Caching**: Query result caching and document ID caching
2. **Connection Pooling**: Efficient database connections
3. **Batch Processing**: Bulk operations for database updates
4. **Lazy Loading**: On-demand component initialization

## Integration Examples

### Basic Query Processing
```python
# Initialize agents
agents = Agents(vector_store, asu_data_processor, middleware, genai, utils, app_config, logger, group_chat)

# Process user question
response = await agents.process_question("What clubs are available for computer science students?")
```

### Direct Agent Access
```python
# Access specific agent
clubs_response = await agents.student_clubs_events_agent.determine_action(
    "Find computer science clubs", 
    "Focus on technical and academic organizations"
)
```

### Custom Web Scraping
```python
# Custom web search
result = await utils.perform_web_search(
    search_url="https://asu.campuslabs.com/engage/organizations",
    optional_query={"category": ["Technology", "Academic"]},
    doc_title="CS Organizations",
    doc_category="clubs_info"
)
```

## Monitoring and Logging

The system provides comprehensive logging across all components:

- **Agent Operations**: Detailed agent execution logs
- **Web Scraping**: Request/response logging with error tracking
- **Database Operations**: Query performance and error logging
- **User Interactions**: Conversation flow and response times

## Future Extensibility

The architecture supports easy extension:

1. **New Agents**: Add specialized agents for new ASU resources
2. **Additional Platforms**: Extend web scraping to new ASU systems
3. **Enhanced AI**: Integrate additional AI models and capabilities
4. **Mobile Support**: API endpoints for mobile applications