import json
from pathlib import Path

from indic_transliteration import sanscript
from indic_transliteration.sanscript import SchemeMap, SCHEMES, transliterate


INPUT_STORY_CODE = 'bus-detour-ka-ta'
OUTPUT_STORY_CODE = 'bus-detour-kalt-ta'
L1_TRANSLATE_FUNCTION = lambda x: transliterate(x, sanscript.KANNADA, sanscript.ITRANS)
L2_TRANSLATE_FUNCTION = lambda x: x


INPUT_FILE = Path('web') / 'stories' / f'{INPUT_STORY_CODE}.json'
OUTPUT_FILE = Path('web') / 'stories' / f'{OUTPUT_STORY_CODE}.json'

story = json.loads(open(INPUT_FILE).read())

story['title']['text_l1'] = L1_TRANSLATE_FUNCTION(story['title']['text_l1'])
story['title']['text_l2'] = L2_TRANSLATE_FUNCTION(story['title']['text_l2'])

for node in story['nodes']:
    node['title']['text_l1'] = L1_TRANSLATE_FUNCTION(node['title']['text_l1'])
    node['title']['text_l2'] = L2_TRANSLATE_FUNCTION(node['title']['text_l2'])

    for text in node['texts']:
        text['text_l1'] = L1_TRANSLATE_FUNCTION(text['text_l1'])
        text['text_l2'] = L2_TRANSLATE_FUNCTION(text['text_l2'])

    for action in node['actions']:
        action['action_text']['text_l1'] = L1_TRANSLATE_FUNCTION(action['action_text']['text_l1'])
        action['action_text']['text_l2'] = L2_TRANSLATE_FUNCTION(action['action_text']['text_l2'])


with open(OUTPUT_FILE, 'w') as f:
    f.write(json.dumps(story, indent=2))

