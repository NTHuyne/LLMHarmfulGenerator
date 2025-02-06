import asyncio
import os
import json
from tqdm import tqdm
from src.openai_calling.call_openai import OpenAIGenerator
from src.utils.load_data import load_jsonl, get_random_tasks
from src.utils.utils import remove_number_from_start
from src.prompts.instructions import INSTRUCTION_GENERATION, INSTRUCTION_TYPE, REQUIREMENTS
from configs.config import settings

async def process_chunk(
    content, openai_client, number_questions_per_chunk, output_language, instruction_requirements, response_requirements, domain, requirements ):
    try:
        instructions = []
        existing_instruction_types = set()
        max_instruction_types = len(INSTRUCTION_TYPE.split('\n')) // 2

        for _ in range(number_questions_per_chunk):
            while True:
                instruction_type = get_random_tasks(instruction_type=INSTRUCTION_TYPE)
                if instruction_type not in existing_instruction_types or len(existing_instruction_types) >= max_instruction_types:
                    existing_instruction_types.add(instruction_type)
                    break

            messages = [
                {
                    "role": "user",
                    "content": INSTRUCTION_GENERATION.format(
                        response_requirements=response_requirements,
                        domain=domain,
                        number_questions_per_openai_call=settings.CONF['number_questions_per_openai_call'],
                        content=content,
                        instruction_type=instruction_type,
                        requirements=requirements,
                        output_language=output_language
                    )
                }
            ]
            sample = openai_client.call_openai(messages)

            if sample.strip():
                for line in filter(bool, map(str.strip, sample.split('\n'))):
                    instructions.append((remove_number_from_start(line), instruction_type))

        # Batch results for writing
        results = []
        for instruction, instruction_type in instructions:
            results.append({
                'document': content,
                'instruction': instruction,
                'instruction_type': instruction_type,
                'instruction_length': len(instruction),
            })

        return results

    except Exception as e:
        print(f"Error processing chunk {id}: {e}")
        raise

async def synthesize_instruction(file_name, batch_size=settings.CONF['batch_size']):
    openai_client = OpenAIGenerator(settings.CONF['llm'])
    instructions_file = os.path.join(settings.CONF['data']['instructions'], file_name)
    chunks_file = os.path.join(settings.CONF['data']['chunks'], file_name)


    # Load and filter data
    data = load_jsonl(chunks_file)
    tasks = [
        process_chunk(
            line['context'], openai_client,
            number_questions_per_chunk=settings.CONF['number_questions_per_chunk'],
            output_language=settings.CONF['output_language'],
            instruction_requirements=settings.CONF['instruction_requirements'],
            response_requirements=settings.CONF['response_requirements'],
            domain=settings.CONF['domain'],
            requirements=REQUIREMENTS
        )
        for line in data
    ]

    # Process in batches
    os.makedirs(os.path.dirname(instructions_file), exist_ok=True)
    for i in tqdm(range(0, len(tasks), batch_size), desc="Synthesizing instructions"):
        batch_tasks = tasks[i:i+batch_size]
        batch_results = await asyncio.gather(*batch_tasks)

        with open(instructions_file, 'a', encoding='utf-8') as file:
            for samples in batch_results:
                for sample in samples:
                    json.dump(sample, file, ensure_ascii=False)
                    file.write('\n')

    print(f"Instructions have been saved to {instructions_file}")
