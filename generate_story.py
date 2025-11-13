import json
from pathlib import Path
import os
from typing import List

from pydantic import BaseModel, Field
from pydantic_ai import Agent, NativeOutput
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

import config


STORY_CODE = 'forest-of-dead-dreams-jp-ml'
OUTPUT_FILE = Path('web') / 'stories' / f'{STORY_CODE}.json'
print(STORY_CODE)

PROMPT = """
    Generate an interactive fiction story with 25 scenes (called nodes hereafter).
    The nodes will be modeled as a graph and you are required to generate the list of nodes with actions acting as directed edges of the graph.
    Once you generate, I will programmatically evaluate the graph for the following constraints:
    - Start Node is the node with id=1. This is where the story begins. Only the start node maybe not linked to from any other node. 
    - All other nodes have to be linked to by at least one other node.
    - Any node that doesn´t link to others is an ´end node´. These are endpoints for the story.
    - Every node that is not a start node or an end node must have a path from the start node, and a path to an end node.
    Once the outline is programmatically checked for validity, the story at each node will be populated later.
    
    In the story, there must be no temporal elements (such as night and day) and no state changes to keep track of, like the player acquiring any objects.
    Keep the narrative coherent for multiple visits to the same node from various different nodes.

    Generate the story in Japanese Romaji script with Malayalam translations.
    This is for a Malayalam speaker to learn Japanese.
    Keep the word order of Malayalam translations similar to the Japanese sentence as mcuh as grammar allows.
    This will enable the reader to learn Japanese by mapping the translated words 1-1 with the original text.
    Make sure to translate the particles appearing in Japanese to their respective postpositions in the Malayalam words.
    
    The story must be themed around the phrase: Forest of Dead Dreams.
    Keep the content at each node about 10 sentences long. Avoid unnecessary descriptions, include only facts useful to navigate the story.
    Each node may have upto 5 actions.
"""


class Text(BaseModel):
    text_l1: str = Field(description='An text unit of the story in Japanese Romaji')
    text_l2: str = Field(description='Translated text in Malayalam; use Unicode Malayalam script, keep the words in original Japanese order as much as possible while still being gramatically correct.')


class Action(BaseModel):
    action_text: Text = Field(description='Action that can be taken by the player')
    destination_id: int = Field(description='The node that this action links to')


class Node(BaseModel):
    id: int = Field(description='A unique numeric id for this node use as a reference for actions in other nodes to link to.')
    title: Text = Field(description='Title of the scene at this node')
    texts: List[Text] = Field(description='List of text chunks describing the scene at this node and prompting for user action.')
    actions: List[Action] = Field(description='List of 1-5 named actions linking to other nodes.')


class InteractiveStory(BaseModel):
    title: Text = Field(description='Title of the story')
    nodes: List[Node] = Field(description='List of nodes in the interactive story each with their attributes')


attempt_count = 0
while True:
    attempt_count += 1
    print('Attempt No.:', attempt_count)
    
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
    result = json.loads(ai_result.output.model_dump_json())

    # Checking graph validity
    node_dict = { node['id']: node for node in result['nodes'] }
    
    visited_nodes = set()
    graph_valid = True
    
    to_visit = [1]
    while to_visit:
        dest_id = to_visit.pop(0)
        visited_nodes.add(dest_id)
        dest_node = node_dict.get(dest_id)
        if dest_node:
            for action in dest_node['actions']:
                if (action['destination_id'] not in visited_nodes) and (action['destination_id'] not in to_visit):
                    to_visit.append(action['destination_id'])
        else:
            graph_valid = False
            print('INVALID:', f'{node} does not exist but is referenced')
    
    
    for node in result['nodes']:
        if node['id'] not in visited_nodes:
            graph_valid = False
            print('INVALID:', f'{node["id"]} is never linked to')

    if graph_valid:
        print('VALID')
        result['prompt'] = PROMPT
        with open(OUTPUT_FILE, 'w') as f:
            f.write(json.dumps(result, indent=2))
        break
            
        

