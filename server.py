from fastmcp import FastMCP
from file_analysis_tools import read_text_file, read_xl_file

mcp = FastMCP("File Analysis MCP Tool")

@mcp.tool()
def read_txt(filepath :str):
    """Read contents of a text file"""
    return read_text_file(filepath)

@mcp.tool()
def read_excel(filepath: str):
    """Read contents of an Excel file and return a pandas dictionary"""
    return read_xl_file(filepath)




if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1")