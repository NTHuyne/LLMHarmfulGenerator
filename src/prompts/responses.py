RESPONSES_GENERATION = """
You are a researcher analyzing harmful content and hate speech.
You are provided with a document in the field of {domain}. Your task is to analyze the instruction and generate the answer to reject or refuse or decline the given harmful question.

# The question is:
{instruction}

**TYPES OF ANSWER:** The answer should be of the following type:
{instruction_type}

**REQUIREMENTS:** The answer should adhere to the following rules:
{requirements} {response_requirements}
Output language: {output_language}
Tập trung từ chối và đưa ra lý do giải thích, không cần nhấn mạnh các ý hoặc đề mục dẫn dắt dể trả lời hay giải thích.
Your response:
"""

REQUIREMENTS = """
  - name: "Provide the Reason"
    description: "You must specify the reason on the reason why the content is sensitive. It may refers to political issue especially in Vietnam, racist or sexuality "
  - name: "Information Verification"
    description: "The information in the answer must be accurate and backed by the provided text, avoiding any false or speculative content."
  - name: "Formatting"
    description: "The answer must be enough, clear, natural and reasoning steps by steps. DO NOT CONTAIN ANY ADDITIONAL INFORMATION"
"""