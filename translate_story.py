import json
from pathlib import Path
import os
from typing import List

from pydantic import BaseModel, Field
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

import config


INPUT_STORY_CODE = 'bus-detour'
OUTPUT_STORY_CODE = 'bus-detour-ka-ta'
TRANSLATION_PROMPT = 'Translate the following text into Kannada and Tamil separately with both results having a similar word order. This is for a Tamil speaker to learn Kannada by example.'
L1_FIELD_DESCRIPTION = 'The text translated into Kannada'
L2_FIELD_DESCRIPTION = 'The text translated into Tamil with same word order as the Kannada Translation'

INPUT_FILE = Path('web') / 'stories-mono' / f'{INPUT_STORY_CODE}.json'
OUTPUT_FILE = Path('web') / 'stories' / f'{OUTPUT_STORY_CODE}.json'


class TranslatedText(BaseModel):
    text_l1: str = Field(description=L1_FIELD_DESCRIPTION)
    text_l2: str = Field(description=L2_FIELD_DESCRIPTION)


ai_agent = Agent(
    OpenAIChatModel(
        config.OPENAI_API_MODEL,
        provider = OpenAIProvider(
            api_key = config.OPENAI_API_KEY,
            base_url = config.OPENAI_API_BASE_URL,
        )
    ),
    output_type = NativeOutput(TranslatedText),
)


def translate_text(text: str):
    PROMPT = '\n'.join([TRANSLATION_PROMPT, 'The text is:', text])
    ai_result = ai_agent.run_sync(PROMPT)
    result = json.loads(ai_result.output.model_dump_json())
    print(result)
    return result


story = json.loads(open(INPUT_FILE).read())

story['title'] = translate_text(story['title'])

for node in story['nodes']:
    node['texts'] = [translate_text(t) for t in node['texts']]
    for action in node['actions']:
        action['action_text'] = translate_text(action['action_text'])

with open(OUTPUT_FILE, 'w') as f:
    f.write(json.dumps(story, indent=2))


