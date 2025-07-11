from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from models.schemas import (
    SingleEvaluationRequest, CSVEvaluationRequest, 
    SingleEvaluationResponse, CSVEvaluationResponse, CSVEvaluationResult,
    EvaluationFeedback
)
from services.llm_service import llm_service
from utils import (
    store_chunks, retrieve_chunks, build_graph, graph_context,
    decode_csv_content, calculate_percentage
)
import sys
import os
import pandas as pd
import io

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

router = APIRouter()

@router.post("/evaluate/one", response_model=SingleEvaluationResponse)
async def evaluate_single_answer(
    file: UploadFile = File(None, description="Study material file (.txt)"),
    study_text: str = Form(None, description="Study material text"),
    question: str = Form(..., description="Question text"),
    reference_answer: str = Form(..., description="Reference answer"),
    student_answer: str = Form(..., description="Student answer"),
    max_marks: int = Form(..., description="Maximum marks for this question")
):
    """
    Evaluate a single student answer.
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
        
        # Store chunks and build graph
        chunks = store_chunks(study_text)
        graph = build_graph(study_text)
        
        # Build context for evaluation
        context = f"Maximum Marks: {max_marks}\nReference Answer: {reference_answer}\n"
        context += "\n".join(retrieve_chunks(question)) + "\n\n"
        context += graph_context(question, graph)
        
        # Evaluate using LLM
        result = llm_service.evaluate_answer(
            study_context=context,
            question=question,
            student_answer=student_answer,
            reference_answer=reference_answer
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Evaluation failed: {result['error']}")
        
        # Create evaluation feedback
        evaluation = EvaluationFeedback(
            score=result["score"],
            max_marks=max_marks,
            rubric="Academic evaluation rubric",
            feedback=result["evaluation"],
            detailed_analysis=result["detailed_analysis"]
        )
        
        return SingleEvaluationResponse(
            question=question,
            evaluation=evaluation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/evaluate/one/text", response_model=SingleEvaluationResponse)
async def evaluate_single_answer_from_text(request: SingleEvaluationRequest):
    """
    Evaluate a single student answer from text input.
    """
    try:
        if not request.study_text.strip():
            raise HTTPException(status_code=400, detail="Study material cannot be empty")
        
        # Store chunks and build graph
        chunks = store_chunks(request.study_text)
        graph = build_graph(request.study_text)
        
        # Build context for evaluation
        context = f"Maximum Marks: {request.max_marks}\nReference Answer: {request.reference_answer}\n"
        context += "\n".join(retrieve_chunks(request.question)) + "\n\n"
        context += graph_context(request.question, graph)
        
        # Evaluate using LLM
        result = llm_service.evaluate_answer(
            study_context=context,
            question=request.question,
            student_answer=request.student_answer,
            reference_answer=request.reference_answer
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=f"Evaluation failed: {result['error']}")
        
        # Create evaluation feedback
        evaluation = EvaluationFeedback(
            score=result["score"],
            max_marks=request.max_marks,
            rubric="Academic evaluation rubric",
            feedback=result["evaluation"],
            detailed_analysis=result["detailed_analysis"]
        )
        
        return SingleEvaluationResponse(
            question=request.question,
            evaluation=evaluation
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/evaluate/csv", response_model=CSVEvaluationResponse)
async def evaluate_from_csv(
    file: UploadFile = File(None, description="Study material file (.txt)"),
    study_text: str = Form(None, description="Study material text"),
    questions_csv: UploadFile = File(..., description="Questions CSV file"),
    student_answers_csv: UploadFile = File(..., description="Student answers CSV file")
):
    """
    Evaluate multiple student answers from CSV files.
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
        
        # Read CSV files
        questions_content = await questions_csv.read()
        student_answers_content = await student_answers_csv.read()
        
        questions_df = pd.read_csv(io.StringIO(questions_content.decode('utf-8')))
        student_answers_df = pd.read_csv(io.StringIO(student_answers_content.decode('utf-8')))
        
        # Store chunks and build graph
        chunks = store_chunks(study_text)
        graph = build_graph(study_text)
        
        # Evaluate each answer
        results = []
        total_score = 0
        total_max_marks = 0
        
        for _, student_row in student_answers_df.iterrows():
            question_number = int(student_row["question_number"])
            question_idx = question_number - 1
            
            if question_idx >= len(questions_df):
                continue
                
            question_row = questions_df.iloc[question_idx]
            
            # Build context
            context = f"Maximum Marks: {question_row['marks']}\nReference Answer: {question_row['answer_text']}\n"
            context += "\n".join(retrieve_chunks(question_row['question_text'])) + "\n\n"
            context += graph_context(question_row['question_text'], graph)
            
            # Evaluate
            result = llm_service.evaluate_answer(
                study_context=context,
                question=question_row['question_text'],
                student_answer=student_row["student_answer"],
                reference_answer=question_row['answer_text']
            )
            
            score = result["score"] if result["success"] else 0.0
            
            results.append(CSVEvaluationResult(
                question_number=question_number,
                score=score,
                max_marks=question_row['marks'],
                feedback=result["evaluation"] if result["success"] else "Evaluation failed"
            ))
            
            total_score += score
            total_max_marks += question_row['marks']
        
        percentage = calculate_percentage(total_score, total_max_marks)
        
        return CSVEvaluationResponse(
            results=results,
            total_score=total_score,
            total_max_marks=total_max_marks,
            percentage=percentage
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/evaluate/csv/text", response_model=CSVEvaluationResponse)
async def evaluate_from_csv_text(request: CSVEvaluationRequest):
    """
    Evaluate multiple student answers from base64 encoded CSV content.
    """
    try:
        if not request.study_text.strip():
            raise HTTPException(status_code=400, detail="Study material cannot be empty")
        
        # Decode CSV content
        questions_df = decode_csv_content(request.questions_csv)
        student_answers_df = decode_csv_content(request.student_answers_csv)
        
        # Store chunks and build graph
        chunks = store_chunks(request.study_text)
        graph = build_graph(request.study_text)
        
        # Evaluate each answer
        results = []
        total_score = 0
        total_max_marks = 0
        
        for _, student_row in student_answers_df.iterrows():
            question_number = int(student_row["question_number"])
            question_idx = question_number - 1
            
            if question_idx >= len(questions_df):
                continue
                
            question_row = questions_df.iloc[question_idx]
            
            # Build context
            context = f"Maximum Marks: {question_row['marks']}\nReference Answer: {question_row['answer_text']}\n"
            context += "\n".join(retrieve_chunks(question_row['question_text'])) + "\n\n"
            context += graph_context(question_row['question_text'], graph)
            
            # Evaluate
            result = llm_service.evaluate_answer(
                study_context=context,
                question=question_row['question_text'],
                student_answer=student_row["student_answer"],
                reference_answer=question_row['answer_text']
            )
            
            score = result["score"] if result["success"] else 0.0
            
            results.append(CSVEvaluationResult(
                question_number=question_number,
                score=score,
                max_marks=question_row['marks'],
                feedback=result["evaluation"] if result["success"] else "Evaluation failed"
            ))
            
            total_score += score
            total_max_marks += question_row['marks']
        
        percentage = calculate_percentage(total_score, total_max_marks)
        
        return CSVEvaluationResponse(
            results=results,
            total_score=total_score,
            total_max_marks=total_max_marks,
            percentage=percentage
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 