from pydantic import BaseModel
from typing import List, Optional
from fastapi import UploadFile

# Request Models
class StudyMaterialUpload(BaseModel):
    filename: str
    content: str

class QuestionPaperRequest(BaseModel):
    study_text: str

class SingleEvaluationRequest(BaseModel):
    study_text: str
    question: str
    reference_answer: str
    student_answer: str
    max_marks: int

class CSVEvaluationRequest(BaseModel):
    study_text: str
    questions_csv: str  # Base64 encoded CSV content
    student_answers_csv: str  # Base64 encoded CSV content

# Response Models
class Question(BaseModel):
    question_text: str
    marks: int
    answer_text: str

class GeneratedPaper(BaseModel):
    questions: List[Question]
    total_marks: int
    raw_paper: str

class EvaluationFeedback(BaseModel):
    score: float
    max_marks: int
    rubric: str
    feedback: str
    detailed_analysis: str

class SingleEvaluationResponse(BaseModel):
    question: str
    evaluation: EvaluationFeedback

class CSVEvaluationResult(BaseModel):
    question_number: int
    score: float
    max_marks: int
    feedback: str

class CSVEvaluationResponse(BaseModel):
    results: List[CSVEvaluationResult]
    total_score: float
    total_max_marks: int
    percentage: float

# Error Models
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None 