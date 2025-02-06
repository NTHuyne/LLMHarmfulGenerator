import asyncio
import os
import json
from tqdm import tqdm

from src.openai_calling.call_openai import OpenAIGenerator
from src.utils.load_data import load_jsonl, get_random_tasks
from src.utils.utils import remove_number_from_start
from src.prompts.responses import RESPONSES_GENERATION, REQUIREMENTS
from configs.config import settings

async def process_chunk(
    instruction, instruction_type, document, openai_client, metadata):
    try:
        messages = [
            {
                "role": "user",
                "content": RESPONSES_GENERATION.format(
                    instruction_requirements=settings.CONF['instruction_requirements'],
                    instruction_type=instruction_type,
                    response_requirements=settings.CONF['response_requirements'],
                    domain=settings.CONF['domain'],
                    instruction=instruction,
                    requirements=REQUIREMENTS,
                    output_language=settings.CONF['output_language']
                )
            }
        ]
        response = openai_client.call_openai(messages)

        if response.strip():
            instruction_length = metadata['instruction_length']

            return {
                'document': document,
                'instruction': instruction,
                'instruction_type': instruction_type,
                'instruction_length': instruction_length,
                'response_length': len(response),
                'response': response
            }
    except Exception as e:
        print(f"Error processing chunk {id}: {e}")
        return None

async def synthesize_response(file_name, batch_size=settings.CONF['batch_size']):
    openai_client = OpenAIGenerator(settings.CONF['llm'])
    instructions_file = os.path.join(settings.CONF['data']['instructions'], file_name)
    responses_file = os.path.join(settings.CONF['data']['responses'], file_name)


    # Load and filter data
    data = load_jsonl(instructions_file)
    tasks = [
        process_chunk(
            line['instruction'], line['instruction_type'], line['document'],
            openai_client, metadata=line
        )
        for line in data
    ]

    # Process tasks in batches
    os.makedirs(os.path.dirname(responses_file), exist_ok=True)

    for i in tqdm(range(0, len(tasks), batch_size), desc="Synthesizing responses"):
        batch_tasks = tasks[i:i+batch_size]
        batch_results = await asyncio.gather(*batch_tasks)

        with open(responses_file, mode='a', encoding='utf-8') as file:
            for result in batch_results:
                json.dump(result, file, ensure_ascii=False)
                file.write('\n')

    print(f"Responses have been saved to {responses_file}")
