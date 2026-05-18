# Premium Care - Financial Analysis Agent 💰

A powerful, multi-user financial analysis platform that helps you optimize your finances by analyzing bank statements, detecting spending patterns, and providing AI-powered recommendations.

## Features ✨

✅ **Multi-User Support** - Each user has their own secure account  
✅ **PDF Bank Statement Analysis** - Automatically extract transactions from PDFs  
✅ **Real-time Financial Analysis** - Spending by category, trends, anomalies  
✅ **Recurring Transaction Detection** - Identify subscriptions and recurring charges  
✅ **Anomaly Detection** - Find unusual transactions  
✅ **AI Recommendations** - GPT-4 powered optimization suggestions  
✅ **Beautiful Dashboard** - Interactive visualizations with Streamlit  
✅ **Fully Local** - All data stored locally (SQLite), no cloud uploads  
✅ **RESTful API** - Complete API documentation with FastAPI  

## Architecture 🏗️

```
Frontend (Streamlit)
        ↓
FastAPI Backend (REST API)
        ↓
Analysis Engine (Financial Analyzer)
        ↓
LLM Agent (GPT-4 Recommendations)
        ↓
SQLite Database (Local Storage)
```

## Quick Start 🚀

### 1. Clone Repository
```bash
git clone https://github.com/alfiostefano-pcp/premium-care.git
cd premium-care
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Get OpenAI API Key
- Go to: https://platform.openai.com/api-keys
- Create a new secret key
- Copy the key

### 5. Configure Environment
```bash
cp .env.example .env
# Edit .env and paste your OPENAI_API_KEY
```

### 6. Initialize Database
```bash
python backend/database.py
```

### 7. Run Application

**Terminal 1 - Backend API:**
```bash
python backend/app.py
```

**Terminal 2 - Frontend Dashboard:**
```bash
streamlit run frontend/streamlit_app.py
```

### 8. Access Application
- **Dashboard:** http://localhost:8501
- **API Docs:** http://localhost:8000/docs

## Usage 📖

### 1. Register Account
- Go to http://localhost:8501
- Click "Register" tab
- Create account with username, email, password

### 2. Login
- Enter your credentials

### 3. Upload Bank Statement
- Go to "📤 Upload Statement"
- Select your bank statement PDF
- Click "Process Statement"

### 4. View Analysis
- Go to "📈 Analysis"
- Select your statement
- View spending breakdown, recurring charges, anomalies, top merchants

### 5. Get Recommendations
- Go to "💡 Recommendations"
- Select your statement
- Get AI-powered suggestions to optimize spending
- See potential savings

## API Endpoints 📡

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get token

### File Upload
- `POST /upload/statement` - Upload and process PDF

### Analysis
- `GET /analysis/{statement_id}` - Get financial analysis
- `GET /recommendations/{statement_id}` - Get AI recommendations

### User
- `GET /user/profile` - Get user profile
- `GET /user/statements` - Get all user statements

### Health
- `GET /health` - Health check

Full API documentation available at http://localhost:8000/docs

## Project Structure 📁

```
premium-care/
├── backend/
│   ├── app.py                 # FastAPI application
│   ├── config.py              # Configuration management
│   ├── database.py            # Database models & setup
│   ├── models.py              # SQLAlchemy models
│   ├── pdf_processor.py       # PDF parsing
│   ├── analyzer.py            # Financial analysis engine
│   └── llm_agent.py           # LLM integration
├── frontend/
│   └── streamlit_app.py       # Streamlit dashboard
├── data/
│   └── premium_care.db        # SQLite database (created on first run)
├── uploads/
│   └── (bank statements)      # Uploaded PDF files
├── requirements.txt           # Python dependencies
├── .env.example              # Configuration template
├── .gitignore                # Git ignore patterns
└── README.md                 # This file
```

## Configuration ⚙️

Edit `.env` file to customize:

```ini
# OpenAI Configuration
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4

# Database
DATABASE_PATH=data/premium_care.db

# File Upload
MAX_UPLOAD_SIZE_MB=50
UPLOAD_FOLDER=uploads

# Analysis Thresholds
MIN_TRANSACTION_AMOUNT=0.01
ANOMALY_THRESHOLD=2.0              # Standard deviations
RECURRING_THRESHOLD_DAYS=25        # 25-35 days for recurring

# Features
ENABLE_RECOMMENDATIONS=true
ENABLE_REAL_TIME_ANALYSIS=true

# Server
API_HOST=0.0.0.0
API_PORT=8000
```

## Key Components 🔧

### PDFProcessor
Extracts transactions from bank statements with:
- Auto bank type detection
- Date and amount parsing
- Description extraction
- Merchant identification

### FinancialAnalyzer
Performs real-time analysis:
- Category-based spending breakdown
- Monthly/weekly trends
- Recurring transaction detection
- Statistical anomaly detection
- Merchant spending analysis

### FinancialAdvisor (LLM Agent)
AI-powered recommendations using GPT-4:
- Subscription optimization
- Spending category analysis
- Budget recommendations
- Savings opportunities
- Custom fallback recommendations if API fails

### Database Models
- **User** - User accounts with hashed passwords
- **BankStatement** - Uploaded statements metadata
- **Transaction** - Individual transactions
- **FinancialAnalysis** - Cached analysis results
- **Recommendation** - Generated recommendations

## Security 🔒

✅ **Password Hashing** - bcrypt for secure password storage  
✅ **JWT Tokens** - Token-based authentication  
✅ **Local Storage** - No cloud uploads, all data stays local  
✅ **CORS Protection** - API CORS configuration  
✅ **Input Validation** - Pydantic validation on all endpoints  

## Technology Stack 🛠️

- **Backend:** FastAPI, SQLAlchemy, SQLite
- **Frontend:** Streamlit, Plotly, Pandas
- **AI:** OpenAI GPT-4
- **PDF Processing:** pdfplumber, PyPDF2
- **Security:** JWT, bcrypt
- **Database:** SQLite

## Troubleshooting 🐛

### Port Already in Use
```bash
# Change port in .env
API_PORT=8001
```

### OpenAI API Error
- Verify API key is set in `.env`
- Check API key is valid at https://platform.openai.com/api-keys
- Ensure account has credits

### PDF Processing Error
- Verify PDF is from a supported bank
- Ensure PDF contains transaction data
- Check file is not corrupted

### Database Error
```bash
# Reinitialize database
rm data/premium_care.db
python backend/database.py
```

## Contributing 🤝

Feel free to fork, modify, and extend this project!

## License 📄

MIT License - Feel free to use for personal or commercial projects

## Support 💬

For issues or questions:
1. Check existing GitHub issues
2. Create a new issue with details
3. Include error messages and steps to reproduce

---

**Built with ❤️ for financial optimization**

💰 **Start optimizing your finances today!**
