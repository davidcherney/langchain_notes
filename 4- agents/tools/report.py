#Instances of Tool can only use a single argument. 
# That is a legacy LangChain thing that will be changed someday...
# For now, StructureTools are the multivariate version object.

from langchain.tools import StructuredTool 
# from pydantic.v1 import BaseSchema # Needs explanation. 
# from pydantic.v1 import BaseModel
from pydantic import BaseModel

def write_report(filename, html):
    with open(filename, 'w') as f:
        f.write(html)

class WriteReportArgsSchema(BaseModel):
    filename: str
    html: str

write_report_tool = StructuredTool.from_function(
    name="write_report",
    description=("Write an HTML file to disk. "
    + "Use this tool whenever someone asks for a report."),
    func=write_report,
    args_schema=WriteReportArgsSchema,
)

