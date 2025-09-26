# Weapons Trade Detection System - Project Overview

## Project Description
This is an **academic research system** designed to detect illegal weapons trade patterns in text content. The system uses natural language processing and pattern recognition to identify suspicious communication patterns that may indicate illegal weapons trading activities. The system also includes a **synthetic content generation module** for creating research datasets and testing detection algorithms, along with a **professional sidebar navigation interface**.

## Architecture Overview
The system follows a **full-stack architecture** with:
- **Backend**: Python FastAPI server providing REST API endpoints
- **Frontend**: React.js web application with professional sidebar navigation
- **Analysis Engine**: Lightweight rule-based text analysis module for weapons detection
- **Content Generator**: Synthetic content generation for academic research
- **User Interface**: Multi-section dashboard with navigation sidebar

## Project Structure

```
weapons-trade-detection-system/
├── backend/                    # Python FastAPI backend
│   ├── src/
│   │   ├── server.py          # Main FastAPI application
│   │   ├── detection/
│   │   │   └── text_analyzer.py  # Lightweight analysis engine
│   │   ├── generation/        # Content generation module
│   │   │   ├── __init__.py
│   │   │   └── content_generator.py  # Enhanced content generation
│   │   └── models/
│   │       └── detection.py   # Pydantic data models
│   ├── requirements.txt       # Python dependencies
│   └── venv/                  # Virtual environment
├── frontend/                   # React.js frontend with sidebar navigation
│   ├── src/
│   │   ├── App.js            # Main React app with sidebar integration
│   │   ├── App.css           # Updated styling
│   │   └── components/
│   │       ├── DetectionForm.js      # Analysis form component
│   │       ├── ContentPlayground.js  # Enhanced content generation UI
│   │       ├── Sidebar.js           # Professional navigation sidebar
│   │       ├── Dashboard.js         # System dashboard with stats
│   │       └── PlaceholderComponents.js  # Future feature placeholders
│   └── package.json          # Node.js dependencies
└── claude.md                 # This updated documentation file
```

## Recent Major Updates

### Version 2.1 Updates (Current)

#### Backend Improvements
- **Lightweight Analysis Engine**: Replaced heavy AI models with fast rule-based detection to improve startup time from 30+ seconds to 2-3 seconds
- **Enhanced Vocabulary**: Added comprehensive weapons terminology including military designations (M16, M4, AK47, etc.), ammunition calibers, and slang terms
- **Improved Content Generator**: Enhanced synthetic content generation with realistic variations, contact information, pricing patterns, and metadata simulation
- **API Optimization**: Streamlined FastAPI server with cleaned imports and better error handling
- **Reddit Integration**: Added comprehensive Reddit data collection capabilities for academic research
- **Configuration Management**: Added proper configuration system with environment variable support

#### Frontend Revolution
- **Professional Sidebar Navigation**: Added comprehensive sidebar with 6 main sections for product-like experience
- **Dashboard Component**: New overview page with statistics, recent activity, and system status
- **Improved Visual Design**: Enhanced contrast and readability with better color schemes and typography
- **Modular Architecture**: Separated functionality into distinct components for better maintainability
- **Reddit Collector Interface**: Added professional Reddit data collection interface with configuration management

#### User Experience Enhancements
- **Multi-Section Interface**: Organized features into logical sections (Dashboard, Analysis, Playground, Reddit Collection, etc.)
- **Better Content Visibility**: Fixed contrast issues in Content Playground for improved readability
- **Professional Layout**: Transformed from simple testing tool to professional research platform
- **Connection Status Handling**: Improved backend connection status display and error handling
- **Data Collection Tools**: Added comprehensive Reddit data collection and analysis capabilities

## Backend Components

### 1. FastAPI Server (`backend/src/server.py`)
**Purpose**: Main API server providing REST endpoints for the detection system.

**Recent Updates**:
- Cleaned up duplicate imports and initializations
- Streamlined endpoint organization
- Improved error handling and response formatting
- Added comprehensive content generation endpoints

**Key Features**:
- CORS middleware for frontend communication
- Health check endpoint (`/health`)
- API information endpoint (`/api`)
- Content analysis endpoint (`/api/detection/analyze`)
- Content generation endpoints for synthetic data creation
- Batch content generation capabilities

**Endpoints**:
- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check with system status
- `GET /api` - API information and available endpoints
- `GET /api/test` - API test endpoint
- `POST /api/detection/analyze` - Main analysis endpoint
- `POST /api/generation/content` - Generate synthetic content
- `POST /api/generation/batch` - Generate batch content across all types
- `GET /api/generation/templates` - Get available templates and vocabulary
- `POST /api/reddit/collect` - Collect Reddit data for research
- `GET /api/reddit/config-status` - Check Reddit API configuration
- `GET /api/reddit/status` - Check Reddit collector availability
- `GET /api/reddit/files` - List collected data files
- `GET /api/reddit/requirements` - Get setup requirements and instructions

**Configuration**:
- Host: `0.0.0.0`
- Port: `9000`
- Auto-reload enabled for development
- Optimized startup time with lightweight analyzer

### 2. Lightweight Text Analyzer (`backend/src/detection/text_analyzer.py`)
**Purpose**: Fast rule-based analysis engine optimized for quick startup and accurate detection.

**Major Updates**:
- **Performance Optimization**: Removed heavy AI models (RoBERTa, BERT) that caused 30+ second startup times
- **Enhanced Vocabulary**: Comprehensive weapons terminology including:
  - Military weapons: M16, M4, M249, AK47, AR15, UZI, MP5, SCAR, etc.
  - Ammunition types: 9mm, .45, .40, .223, .308, 5.56, 7.62, etc.
  - Weapon slang: heat, strap, burner, choppa, stick, iron, tool, etc.
  - Weapon parts: barrel, trigger, stock, magazine, scope, silencer, etc.
- **Aggressive Detection Logic**: Ensures any weapons-related content is flagged as HIGH risk
- **Pattern Recognition**: Enhanced regex patterns for suspicious communication
- **Text Normalization**: Improved text cleaning and preprocessing

**Analysis Categories**:
- **Firearms**: Comprehensive list of weapons, brands, models, and slang
- **Explosives**: Bombs, grenades, military explosives, and components
- **Violence**: Threatening language and violent intent indicators
- **Illegal Terms**: Black market, trafficking, and suspicious transaction terms

**Scoring Algorithm**:
- Each keyword adds 40% risk score
- Each pattern match adds 50% risk score
- Minimum 70% risk for any weapons content
- Minimum 80% risk for direct weapon mentions
- Combination bonuses for weapons + violence or weapons + transaction intent

**Output Structure**:
```python
{
    'risk_score': float,        # 0.0 to 1.0 risk assessment (optimized for HIGH detection)
    'confidence': float,        # Analysis confidence level (0.9 default)
    'flags': List[str],         # Detailed detection flags with categories
    'detected_keywords': List[str],  # Found keywords by category
    'detected_patterns': List[str],  # Matched regex patterns
    'analysis_time': str        # ISO timestamp
}
```

### 3. Enhanced Content Generator (`backend/src/generation/content_generator.py`)
**Purpose**: Advanced synthetic content generation engine for comprehensive academic research datasets.

**New Features**:
- **Realistic Variations**: Adds typos, abbreviations, and platform-specific language
- **Contact Information Generation**: Synthetic phone numbers, emails, usernames
- **Pricing Patterns**: Realistic pricing with various formats and ranges
- **Metadata Simulation**: Timestamps, platforms, locations, user IDs
- **Content Variations**: Platform-specific tone and style adjustments
- **Batch Processing**: Generate multiple content types simultaneously

**Content Types**:
- **Posts**: Social media style content with casual tone
- **Messages**: Direct message style with personal/secretive tone
- **Ads**: Classified ad style with business/transaction tone
- **Forum**: Discussion forum style with community tone

**Intensity Levels** (Updated):
- **Low**: Sporting goods, collectibles, antiques (legitimate items)
- **Medium**: Tactical gear, survival equipment, protection items
- **High**: Direct weapons references, ammunition, illegal terms

**Generation Parameters**:
```python
@dataclass
class ContentParameters:
    content_type: str     # 'post', 'message', 'ad', 'forum'
    intensity_level: str  # 'low', 'medium', 'high'
    language: str = 'en'
    include_contact: bool = False
    include_pricing: bool = False
    quantity: int = 1
```

**Enhanced Output Structure**:
```python
{
    'id': str,              # Unique synthetic ID
    'content': str,         # Generated content with research disclaimer
    'parameters': dict,     # Generation parameters used
    'metadata': {
        'timestamp': str,   # Synthetic timestamp
        'platform': str,    # Platform simulation
        'location': str,    # Location code
        'user_id': str,     # Synthetic user ID
        'post_id': str      # Synthetic post ID
    },
    'contact_info': dict,   # Optional contact information
    'pricing': str,         # Optional pricing information
    'generated_at': str     # Actual generation timestamp
}
```

### 4. Reddit Data Collector (`backend/src/reddit/reddit_collector.py`)
**Purpose**: Academic Reddit data collection system for research purposes.

**Key Features**:
- **Academic Compliance**: Designed for academic research with proper data handling
- **Privacy Protection**: Usernames are hashed for privacy protection
- **Rate Limiting**: Respectful API usage with configurable delays
- **Data Analysis**: Automatic analysis of collected posts using the detection engine
- **Multiple Formats**: Save data in JSON and CSV formats
- **Keyword Search**: Search for specific keywords across subreddits
- **Time Filtering**: Collect posts from different time periods (day, week, month, year, all)

**Collection Methods**:
- **Subreddit Collection**: Collect posts from specific subreddits
- **Keyword Search**: Search for posts containing specific keywords
- **Time-based Filtering**: Filter posts by time period
- **Sort Methods**: Sort by hot, new, top, controversial

**Data Storage**:
- Raw posts saved in JSON and CSV formats
- Analyzed posts with risk scores and flags
- Organized file structure with timestamps
- Privacy-compliant data handling

### 5. Configuration System (`backend/config.py`)
**Purpose**: Centralized configuration management with environment variable support.

**Key Features**:
- **Environment Variables**: Support for .env file configuration
- **Reddit API Configuration**: Secure credential management
- **Application Settings**: Host, port, debug mode configuration
- **Data Directory Management**: Configurable data storage locations
- **Validation**: Configuration validation and missing item detection

**Configuration Classes**:
- `RedditConfig`: Reddit API credentials and settings
- `AppConfig`: General application configuration
- Environment variable loading with defaults

## Frontend Components Revolution

### 1. Professional App Layout (`frontend/src/App.js`)
**Purpose**: Main application with professional sidebar navigation and section management.

**Major Updates**:
- **Sidebar Integration**: Added professional navigation sidebar
- **Section Management**: Route between different application sections
- **Connection Handling**: Improved backend connection status display
- **Layout Optimization**: Professional multi-panel layout with proper spacing
- **State Management**: Centralized active tab and connection state management

**New Features**:
- Professional connection status screen when backend is disconnected
- Floating API test button for quick connectivity testing
- Seamless navigation between sections
- Responsive layout that adapts to sidebar presence

**State Management**:
```javascript
const [activeTab, setActiveTab] = useState('dashboard');
const [backendStatus, setBackendStatus] = useState('Connecting...');
const [healthData, setHealthData] = useState(null);
const [isConnected, setIsConnected] = useState(false);
```

### 2. Professional Sidebar Navigation (`frontend/src/components/Sidebar.js`)
**Purpose**: Professional navigation sidebar providing access to all system sections.

**Features**:
- **Visual Design**: Dark theme with professional styling and hover effects
- **Active State Indication**: Clear visual feedback for current section
- **Icon Integration**: Emoji icons for visual section identification
- **System Status**: Displays backend connection and version information
- **Responsive Design**: Fixed positioning with proper z-index management

**Navigation Sections**:
1. **Dashboard** (📊) - System overview and statistics
2. **Content Analysis** (🔍) - Text analysis and detection
3. **Content Playground** (🎮) - Synthetic content generation and testing
4. **Datasets** (📁) - Research dataset management (placeholder)
5. **Reports** (📈) - Analysis reports and metrics (placeholder)
6. **Settings** (⚙️) - System configuration (placeholder)

### 3. System Dashboard (`frontend/src/components/Dashboard.js`)
**Purpose**: Professional overview dashboard with system statistics and recent activity.

**Features**:
- **Statistics Cards**: Total analyses, high-risk detections, generated content
- **Recent Activity Feed**: Live activity log with color-coded risk levels
- **Visual Indicators**: Professional card layout with proper typography
- **Data Visualization**: Prepared for future integration with real analytics

**Dashboard Metrics** (Simulated):
- Total Analyses: 1,247 (+12% from last week)
- High Risk Detected: 89 (7.1% of total analyses)
- Generated Content: 2,456 (For research testing)

### 4. Enhanced Content Playground (`frontend/src/components/ContentPlayground.js`)
**Purpose**: Advanced interface for synthetic content generation with improved usability.

**Major Updates**:
- **Improved Contrast**: Fixed text visibility issues with better color schemes
- **Enhanced Typography**: Bold labels and better font weights for readability
- **Professional Styling**: Updated intensity badges with better contrast
- **Content Display**: Improved content boxes with borders and better spacing
- **Analysis Integration**: Seamless integration with detection analysis

**Visual Improvements**:
- Content text: Dark gray (#1f2937) with border for better definition
- Metadata text: Darker gray (#374151) with bold labels
- Intensity badges: Higher contrast colors with bold text
- Type badges: Better contrast and visual hierarchy

**Generation Controls**:
- Content type dropdown (post, message, ad, forum)
- Intensity selector (low, medium, high) with descriptive labels
- Quantity input (1-50 items)
- Language selection (currently English)
- Optional contact information inclusion checkbox
- Optional pricing information inclusion checkbox

**Analysis Integration**:
- Real-time analysis of generated content
- Risk scores and flags displayed alongside generated content
- Color-coded risk level indicators
- Summary statistics for batch analysis

### 5. Reddit Data Collector (`frontend/src/components/RedditCollector.js`)
**Purpose**: Professional interface for Reddit data collection and research.

**Key Features**:
- **Configuration Management**: Reddit API credentials setup and validation
- **Collection Parameters**: Subreddit selection, time filters, keyword search
- **Real-time Status**: Live collection progress and status updates
- **Data Visualization**: Collected data preview and analysis results
- **File Management**: View and download collected data files
- **Academic Compliance**: Built-in compliance reminders and data handling guidelines

**Collection Interface**:
- Subreddit input with validation
- Time filter selection (day, week, month, year, all)
- Sort method selection (hot, new, top, controversial)
- Keyword search with comma-separated terms
- Collection limit configuration (1-100 posts)
- Real-time progress indicators

**Data Management**:
- View collected files with metadata
- Download raw and analyzed data
- File size and modification time display
- Organized file listing by type (raw/analyzed)

### 6. Placeholder Components (`frontend/src/components/PlaceholderComponents.js`)
**Purpose**: Professional placeholder sections for future system expansion.

**Components**:
- **Datasets**: Research dataset management and export tools
- **Reports**: Analysis reports, performance metrics, and research insights
- **Settings**: System configuration, detection tuning, and API settings

## Technology Stack Updates

### Backend Dependencies (Updated)
- **FastAPI**: Web framework (≥0.104.1)
- **Uvicorn**: ASGI server (≥0.24.0)
- **Pydantic**: Data validation (≥2.5.0) - Updated for v2 compatibility
- **Python 3.13**: Latest Python with optimized performance
- **Removed Heavy Dependencies**: No longer requires transformers, torch, spacy, or textblob for faster startup

### Frontend Dependencies (Enhanced)
- **React**: UI library with enhanced component architecture
- **Professional CSS**: Improved styling with better contrast and typography
- **Modular Components**: Separated concerns for better maintainability

## API Integration Updates

### Enhanced Analysis Response Format
```json
{
    "analysis_id": "analysis_1234567890",
    "status": "completed",
    "risk_score": 0.80,
    "risk_level": "HIGH",
    "confidence": 0.90,
    "flags": [
        "HIGH RISK: Detected firearms keyword 'glock'",
        "HIGH RISK: Suspicious intent pattern detected: 'want to buy glock'",
        "CRITICAL: Weapon + transaction intent detected"
    ],
    "detected_keywords": ["firearms: glock"],
    "detected_patterns": ["want to buy glock"],
    "summary": "Analysis completed. Risk level: HIGH. Found 3 potential indicators.",
    "timestamp": "2024-01-01T12:00:00"
}
```

### Enhanced Content Generation Response Format
```json
{
    "status": "success",
    "generated_count": 5,
    "content": [
        {
            "id": "synthetic_726519",
            "content": "[SYNTHETIC DATA FOR ACADEMIC RESEARCH ONLY] Looking for tactical gear. Need professional-grade equipment. Text 555-123-4567",
            "parameters": {
                "type": "post",
                "intensity": "medium",
                "language": "en"
            },
            "metadata": {
                "timestamp": "2024-01-01T11:30:00",
                "platform": "Facebook",
                "location": "TX",
                "user_id": "user_12345",
                "post_id": "post_67890"
            },
            "contact_info": {
                "phone": "555-123-4567",
                "email": "user123@tempmail.com",
                "username": "user_1234",
                "app": "WhatsApp"
            },
            "pricing": "$450 OBO",
            "generated_at": "2024-01-01T12:00:00"
        }
    ],
    "parameters": {
        "content_type": "post",
        "intensity_level": "medium",
        "quantity": 5,
        "language": "en",
        "include_contact": true,
        "include_pricing": true
    },
    "timestamp": "2024-01-01T12:00:00"
}
```

## Risk Assessment Logic (Enhanced)

The updated system uses an **aggressive scoring algorithm** to ensure weapons content is properly flagged:

1. **Keyword Scoring**: Each detected keyword adds 40% to the risk score
2. **Pattern Scoring**: Each matched pattern adds 50% to the risk score
3. **Combination Bonuses**: 
   - Weapons + transaction intent: +30%
   - Weapons + violence intent: +40%
4. **Minimum Thresholds**:
   - Any weapons content: Minimum 70% risk score
   - Direct weapon mentions: Minimum 80% risk score
5. **Risk Level Classification**:
   - **HIGH**: Risk score ≥ 0.7 (most weapons content)
   - **MEDIUM**: Risk score ≥ 0.4 (tactical/borderline content)
   - **LOW**: Risk score < 0.4 (legitimate sporting goods)

## Development Setup (Updated)

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create generation module
mkdir -p src/generation
touch src/generation/__init__.py

# Start server (now starts in 2-3 seconds instead of 30+)
python src/server.py
```

### Frontend Setup
```bash
cd frontend
npm install

# Create new component files
cd src/components
touch Sidebar.js Dashboard.js PlaceholderComponents.js

# Start development server
npm start
```

## Performance Improvements

### Backend Optimizations
- **Startup Time**: Reduced from 30+ seconds to 2-3 seconds by removing heavy AI models
- **Memory Usage**: Significantly reduced memory footprint without transformer models
- **Response Time**: Faster text analysis with optimized rule-based detection
- **Code Organization**: Cleaned up imports and removed redundant initializations

### Frontend Enhancements
- **User Experience**: Professional navigation and improved visual hierarchy
- **Readability**: Fixed contrast issues and improved typography
- **Organization**: Modular component architecture for better maintainability
- **Professional Appearance**: Transformed from testing tool to product-like interface

## Security Considerations (Updated)

**Important**: This remains an **academic research system** with enhanced capabilities:

1. **No Real Data**: System processes only synthetic research data
2. **Local Development**: Configured for localhost development environment
3. **Research Context**: All analysis and generation for academic research only
4. **Data Privacy**: No persistent storage of analyzed content
5. **Academic Disclaimer**: All generated content clearly marked as synthetic research data
6. **Professional Interface**: Enhanced UI suitable for academic presentations and demonstrations

## Future Enhancements (Updated Roadmap)

### Immediate Future (Phase 3)
1. **Database Integration**: Persistent storage for generated content and analysis results
2. **Advanced Analytics**: Real dashboard statistics and performance metrics
3. **Export Functionality**: Download datasets in various formats (JSON, CSV, XML)
4. **User Authentication**: Basic user management for research teams
5. **API Key Management**: Secure API access for external integrations

### Medium Term (Phase 4)
1. **Advanced Content Generation**: 
   - Multi-language support (Spanish, French, Arabic)
   - Platform-specific variations (WhatsApp, Telegram, Discord styles)
   - Temporal pattern simulation (time-based content variations)
2. **Enhanced Analysis Engine**:
   - Machine learning model integration (optional)
   - Custom vocabulary management
   - False positive reduction algorithms
3. **Collaboration Features**:
   - Team workspaces
   - Shared datasets
   - Research project management

### Long Term (Phase 5)
1. **Advanced AI Integration**: Optional AI models for enhanced detection
2. **Image Analysis**: Visual content analysis capabilities
3. **Real-time Monitoring**: Live content stream analysis
4. **Multi-language Analysis**: Support for multiple languages
5. **Research Publication Tools**: Automated report generation for academic papers

## Academic Research Context (Enhanced)

This enhanced system now supports comprehensive academic research in:

- **Natural Language Processing**: Advanced pattern recognition and text analysis
- **Synthetic Data Generation**: Realistic dataset creation for algorithm testing
- **User Interface Design**: Professional interface design for research presentations
- **Detection Algorithm Validation**: Comprehensive testing with generated datasets
- **Human-Computer Interaction**: Professional interface for researcher interaction
- **Academic Demonstration**: Product-like interface suitable for academic presentations
- **Research Methodology**: Systematic approach to content analysis and generation

The system now provides a professional research platform suitable for academic papers, conference presentations, and research collaboration.

## Version History

### Version 2.1 (Current) - Reddit Integration & Configuration
- Added comprehensive Reddit data collection capabilities
- Implemented configuration management system
- Added Reddit collector frontend interface
- Enhanced API endpoints for data collection
- Improved error handling and configuration validation
- Added academic compliance features for data collection

### Version 2.0 - Professional Interface Update
- Added professional sidebar navigation
- Enhanced content generation capabilities
- Optimized backend performance (2-3 second startup)
- Improved visual design and contrast
- Added dashboard with statistics
- Comprehensive documentation update

### Version 1.5 - Content Generation Integration
- Added synthetic content generation
- Enhanced text analyzer with comprehensive vocabulary
- Integrated Content Playground interface
- Added batch content generation

### Version 1.0 - Initial Implementation
- Basic FastAPI backend
- Simple React frontend
- Rule-based text analysis
- Basic detection capabilities

## API Documentation

The FastAPI backend automatically generates interactive API documentation available at:
- **Swagger UI**: `http://localhost:9000/docs`
- **ReDoc**: `http://localhost:9000/redoc`

This documentation provides interactive testing capabilities for all API endpoints and reflects all recent updates and enhancements.