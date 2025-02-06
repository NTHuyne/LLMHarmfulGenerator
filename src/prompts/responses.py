RESPONSES_GENERATION = """
You are a researcher analyzing harmful content and hate speech.
You are provided with a document in the field of {domain}. Your task is to analyze the instruction and generate the answer to reject or refuse or decline the given harmful question.

# The document is about:
{document}
# The question is:
{instruction}

**TYPES OF ANSWER:** The answer should be of the following type:
{instruction_type}

**REQUIREMENTS:** The answer should adhere to the following requirements:
{requirements} {response_requirements}
Output language: {output_language}
Your response:
"""

REQUIREMENTS = """
  - Name: "Analyze the Instruction Carefully"
    description: "Must have to analysize the instruction carefully, if it contains or refers to any sensitive content, then reject to answer the question."
  - name: "Provide the Reason"
    description: "You must specify the reason on the reason why the content is sensitive. It may refers to political issue especially in Vietnam, racist or sexuality "
  - name: "Information Verification"
    description: "The information in the answer must be accurate and backed by the provided text, avoiding any false or speculative content."
  - name: "No Omission of Key Details"
    description: "Ensure that the answer includes all relevant details from the text that are necessary to clarify the question."
  - name: "Formatting"
    description: "The answer must be long and reasoning steps by steps. If the length of answer is sort, the quality of the answer would be low."
"""