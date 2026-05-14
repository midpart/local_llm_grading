import pandas as pd
import ollama

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