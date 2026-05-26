from dataclasses import dataclass, field
from typing import List

@dataclass
class ExamDetailsDTO:
    title: str
    details: str
    relation_to_question_no: str
    
@dataclass
class ExamQuestionDTO:
    question_serial: int
    points: int
    question: str
    sample_answer: str

    details: List[ExamDetailsDTO] = field(default_factory=list)

@dataclass
class StudentGradeDTO:
    exam_id: int 
    exam_name: str
    exam_code: str 
    exam_full_points: int 
    academic_year: int
    total_question: int
    student_name: str  
    student_total_point: float
    student_grade: int
    student_total_answer: int
    student_total_processed_answer: int
    llm_model: str
    is_llm_processed: bool