from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from models.schemas import QuestionPaperRequest, GeneratedPaper, Question
from services.llm_service import llm_service
from utils import store_chunks, extract_questions_from_paper
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()

@router.post("/generate/paper", response_model=GeneratedPaper)
async def generate_question_paper(
    file: UploadFile = File(None, description="Study material file (.txt)"),
    study_text: str = Form(None, description="Study material text (alternative to file upload)")
):
    """
    Generate a question paper from study material.
    
    Either upload a .txt file or provide study_text directly.
    """
    try:
        # Get study text from file or form
        if file:
            if not file.filename.endswith('.txt'):
                raise HTTPException(status_code=400, detail="Only .txt files are supported")
            
            content = await file.read()
            study_text = content.decode('utf-8')
        elif study_text:
            study_text = study_text
        else:
            raise HTTPException(status_code=400, detail="Either file or study_text must be provided")
        
        if not study_text.strip():
            raise HTTPException(status_code=400, detail="Study material cannot be empty")
        
        # Store chunks in ChromaDB for later retrieval
        chunks = store_chunks(study_text)
        
        # Generate question paper using LLM
        result = llm_service.generate_question_paper(study_text)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Generation failed: {result['error']}")
        
        # Extract questions from generated paper
        questions_df = extract_questions_from_paper(result["question_paper"])
        
        # Convert to response format
        questions = []
        total_marks = 0
        
        for _, row in questions_df.iterrows():
            question = Question(
                question_text=row['question_text'],
                marks=row['marks'],
                answer_text=row['answer_text']
            )
            questions.append(question)
            total_marks += row['marks']
        
        return GeneratedPaper(
            questions=questions,
            total_marks=total_marks,
            raw_paper=result["raw_paper"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/generate/paper/text", response_model=GeneratedPaper)
async def generate_question_paper_from_text(request: QuestionPaperRequest):
    """
    Generate a question paper from study material text.
    """
    try:
        if not request.study_text.strip():
            raise HTTPException(status_code=400, detail="Study material cannot be empty")
        
        # Store chunks in ChromaDB for later retrieval
        chunks = store_chunks(request.study_text)
        
        # Generate question paper using LLM
        result = llm_service.generate_question_paper(request.study_text)
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Generation failed: {result['error']}")
        
        # Extract questions from generated paper
        questions_df = extract_questions_from_paper(result["question_paper"])
        
        # Convert to response format
        questions = []
        total_marks = 0
        
        for _, row in questions_df.iterrows():
            question = Question(
                question_text=row['question_text'],
                marks=row['marks'],
                answer_text=row['answer_text']
            )
            questions.append(question)
            total_marks += row['marks']
        
        return GeneratedPaper(
            questions=questions,
            total_marks=total_marks,
            raw_paper=result["raw_paper"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 