import json
from pathlib import Path
import shutil
import subprocess

from ebooklib import epub
from jinja2 import Environment, FileSystemLoader


STORY_CODE = 'arthur-clarke-lt-si-ka-2'
INPUT_FILE = Path('web') / 'stories' / f'{STORY_CODE}.json'
OUTPUT_DIR = Path('ebooks') / STORY_CODE

OUTPUT_DIR.mkdir(exist_ok=True)

env = Environment(loader=FileSystemLoader(Path('ebooks') / "_templates"))
cover_template = env.get_template('cover.html')
node_template = env.get_template('node.html')

data = json.loads(open(INPUT_FILE).read())

cover_html = cover_template.render(
    code = STORY_CODE, 
    title_l1 = data['title']['text_l1'],
    title_l2 = data['title']['text_l2'],
)
cover_path = OUTPUT_DIR / '00.html'
cover_path.write_text(cover_html)

for node in data['nodes']:
    for action in node['actions']:
        action['destination_href'] = str(action['destination_id']).zfill(2) + '.html'
    node_html = node_template.render(code=STORY_CODE, node=node)
    node_path = OUTPUT_DIR / (str(node['id']).zfill(2) + '.html')
    node_path.write_text(node_html)

epub_path = Path('ebooks') / f"{STORY_CODE}.epub"
azw3_path = Path('ebooks') / f"{STORY_CODE}.azw3"
    
book = epub.EpubBook()
book.set_title(STORY_CODE)

chapters = []
html_files = sorted(OUTPUT_DIR.glob("*.html"))
for f in html_files:
    c = epub.EpubHtml(title=f.stem, file_name=f.name, lang="en")
    c.content = f.read_text()
    book.add_item(c)
    chapters.append(c)

book.toc = chapters
book.spine = ["nav"] + chapters
book.add_item(epub.EpubNcx())
book.add_item(epub.EpubNav())

epub.write_epub(epub_path, book)


subprocess.run(["ebook-convert", epub_path, azw3_path])
shutil.rmtree(OUTPUT_DIR)