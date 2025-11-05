from dotenv import dotenv_values

env = dotenv_values('.env')

OPENAI_API_BASE_URL = env['OPENAI_API_BASE_URL']
OPENAI_API_KEY = env['OPENAI_API_KEY']
OPENAI_API_MODEL = env['OPENAI_API_MODEL']
