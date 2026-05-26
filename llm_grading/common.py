import pandas as pd
import ollama
from django.db import connection

def check_file(file):
    allwoed_extention = ('.csv', '.xls', '.xlsx')
    if file is None:
        raise ValueError("There is no file to operate.")
    elif file.name.endswith(allwoed_extention) == False: 
        raise ValueError(f"Invalid file, it only support {(", ".join(allwoed_extention))}.")

def str_to_str(value):
    try:
        if pd.isna(value):
            return ""
        # Convert everything to string first
        value_str = str(value)
        return value_str.strip()
    except (ValueError, TypeError):
        return None    

def str_to_bigint(value, default = None):
    try:
        return int(value)
    except (ValueError, TypeError):
        if default is None:
            return None
        else: 
            return default 

def str_to_float(value, default = None):
    try:
        return float(value)
    except (ValueError, TypeError):
        if default is None:
            return None
        else: 
            return default    
        
def get_all_ollama_llm_model():
    response = ollama.list()
    models = response["models"]
    model_names = [ model["model"] for model in models]

    return model_names


def get_student_grade_report():

    sql = """
SELECT 
	e.name AS exam_name
	, e.exam_code 
	, e.company_name 
	, e.academic_year 
	, e.full_points AS exam_full_points
	, q.total_question 
	, sg.student_name 
	, sg.total_point AS student_total_point
	, sg.grade AS student_grade
	, sg.exam_id 
	, stuA.llm_model 
	, stuA.student_total_answer 
	, stuA.student_total_processed_answer 
	, CASE WHEN stuA.student_total_processed_answer > 0 THEN true ELSE 0 END AS is_llm_processed 
FROM grading_studentgrade sg
INNER JOIN exams_exam e ON e.id = sg.exam_id 
INNER JOIN (
	SELECT
		eq.exam_id 
		, MAX(eq.question_serial) AS total_question
	FROM exams_examquestionanswer eq 
	GROUP BY eq.exam_id 
) AS q ON q.exam_id  = sg.exam_id 
LEFT JOIN (
	SELECT 
		sa.exam_id 
		, sa.student_name 
		, MAX(sa.llm_model) AS llm_model
		, COUNT(*) AS student_total_answer
		, SUM(CASE WHEN sa.llm_has_response = true THEN 1 ELSE 0 END) AS student_total_processed_answer
	FROM grading_studentanswer sa
	GROUP BY sa.exam_id 
		, sa.student_name
) AS stuA ON stuA.exam_id = sg.exam_id AND stuA.student_name = sg.student_name 
"""
    params = []
    where_sql = "WHERE 1 = 1 "
    sql += where_sql
    sql += " \n ORDER BY sg.exam_id, student_grade DESC"
    # execute safely
    with connection.cursor() as cursor:
        #print(cursor.mogrify(sql, params))
        #print(get_sql_debug(sql, params))  # for debugging only
        cursor.execute(sql, params)
        #rows = cursor.fetchall()
        rows = dictfetchall(cursor)

    return rows

def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]