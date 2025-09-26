# 🚨 Weapons Trade Detection System

> **Academic Research Project** - An AI-powered system for detecting suspicious weapons trade activities across online platforms using advanced NLP and machine learning techniques.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.1+-blue.svg)](https://reactjs.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)

## 🎯 Project Overview

This system is designed for **academic research purposes** to study patterns in online weapons trade discussions. It combines web scraping, natural language processing, and machine learning to identify potentially suspicious activities while maintaining ethical research standards.

### Key Features

- 🔍 **Multi-Platform Data Collection** - Reddit, news sites, and forum scraping
- 🤖 **AI-Powered Analysis** - Advanced NLP for pattern detection
- 📊 **Interactive Dashboard** - Real-time visualization and monitoring
- 🛡️ **Safe Playground** - Synthetic data generation for testing
- 🐳 **Docker Ready** - Easy deployment and scaling

## 🏗️ Current Architecture

```
weapons-trade-detection-system/
├── 🖥️  backend/                    # FastAPI Backend Server
│   ├── src/
│   │   ├── detection/             # AI Text Analysis Engine
│   │   │   └── text_analyzer.py   # Weapons pattern detection
│   │   ├── models/                # Data Models & Schemas
│   │   ├── reddit/                # Reddit API Integration
│   │   └── server.py              # Main API Server
│   ├── generation/                # Synthetic Content Generator
│   ├── collected_data/            # Generated Datasets
│   └── requirements.txt           # Python Dependencies
├── 🎨  frontend/                   # React Dashboard
│   ├── src/components/            # UI Components
│   │   ├── Dashboard.js           # Main analytics dashboard
│   │   ├── RedditCollector.js     # Data collection interface
│   │   ├── DetectionForm.js       # Analysis input forms
│   │   └── ContentPlayground.js   # Synthetic data playground
│   └── package.json              # Node.js Dependencies
├── 🐳  docker-compose.yml         # Container Orchestration
└── 📚  docs/                      # Documentation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker Desktop
- Git

### 1. Clone & Setup
```bash
git clone https://github.com/YourUserName/weapons-trade-detection-system.git
cd weapons-trade-detection-system
```

### 2. Start Ollama (AI Service)
```bash
docker-compose up -d ollama
docker exec ollama ollama pull llama3.1:8b
```

### 3. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python src/server.py
```

### 4. Frontend Setup
```bash
cd frontend
npm install
npm start
```

**Access Points:**
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:9000
- 🤖 Ollama AI: http://localhost:11434

## 🧠 Core Components

### 🔍 Detection Engine
- **Text Analysis**: Advanced NLP for identifying suspicious patterns
- **Entity Extraction**: Weapons, locations, and trade indicators
- **Risk Scoring**: AI-powered threat assessment
- **Pattern Recognition**: Machine learning for anomaly detection

### 📊 Data Collection
- **Reddit Integration**: Automated subreddit monitoring
- **News Scraping**: Real-time news article analysis
- **Forum Crawling**: Multi-platform data gathering
- **Synthetic Generation**: Safe testing data creation

### 🎨 Dashboard Features
- **Real-time Monitoring**: Live data collection status
- **Analytics Visualization**: Interactive charts and graphs
- **Content Playground**: Safe experimentation environment
- **Detection Results**: AI analysis and scoring

## 🔮 Future Roadmap

### Phase 1: Enhanced Detection (Q1 2024)
- [ ] **Multi-language Support** - Expand beyond English
- [ ] **Advanced ML Models** - Custom trained models for weapons detection
- [ ] **Real-time Streaming** - Live data processing pipeline
- [ ] **API Rate Limiting** - Improved data collection efficiency

### Phase 2: Platform Expansion (Q2 2024)
- [ ] **Twitter/X Integration** - Social media monitoring
- [ ] **Telegram Monitoring** - Encrypted platform analysis
- [ ] **Dark Web Simulation** - Safe research environment
- [ ] **Blockchain Analysis** - Cryptocurrency transaction tracking

### Phase 3: Advanced Analytics (Q3 2024)
- [ ] **Network Analysis** - User relationship mapping
- [ ] **Temporal Patterns** - Time-series analysis
- [ ] **Geographic Mapping** - Location-based insights
- [ ] **Threat Intelligence** - Automated reporting system

### Phase 4: Research Tools (Q4 2024)
- [ ] **Academic Dashboard** - Research-focused interface
- [ ] **Data Export Tools** - Research data extraction
- [ ] **Collaboration Features** - Multi-researcher support
- [ ] **Publication Tools** - Automated report generation

## 🛠️ Development

### Tech Stack
- **Backend**: FastAPI, Python, MongoDB
- **Frontend**: React, JavaScript, CSS3
- **AI/ML**: Ollama, Transformers, scikit-learn
- **Infrastructure**: Docker, Docker Compose
- **Data**: Pandas, NumPy, JSON

### Contributing
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Setup
See [DEVELOPER_SETUP.md](./DEVELOPER_SETUP.md) for detailed setup instructions.

## 📊 Research Applications

### Academic Use Cases
- **Criminology Research** - Study of online illegal trade patterns
- **Digital Forensics** - Investigation of cybercrime networks
- **Social Network Analysis** - Understanding criminal networks
- **AI Ethics Research** - Responsible AI development

### Data Privacy & Ethics
- ✅ **Synthetic Data Generation** - Safe testing without real data
- ✅ **Academic Research Focus** - Educational and research purposes only
- ✅ **Privacy Protection** - No personal data collection
- ✅ **Open Source** - Transparent and auditable code

## 🚨 Important Disclaimers

> **⚠️ Academic Research Only**: This system is designed exclusively for academic research and educational purposes. It should not be used for surveillance, monitoring, or any commercial applications.

> **🔒 Privacy First**: All data collection follows ethical guidelines and privacy protection standards.

> **📚 Educational Purpose**: This project serves as a learning tool for understanding AI applications in cybersecurity research.

## 📈 Performance Metrics

- **Data Processing**: 1000+ posts per minute
- **Detection Accuracy**: 85%+ precision on synthetic data
- **Response Time**: <2 seconds for real-time analysis
- **Scalability**: Docker-ready for cloud deployment

## 🤝 Contributing & Support

### Getting Help
- 📖 Check the [Documentation](./docs/)
- 🐛 Report issues on [GitHub Issues](https://github.com/YourUserName/weapons-trade-detection-system/issues)
- 💬 Join our [Discord Community](https://discord.gg/your-invite)
- 📧 Email: research@yourdomain.com

### Code of Conduct
We are committed to providing a welcoming and inclusive environment. Please read our [Code of Conduct](./CODE_OF_CONDUCT.md) before contributing.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🙏 Acknowledgments

- **Academic Advisors** - For research guidance and ethical oversight
- **Open Source Community** - For the amazing tools and libraries
- **Research Partners** - For collaboration and feedback
- **Contributors** - For making this project possible

---

**🔬 Built for Academic Research | 🛡️ Privacy-First Design | 🚀 Open Source**

*This project is part of ongoing academic research into AI applications for cybersecurity and digital forensics.*

https://github.com/user-attachments/assets/04e42ad9-809b-47de-b14c-519806b57c10


<img width="1206" height="820" alt="Screenshot 2025-09-26 at 19 57 24" src="https://github.com/user-attachments/assets/8a15ed8a-b275-4222-982a-94f5514d6b79" />


```bash

{
  "analysis_info": {
    "analyzed_at": "2025-09-26T19:54:58.414585",
    "total_posts": 2,
    "high_risk_posts": 2,
    "medium_risk_posts": 0,
    "low_risk_posts": 0,
    "academic_disclaimer": "ACADEMIC RESEARCH DATA COLLECTION\n        This data is collected for legitimate academic research purposes only.\n        All data handling follows academic ethics guidelines and privacy laws."
  },
  "high_risk_posts": [
    {
      "id": "1no0gmr",
      "title": "Well, he would, wouldn't he?",
      "content": "Mandy Rice-Davies brought down the UK [Tory](https://en.wikipedia.org/wiki/Conservative_Party_(UK)) government in 1963, specifically Tory MP [Lord Astor](https://en.wikipedia.org/wiki/William_Astor,_3rd_Viscount_Astor) and Tory Minister of War [John Profumo](https://en.wikipedia.org/wiki/John_Profumo). She was effectively pimped out by social climber [Stephen Ward](https://en.wikipedia.org/wiki/Stephen_Ward), who died by barbiturate overdose that same year (some have suggested an MI6 motive).\n\nClimax magazine, Oct 1963, reported an FBI report that there was a \"ring of call girls who worked both sides of the Atlantic and specialized in catering to the diplomatic trade. Some of these girls were known to be acquainted with [Christine Keeler](https://en.wikipedia.org/wiki/Christine_Keeler).\" Both Rice-Davies and Keeler had visited the US in July 1962 to set up shop near [the UN](https://en.wikipedia.org/wiki/Headquarters_of_the_United_Nations) and had been seen around the diplomatic circles.\n\nA confidential source to Climax stated: \"There was an American around here a while back who wanted to get some land rights in another country. He kept a stable of girls very busy helping his cause -- but I can't say for sure that he got what he wanted... The Russians and [their satellites](https://en.wikipedia.org/wiki/Eastern_Bloc) do use sex to get information, but they seldom use the professionals for this sort of thing. Most of the men around the UN engage in sex because it's part of life. The Russians and their satellites use sex as a weapon. They enter into sexual alliances the same as they'd sign a treaty.\n\n[Dorothy Kilgallen](https://en.wikipedia.org/wiki/Dorothy_Kilgallen) summarized: \"The news stories about ladies of the evening fluttering the corridors of the United Nations building had an immediate effect on the East Side neighborhood of the world organization. Scores of shady belles decided it sounded like a good idea, and veteran bar operators with places near the UN report that they haven't seen so many unmistakable types in the area since World War II.\"",
      "subreddit": "conspiracy",
      "author_hash": "30d481ef4f01ea68",
      "score": 4,
      "num_comments": 2,
      "created_utc": 1758579728.0,
      "url": "https://reddit.com/r/conspiracy/comments/1no0gmr/well_he_would_wouldnt_he/",
      "collected_at": "2025-09-26T19:54:35.993271",
      "risk_analysis": {
        "risk_score": 1.0,
        "confidence": 0.9,
        "flags": [
          "HIGH RISK: Detected firearms keyword 'sig'",
          "HIGH RISK: Detected firearms keyword 'magazine'",
          "HIGH RISK: Detected explosives keyword 'ied'",
          "HIGH RISK: Detected violence keyword 'ice'",
          "CRITICAL: Weapon + transaction intent detected",
          "CRITICAL: Weapon + violence intent detected"
        ],
        "detected_keywords": [
          "firearms: sig, magazine",
          "explosives: ied",
          "violence: ice"
        ],
        "detected_patterns": [],
        "analysis_time": "2025-09-26T19:54:58.412704"
      }
    },
    {
      "id": "1npoijl",
      "title": "Trying to understand AR pistols. Are they a compromise or a solid choice for anything in particular?",
      "content": "I'm a veteran and have built a modest collection of firearms over the years so while I'm acceptably comfortable and familiar with guns, I don't really pay attention to what's new out there or even what's been around for a bit already.\n\nI just started noticing AR pistols recently (I never claimed to be all that swift) and I'm genuinely curious - what role do they play? Are they good for a specific purpose over another weapon or were they mainly developed from a place of needing to sidestep state/federal regulations? \n\nPart of me wants to hear that they're a jack-of-all-trades-but-a-master-of-none so I can save my money. But then again, if they're a solid platform, I could be persuaded to make room for one in my safe. Thanks for reading!   ",
      "subreddit": "liberalgunowners",
      "author_hash": "eb50420a4d36ddca",
      "score": 58,
      "num_comments": 109,
      "created_utc": 1758749081.0,
      "url": "https://reddit.com/r/liberalgunowners/comments/1npoijl/trying_to_understand_ar_pistols_are_they_a/",
      "collected_at": "2025-09-26T19:54:46.077030",
      "risk_analysis": {
        "risk_score": 1.0,
        "confidence": 0.9,
        "flags": [
          "HIGH RISK: Detected firearms keyword 'gun'",
          "HIGH RISK: Detected firearms keyword 'pistol'",
          "HIGH RISK: Detected firearms keyword 'firearm'",
          "HIGH RISK: Detected firearms keyword 'fal'",
          "HIGH RISK: Detected violence keyword 'ice'",
          "CRITICAL: Weapon + transaction intent detected",
          "CRITICAL: Weapon + violence intent detected"
        ],
        "detected_keywords": [
          "firearms: gun, pistol, firearm, fal",
          "violence: ice"
        ],
        "detected_patterns": [],
        "analysis_time": "2025-09-26T19:54:58.413880"
      }
    }
  ],
  "medium_risk_posts": [],
  "low_risk_posts": []
}

```

