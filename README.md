# 📚 Question Paper Generator & Evaluator

A full-stack AI-powered application for generating question papers from study material and evaluating student answers using advanced NLP and LLM technologies.

## 🚀 Features

### Backend (FastAPI)
- **Question Paper Generation**: Generate 50-mark question papers with 2, 5, or 10 mark questions
- **Answer Evaluation**: Evaluate individual student answers with detailed feedback
- **Batch Evaluation**: Process multiple answers from CSV files
- **ChromaDB Integration**: Vector storage for efficient text retrieval
- **Graph-based Context**: spaCy-powered concept extraction and relationship mapping
- **DSPy Integration**: Advanced LLM orchestration with Llama3-70B via Groq

### Frontend (Streamlit)
- **📘 Upload Study Material**: File upload and direct text input
- **📝 Generate Question Paper**: AI-powered question generation with preview
- **✅ Evaluate Single Answer**: Individual answer evaluation with detailed feedback
- **📊 Evaluate from CSV**: Batch evaluation with comprehensive results
- **📈 Score Summary**: Analytics dashboard with visualizations

## 🏗️ Architecture

```
llm-proj/
├── backend/                 # FastAPI Backend
│   ├── main.py             # FastAPI app entrypoint
│   ├── config.py           # Configuration settings
│   ├── utils.py            # Utility functions (ChromaDB, spaCy, etc.)
│   ├── models/
│   │   └── schemas.py      # Pydantic models
│   ├── routes/
│   │   ├── generate.py     # Question generation endpoints
│   │   └── evaluate.py     # Evaluation endpoints
│   └── services/
│       └── llm_service.py  # DSPy LLM service
├── frontend/               # Streamlit Frontend
│   ├── main.py            # Main Streamlit app
│   ├── pages.py           # Page functions
│   └── requirements.txt   # Frontend dependencies
├── requirements.txt       # Backend dependencies
└── README.md             # This file
```

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8+
- Groq API key (for Llama3-70B access)
- spaCy English model

### 1. Clone and Setup
```bash
git clone <repository-url>
cd llm-proj
```

### 2. Install Dependencies

#### Backend Setup
```bash
# Install backend dependencies
pip install -r requirements.txt

# Install spaCy English model
python -m spacy download en_core_web_sm
```

#### Frontend Setup
```bash
# Install frontend dependencies
cd frontend
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy example environment file
cp env.example .env

# Edit .env file with your Groq API key
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Start the Application

#### Start Backend
```bash
# From project root
cd backend
python start.py
```
Backend will be available at: http://localhost:8000
API Documentation: http://localhost:8000/docs

#### Start Frontend
```bash
# From project root
cd frontend
python start.py
```
Frontend will be available at: http://localhost:8501

## 📖 Usage Guide

### 1. Upload Study Material
- Navigate to "📘 Upload Study Material"
- Upload a `.txt` file or paste text directly
- Study material is processed and stored in ChromaDB

### 2. Generate Question Paper
- Go to "📝 Generate Question Paper"
- Click "Generate Question Paper" button
- Download generated paper as text or CSV

### 3. Evaluate Answers
- **Single Answer**: Use "✅ Evaluate Single Answer" page
- **Batch Evaluation**: Use "📊 Evaluate from CSV" page
- Upload CSV files with questions and student answers

### 4. View Analytics
- Visit "📈 Score Summary" for detailed analytics
- Upload evaluation results CSV for visualization

## 🔧 API Endpoints

### Generation
- `POST /api/v1/generate/paper` - Generate from file upload
- `POST /api/v1/generate/paper/text` - Generate from text input

### Evaluation
- `POST /api/v1/evaluate/one` - Evaluate single answer (file upload)
- `POST /api/v1/evaluate/one/text` - Evaluate single answer (text input)
- `POST /api/v1/evaluate/csv` - Batch evaluation from CSV files
- `POST /api/v1/evaluate/csv/text` - Batch evaluation from base64 CSV

## 📊 CSV Formats

### Questions CSV
```csv
question_text,marks,answer_text
"What is machine learning?",5,"Machine learning is..."
"Explain neural networks.",10,"Neural networks are..."
```

### Student Answers CSV
```csv
question_number,student_answer
1,"Machine learning is a subset of AI..."
2,"Neural networks are computational models..."
```

## 🧠 Technical Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **DSPy**: Advanced LLM orchestration
- **ChromaDB**: Vector database for embeddings
- **spaCy**: NLP for concept extraction
- **SentenceTransformers**: Text embeddings
- **NetworkX**: Graph operations
- **Pydantic**: Data validation

### Frontend
- **Streamlit**: Rapid web app development
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation
- **Requests**: HTTP client

### AI/ML
- **Llama3-70B**: Large language model (via Groq)
- **all-MiniLM-L6-v2**: Sentence embeddings
- **en_core_web_sm**: spaCy English model

## 🔐 Security Features

- CORS configuration for frontend-backend communication
- Input validation with Pydantic models
- Error handling and logging
- Environment variable configuration

## 🚀 Deployment

### Local Development
```bash
# Terminal 1: Backend
cd backend && python start.py

# Terminal 2: Frontend  
cd frontend && python start.py
```

### Production
- Use production WSGI server (Gunicorn) for FastAPI
- Configure environment variables
- Set up proper CORS origins
- Use HTTPS in production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **spaCy model not found**
   ```bash
   python -m spacy download en_core_web_sm
   ```

2. **ChromaDB connection issues**
   - Check if ChromaDB is running
   - Verify collection permissions

3. **Groq API errors**
   - Verify API key in environment variables
   - Check API quota and limits

4. **Frontend can't connect to backend**
   - Ensure backend is running on port 8000
   - Check CORS configuration
   - Verify network connectivity

### Debug Mode
```bash
# Backend debug mode
DEBUG=True python backend/start.py

# Frontend debug mode
streamlit run frontend/main.py --logger.level debug
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review API documentation at http://localhost:8000/docs
3. Open an issue on GitHub

---

**Built with ❤️ using FastAPI, Streamlit, and DSPy** 