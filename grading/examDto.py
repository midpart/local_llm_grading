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