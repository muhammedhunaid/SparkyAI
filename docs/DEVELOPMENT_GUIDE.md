# SparkyAI Development Guide

## Getting Started

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Chrome/Chromium browser
- Google Cloud Project (for Gemini API)
- Firebase Project (for Firestore)
- Qdrant Vector Database

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/ashworks1706/SparkyAI.git
cd SparkyAI
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp config/__sample__appConfig.json config/appConfig.json
cp config/sample__firebase_secret.json config/firebase_secret.json
```

4. **Update configuration files**
- `config/appConfig.json`: Add API keys, Discord tokens, etc.
- `config/firebase_secret.json`: Add Firebase service account credentials

5. **Start services**
```bash
docker-compose up -d  # Start Qdrant and other services
```

6. **Run the application**
```bash
python main.py  # Start the main application
python discord_bot.py  # Start the Discord bot (separate terminal)
```

## Development Environment Setup

### Docker Development
The project includes a dev container configuration for consistent development:

```bash
# Build and run in dev container
docker-compose -f docker-compose.dev.yml up --build
```

### Local Development
For local development without Docker:

1. **Install Chrome/Chromium**
   - Ubuntu: `sudo apt-get install google-chrome-stable`
   - macOS: Download from Google Chrome website
   - Windows: Download from Google Chrome website

2. **Install ChromeDriver**
```bash
# Auto-managed by webdriver-manager in the code
# No manual installation required
```

3. **Environment Variables**
```bash
export GOOGLE_APPLICATION_CREDENTIALS="config/firebase_secret.json"
export GEMINI_API_KEY="your_gemini_api_key"
export DISCORD_BOT_TOKEN="your_discord_bot_token"
```

## Project Structure

```
SparkyAI/
├── agents/                     # AI agent implementations
│   ├── campus_agent.py
│   ├── courses_agent.py
│   ├── discord_agent.py
│   ├── library_agent.py
│   ├── news_media_agent.py
│   ├── scholarship_agent.py
│   ├── shuttle_status_agent.py
│   ├── sports_agent.py
│   ├── student_clubs_events_agent.py
│   ├── student_jobs_agent.py
│   └── superior_agent.py
├── agent_tools/               # Agent tool implementations
│   ├── campus_agent_tools.py
│   ├── courses_agent_tools.py
│   ├── discord_agent_tools.py
│   ├── library_agent_tools.py
│   ├── news_media_agent_tools.py
│   ├── scholarship_agent_tools.py
│   ├── shuttle_status_agent_tools.py
│   ├── sports_agent_tools.py
│   ├── student_clubs_events_tools.py
│   ├── student_jobs_agent_tools.py
│   └── superior_agent_tools.py
├── background/                # Background data fetching
│   ├── clubs.py
│   ├── courses_catalog.py
│   ├── events.py
│   ├── library_catalog.py
│   ├── news.py
│   ├── scholarships_goglobal.py
│   ├── scholarships_onsa.py
│   ├── shuttles.py
│   ├── social_media_facebook.py
│   ├── social_media_instagram.py
│   ├── social_media_x.py
│   └── study_rooms.py
├── config/                    # Configuration files
│   ├── app_config.py
│   ├── bot_config.py
│   └── sample configs/
├── database/                  # Database integration
│   └── middleware.py
├── docs/                      # Documentation
├── finetune/                  # Model fine-tuning datasets
├── rag/                       # RAG system components
│   ├── agents.py
│   ├── data_processor.py
│   ├── group_chat.py
│   ├── raptor.py
│   ├── vector_store.py
│   └── web_scrape.py
├── scripts/                   # Utility scripts
├── tests/                     # Test files and images
├── utils/                     # Utility modules
│   ├── common_imports.py
│   ├── login_modal.py
│   ├── otp_verification.py
│   └── utils.py
├── main.py                    # Main application entry point
├── discord_bot.py            # Discord bot implementation
├── background_fetch.py       # Background data collection
└── requirements.txt          # Python dependencies
```

## Configuration Management

### App Configuration (`config/app_config.py`)
Centralized configuration management with the following sections:

- **API Keys**: Gemini AI, Discord, Firebase
- **Agent Instructions**: System prompts for each agent
- **Database Settings**: Qdrant connection details
- **Discord Settings**: Guild IDs, channel IDs, role IDs
- **Web Scraping Settings**: Timeouts, retry counts, selectors

### Firebase Configuration
Store Firebase service account credentials in `config/firebase_secret.json`:
```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "key-id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "firebase-adminsdk-xxx@your-project.iam.gserviceaccount.com",
  "client_id": "client-id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}
```

## Adding New Agents

### 1. Create Agent Class
Create a new agent file in `agents/` directory:

```python
from utils.common_imports import *

class NewAgentModel:
    def __init__(self, middleware, genai, app_config, logger, agent_tools):
        self.logger = logger
        self.agent_tools = agent_tools
        self.middleware = middleware
        self.app_config = app_config
        
        # Initialize Gemini model with tools
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": 0.0,
                "top_p": 0.1,
                "top_k": 40,
                "max_output_tokens": 2500,
            },
            system_instruction=f"{self.app_config.get_new_agent_instruction()}",
            tools=[
                genai.protos.Tool(
                    function_declarations=[
                        genai.protos.FunctionDeclaration(
                            name="new_function",
                            description="Description of the function",
                            parameters=content.Schema(
                                type=content.Type.OBJECT,
                                properties={
                                    "param1": content.Schema(
                                        type=content.Type.STRING,
                                        description="Parameter description"
                                    )
                                },
                                required=["param1"]
                            )
                        )
                    ]
                )
            ],
            tool_config={'function_calling_config': 'ANY'}
        )

    async def determine_action(self, instruction: str, special_instructions: str) -> str:
        # Implementation here
        pass
```

### 2. Create Agent Tools
Create corresponding tools file in `agent_tools/` directory:

```python
from utils.common_imports import *

class New_Agent_Tools:
    def __init__(self, middleware, utils, logger):
        self.middleware = middleware
        self.utils = utils
        self.logger = logger

    async def new_function(self, param1: str) -> str:
        # Tool implementation here
        result = await self.utils.perform_web_search(
            search_url="https://example.asu.edu",
            optional_query={"query": param1},
            doc_title="New Function Result",
            doc_category="new_category"
        )
        return result
```

### 3. Register Agent
Add the new agent to `rag/agents.py`:

```python
from agents.new_agent import NewAgentModel
from agent_tools.new_agent_tools import New_Agent_Tools

class Agents:
    def __init__(self, ...):
        # ... existing code ...
        
        self.new_agent_tools = New_Agent_Tools(middleware, utils, logger)
        self.new_agent = NewAgentModel(middleware, genai, app_config, logger, self.new_agent_tools)
        
        # Update superior agent tools to include new agent
        self.superior_agent_tools = Superior_Agent_Tools(
            # ... existing parameters ...
            self.new_agent,  # Add new agent here
            logger, self.group_chat
        )
```

### 4. Add to Superior Agent
Update `agent_tools/superior_agent_tools.py`:

```python
async def access_new_agent(self, instruction_to_agent: str, special_instructions: str):
    """Access the new agent functionality."""
    try:
        response = await self.new_agent.determine_action(instruction_to_agent, special_instructions)
        return response
    except Exception as e:
        self.logger.error(f"@superior_agent_tools.py Error in new agent: {str(e)}")
        return "Error occurred while processing new agent request."
```

## Web Scraping Development

### Adding New Scrapers
To add support for a new ASU platform:

1. **Add URL detection** in `ASUWebScraper.engine_search()`:
```python
if 'new-platform.asu.edu' in search_url:
    results = await self.scrape_new_platform(url=url, query=optional_query)
```

2. **Implement scraper method**:
```python
async def scrape_new_platform(self, url, query) -> List[Dict[str, str]]:
    """Scrape content from new ASU platform"""
    try:
        self.driver.get(url)
        # Wait for page load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        # Extract content
        elements = self.driver.find_elements(By.CSS_SELECTOR, '.content-selector')
        results = []
        
        for element in elements:
            content = element.text.strip()
            if content:
                results.append({
                    'content': content,
                    'metadata': {
                        'url': url,
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                })
        
        return results
        
    except Exception as e:
        self.logger.error(f"Error scraping new platform: {str(e)}")
        return []
```

### Handling Dynamic Content
For JavaScript-heavy pages:

```python
# Wait for JavaScript to load content
WebDriverWait(self.driver, 30).until(
    EC.presence_of_element_located((By.CLASS_NAME, "dynamic-content"))
)

# Handle infinite scroll
self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
time.sleep(3)

# Handle AJAX loading
WebDriverWait(self.driver, 10).until_not(
    EC.presence_of_element_located((By.CLASS_NAME, "loading-spinner"))
)
```

## Database Operations

### Adding New Collections
To add support for new Firestore collections:

```python
# In middleware.py
async def create_new_collection_document(self, data: dict) -> str:
    """Create document in new collection"""
    try:
        collection_ref = self.db.collection("new_collection")
        doc_ref = await collection_ref.add(data)
        return doc_ref.id
    except Exception as e:
        self.logger.error(f"Error creating document: {str(e)}")
        return None
```

### Vector Store Operations
Adding documents to vector database:

```python
# Process and store documents
processed_docs = await data_processor.process_documents(
    documents=scraped_data,
    search_context="Context for processing",
    title="Document Title",
    category="document_category"
)

# Store in vector database
success = await vector_store.store_documents(processed_docs)
```

## Testing

### Unit Tests
Create tests in `tests/` directory:

```python
import unittest
from agents.new_agent import NewAgentModel

class TestNewAgent(unittest.TestCase):
    def setUp(self):
        # Initialize test environment
        pass
        
    async def test_new_function(self):
        # Test implementation
        pass

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests
Test complete workflows:

```python
async def test_full_workflow():
    """Test complete query processing workflow"""
    agents = Agents(...)
    response = await agents.process_question("Test question")
    assert response is not None
    assert len(response) > 0
```

## Performance Optimization

### Caching Strategies
Implement caching for frequently accessed data:

```python
from functools import lru_cache
import asyncio

@lru_cache(maxsize=100)
async def cached_web_search(url: str, query: str) -> str:
    # Cached implementation
    return await perform_expensive_operation(url, query)
```

### Database Optimization
- Use appropriate indexes in Firestore
- Implement batch operations for bulk updates
- Use connection pooling for database connections

### Memory Management
- Implement proper cleanup for Selenium drivers
- Use context managers for resource management
- Monitor memory usage in long-running operations

## Monitoring and Debugging

### Logging Configuration
Configure detailed logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/application.log'),
        logging.StreamHandler()
    ]
)
```

### Error Monitoring
Implement comprehensive error tracking:

```python
try:
    # Operation
    pass
except Exception as e:
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
    # Send to monitoring service if configured
```

## Deployment

### Production Deployment
1. **Environment Variables**: Set all required environment variables
2. **Database Setup**: Configure production Firestore and Qdrant instances
3. **Monitoring**: Set up application monitoring and alerting
4. **Scaling**: Configure auto-scaling for high-traffic scenarios

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Chrome for Selenium
RUN apt-get update && apt-get install -y \
    google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

COPY . .
CMD ["python", "main.py"]
```

## Contributing Guidelines

1. **Code Style**: Follow PEP 8 guidelines
2. **Documentation**: Update documentation for new features
3. **Testing**: Include tests for new functionality
4. **Error Handling**: Implement comprehensive error handling
5. **Logging**: Add appropriate logging statements
6. **Performance**: Consider performance impact of changes

## Troubleshooting

### Common Issues

1. **ChromeDriver Version Mismatch**
   - Solution: Update Chrome browser or let webdriver-manager handle it

2. **Firebase Permission Errors**
   - Solution: Verify service account has appropriate permissions

3. **Discord Rate Limiting**
   - Solution: Implement proper rate limiting and retry logic

4. **Vector Database Connection Issues**
   - Solution: Check Qdrant service status and connection parameters

5. **Memory Issues with Large Documents**
   - Solution: Implement document chunking and batch processing