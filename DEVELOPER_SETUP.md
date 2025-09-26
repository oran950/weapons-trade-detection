# 🚀 Developer Setup Guide

Welcome to the Weapons Trade Detection System! This guide will help you get the project running on your local machine.

## 📋 Prerequisites

Before you start, make sure you have these installed:

- **Git** - [Download here](https://git-scm.com/downloads)
- **Python 3.8+** - [Download here](https://www.python.org/downloads/)
- **Node.js 16+** - [Download here](https://nodejs.org/)
- **Docker Desktop** - [Download here](https://www.docker.com/products/docker-desktop/)

## 🏁 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YourUserName/weapons-trade-detection-system.git
cd weapons-trade-detection-system
```

### 2. Environment Setup

Create environment files for both frontend and backend:

```bash
# Backend environment
cp backend/.env.example backend/.env  # (if exists)
# Or create backend/.env with:
echo "REDDIT_CLIENT_ID=your_reddit_client_id" >> backend/.env
echo "REDDIT_CLIENT_SECRET=your_reddit_client_secret" >> backend/.env
echo "REDDIT_USER_AGENT=your_app_name" >> backend/.env

# Frontend environment
echo "REACT_APP_API_URL=http://localhost:9000/api" >> frontend/.env
echo "REACT_APP_ENVIRONMENT=development" >> frontend/.env
```

### 3. Start Ollama Service (Required First!)

```bash
# Start Ollama using Docker Compose
docker-compose up -d ollama

# Wait for Ollama to be ready (check logs if needed)
docker-compose logs ollama

# Pull the required model (this may take a while on first run)
docker exec ollama ollama pull llama3.1:8b
```

**Important:** The backend server requires Ollama to be running, so this step is mandatory before starting the backend.

### 4. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend server
python src/server.py
```

The backend will run on `http://localhost:9000`

### 5. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm start
```

The frontend will run on `http://localhost:3000`

### 6. Verify Everything is Running

Check that all services are running:

```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check backend is running
curl http://localhost:9000/health

# Frontend should be accessible at http://localhost:3000
```

## 🛠️ Development Workflow

### Daily Development

1. **Start your day:**
   ```bash
   git pull origin main
   ```

2. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes and test them**

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```

5. **Push to GitHub:**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request on GitHub**

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 📁 Project Structure

```
weapons-trade-detection-system/
├── backend/                 # Python FastAPI backend
│   ├── src/                # Source code
│   │   ├── detection/      # Text analysis modules
│   │   ├── models/         # Data models
│   │   ├── reddit/         # Reddit integration
│   │   └── server.py       # Main server file
│   ├── collected_data/     # Generated data (ignored by git)
│   ├── requirements.txt   # Python dependencies
│   └── venv/              # Virtual environment
├── frontend/               # React frontend
│   ├── src/
│   │   └── components/     # React components
│   ├── package.json       # Node dependencies
│   └── public/            # Static assets
├── docker-compose.yml     # Docker services
├── .gitignore            # Git ignore rules
└── README.md            # Project overview
```

## 🔧 Configuration

### Backend Configuration

The backend uses environment variables for configuration. Key settings:

- `REDDIT_CLIENT_ID` - Your Reddit API client ID
- `REDDIT_CLIENT_SECRET` - Your Reddit API client secret
- `REDDIT_USER_AGENT` - Your app identifier for Reddit API
- `MONGODB_URL` - MongoDB connection string (if using database)

### Frontend Configuration

The frontend uses React environment variables:

- `REACT_APP_API_URL` - Backend API URL (default: http://localhost:9000/api)
- `REACT_APP_ENVIRONMENT` - Environment (development/production)

## 🐛 Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Kill process using port 3000 (frontend)
   lsof -ti:3000 | xargs kill -9
   
   # Kill process using port 9000 (backend)
   lsof -ti:9000 | xargs kill -9
   ```

2. **Python dependencies issues:**
   ```bash
   cd backend
   pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

3. **Node modules issues:**
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

4. **Docker issues:**
   ```bash
   docker-compose down
   docker-compose up -d
   ```

### Getting Help

- Check the main README.md for project overview
- Look at existing code for patterns and examples
- Ask questions in team chat or create an issue on GitHub

## 📝 Code Standards

- **Python**: Follow PEP 8, use type hints
- **JavaScript**: Use modern ES6+ features, follow React best practices
- **Git**: Write clear commit messages, use conventional commits format
- **Testing**: Write tests for new features

## 🚀 Deployment

For production deployment, see the main README.md file for Docker and deployment instructions.

---

**Happy coding! 🎉**

If you run into any issues, don't hesitate to ask for help from the team.
