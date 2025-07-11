import os
import dspy
from dspy import Signature, InputField, OutputField, Predict, Module
from typing import Dict, Any
import re

# Configure DSPy with Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "..")

# Initialize DSPy LM
lm = dspy.LM(
    "openai/llama3-70b-8192",
    api_key=GROQ_API_KEY,
    api_base="https://api.groq.com/openai/v1"
)
dspy.configure(lm=lm)

class EvalSignature(dspy.Signature):
    """Signature for answer evaluation"""
    study_context = dspy.InputField()
    question = dspy.InputField()
    reference_answer = dspy.InputField()
    student_answer = dspy.InputField()
    evaluation = OutputField(desc="Score, rubric, and feedback")

class EvalModule(Module):
    """DSPy module for evaluating student answers"""
    def __init__(self):
        super().__init__()
        self.pred = Predict(EvalSignature)

    def forward(self, study_context: str, question: str, student_answer: str, reference_answer: str):
        return self.pred(
            study_context=study_context,
            question=question,
            student_answer=student_answer,
            reference_answer=reference_answer
        )

class QuestionGenSignature(Signature):
    """Signature for question paper generation"""
    study_text = InputField()
    question_paper = OutputField(desc="50-mark question paper with answers")

class QuestionGenModule(Module):
    """DSPy module for generating question papers"""
    def __init__(self):
        super().__init__()
        self.gen = Predict(QuestionGenSignature)

    def forward(self, study_text: str):
        prompt = f"""
You are a strict academic examiner.

Generate a question paper totaling **EXACTLY 50 marks** from the study material below, using ONLY questions of **2, 5, or 10 marks**.

❗Important Rules:
- Only 2, 5, or 10 mark questions are allowed.
- Total should be EXACTLY 50 marks.
- Include model answers.
- Format must be:

1. Question text (2 marks)
Answer: ...

2. Question text (5 marks)
Answer: ...

3. Question text (10 marks)
Answer: ...

...

📌 Do NOT include any titles, instructions, or extra explanations.

STUDY MATERIAL:
{study_text}
"""
        return self.gen(study_text=prompt)

class LLMService:
    """Service class for LLM operations"""
    
    def __init__(self):
        self.question_generator = QuestionGenModule()
        self.evaluator = EvalModule()
    
    def generate_question_paper(self, study_text: str) -> Dict[str, Any]:
        """Generate a question paper from study material"""
        try:
            result = self.question_generator(study_text=study_text)
            return {
                "success": True,
                "question_paper": result.question_paper,
                "raw_paper": result.question_paper
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "question_paper": "",
                "raw_paper": ""
            }
    
    def evaluate_answer(self, study_context: str, question: str, 
                       student_answer: str, reference_answer: str) -> Dict[str, Any]:
        """Evaluate a single student answer"""
        try:
            result = self.evaluator(
                study_context=study_context,
                question=question,
                student_answer=student_answer,
                reference_answer=reference_answer
            )
            
            # Extract score from evaluation text
            score_match = re.search(r"Score:\s*([0-9.]+)", result.evaluation)
            score = float(score_match.group(1)) if score_match else 0.0
            
            return {
                "success": True,
                "evaluation": result.evaluation,
                "score": score,
                "detailed_analysis": result.evaluation
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "evaluation": "",
                "score": 0.0,
                "detailed_analysis": ""
            }

# Global service instance
llm_service = LLMService() 
