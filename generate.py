import json
from pathlib import Path
import os
from typing import List

from pydantic import BaseModel, Field
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

import config


OUTPUT_DIR = Path('web') / 'stories'
OUTPUT_FILE = OUTPUT_DIR / 'welcome-to-tokyo.json'


PROMPT = """
    Generate an interactive fiction story with 50 scenes (called nodes hereafter).
    Each Node will have a description presented line-by-line, and 1 - 4 'actions' that will link to other nodes.
    For each bit of any kind of text generate, you will be providing the texts in Japanese Romaji and Old Kannada
    For Kannada translations, use Old Mysore colloquial Kannada.
    This story is for a language learner to study Japanese using Kannada, so try to keep the word order in Japanese
    and the translated word order in Kannada the same as much as possible, so that they map 1-1.

    The story must be set in Tokyo city and the player must be a character visiting Tokyo for the first time.
    The story will be titled something like 'Welcome To Tokyo'
    Keep each scene around 10 sentences long, but make each sentence relevant and important. Avoid unnecessary verbose descriptions.
"""


class Text(BaseModel):
    text_l1: str = Field(description='An text unit of the story in Japanese Romaji')
    text_l2: str = Field(description='Translated text in Kannada, retaining word original Japanese order as much as possible while still being gramatically correct.')


class Action(BaseModel):
    action_text: Text = Field(description='Action that can be taken by the player')
    destination_id: int = Field(description='The node that this action links to')


class Node(BaseModel):
    id: int = Field(description='A unique numeric id for this node use as a reference for actions in other nodes to link to.')
    title: Text = Field(description='Title of the scene at this node')
    texts: List[Text] = Field(description='List of text chunks describing the scene at this node and prompting for user action.')
    actions: List[Action] = Field(description='List of 1-3 named actions linking to other nodes.')


class InteractiveStory(BaseModel):
    title: Text = Field(description='Title of the story')
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
    output = json.loads(ai_result.output.model_dump_json())
    output['prompt'] = PROMPT
    f.write(json.dumps(output, indent=2))
