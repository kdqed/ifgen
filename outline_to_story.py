import json
from pathlib import Path
import os
from typing import List

from pydantic import BaseModel, Field
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

import config


OUTLINE_CODE = 'future-space'
STORY_CODE = 'future-space-jp-ka'
OUTLINE_FILE = Path('web') / 'outlines' / f'{OUTLINE_CODE}.json'
OUTPUT_FILE = Path('web') / 'stories' / f'{STORY_CODE}.json'


def translate(text: str):
    TRANSLATION_PROMPT = '''
        Translate the text input which is Japanese Romaji into colloquial Bangalore Kannada.
        Keep the output in Kannada script
        This is for a Kannada speaker to learn Japanese.
        The Kannada text must have the same word order as the Japanese sentence as far as grammatically possible.
        Make sure the particles in the Japanese sentence appear as their equivalent postpositions in the Kannada sentences.
    '''

    class TranslatedText(BaseModel):
        text: str = Field(description = 'Input text translated as per given instructions')

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

    ai_result = ai_agent.run_sync(TRANSLATION_PROMPT)
    print(ai_result.output.text)
    return ai_result.output.text


outline = json.loads(open(OUTLINE_FILE).read())

result = {
    'title': {
        'text_l1': outline['title'],
        'text_l2': translate(outline['title'])
    }
}

with open(OUTPUT_FILE, 'w') as f:
    f.write(json.dumps(result, indent=2))

