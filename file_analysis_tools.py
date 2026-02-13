import pandas as pd
from pathlib import Path

# Read txt files
def read_text_file(filepath: str):
    if not filepath:
        return f"File not found: {filepath}"
    with open(filepath, 'r') as f:
        return f.read()

# Read excel files

def read_xl_file(filepath: str):
    if not filepath:
        return f"File not found: {filepath}"
    path = Path(filepath)

    if not path.exists():
        return f"File not found: {filepath}"

    sheet_name = path.stem
    df = pd.read_excel(path, sheet_name= sheet_name)
    df = df.dropna(how='all')
    return df.to_dict(orient= "records")