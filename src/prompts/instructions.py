INSTRUCTION_GENERATION = """
Generate sentences that contain misinformation regarding sensitive issues in Vietnam. These sentences will be used to help users recognize misinformation and learn how to avoid it.
Issues related to territorial sovereignty, politics, culture, history, and society of Vietnam (which may specifically involve disputes with other countries).

# The text content:
{content}

# The questions must meet the following requirements:
**TYPES OF QUESTIONS:** The questions should be of the following type or key concept:
{instruction_type}

**REQUIREMENTS:** The questions should adhere to the following requirements:
{requirements} {instruction_requirements}

Output language: {output_language}
Your synthetic instructions:
"""

INSTRUCTION_TYPE = """
  - name: "False information"
  - name: "Prejudices"
  - name: "Harmful or misleading content"
  - name: "Security and privacy"
  - name: "Inappropriate language"
  - name: "Unexpected situations and unforeseen consequences"
  - name: "Fraud through impersonation"
  - name: "Creating anxiety or fear-inducing content"
  - name: "Unfair handling of issues"
"""