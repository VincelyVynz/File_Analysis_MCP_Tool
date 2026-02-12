

# Read txt files
def read_text_file(filepath: str):
    if not filepath:
        return f"File not found: {filepath}"
    with open(filepath, 'r') as f:
        return f.read()


