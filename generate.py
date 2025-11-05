from pathlib import Path
import os
from typing import List

from pydantic import BaseModel, Field
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

import config


OUTPUT_DIR = Path('outputs')
OUTPUT_FILE = OUTPUT_DIR / 'test.json'
os.makedirs(OUTPUT_DIR, exist_ok = True)


PROMPT = """
    Generate an interactive fiction story with 20 scenes (called nodes hereafter).
    Each Node will have a description presented line-by-line, and 1 - 4 'actions' that will link to other nodes.
    For each bit of any kind of text generate, you will be providing the texts in Japanese, Romaji and Kannada
    This story is for a language learner to study Japanese using Kannada, so try to keep the word order in Japanese
    and the translated word order in Kannada the same as much as possible, so that they map 1-1.
"""


class Text(BaseModel):
    text_japanese: str = Field(description='An individual phrase unit of the story')
    text_romaji: str = Field(description='Romaji representation of the text')
    text_kannada: str = Field(description='Translated text in Kannada')


class Action(BaseModel):
    text_japanese: str = Field(description='A phrase describing the action')
    text_romaji: str = Field(description='Romaji representation of the action text')
    text_kannada: str = Field(description='Translated text in Kannada')
    destination_id: int = Field(description='The node that this action links to')


class Node(BaseModel):
    id: int = Field(description='A unique numeric id for this node use as a reference for actions in other nodes to link to.')
    title_japanese: str = Field(description='Title of the scene at this node')
    title_romaji: str = Field(description='Romaji representation of the title')
    title_kannada: str = Field(description='Title translated in Kannada')
    texts: List[Text] = Field(description='List of text chunks describing the scene at this node and prompting for user action.')
    actions: List[Action] = Field(description='List of 1-3 named actions linking to other nodes.')


class InteractiveStory(BaseModel):
    title_japanese: str = Field(description='Title of the story')
    title_romaji: str = Field(description='Romaji representation of the title')
    title_kannada: str = Field(description='Title translated in Kannada')
    nodes: List[Node] = Field(description='List of nodes in the interactive story each with their attributes')

    
ai_agent = Agent(
    OpenAIChatModel(
        config.OPENAI_API_MODEL,
        provider = OpenAIProvider(
            api_key = config.OPENAI_API_KEY,
            base_url = config.OPENAI_API_BASE_URL,
        )
    ),
    output_type = NativeOutput(InteractiveStory),
)

ai_result = ai_agent.run_sync(PROMPT)
with open(OUTPUT_FILE, 'w') as f:
    f.write(ai_result.output.model_dump_json(indent=2))
