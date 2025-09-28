from llama_index.core import PromptTemplate
from llama_index.llms.openai import OpenAI
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex
import json
import re
import os

API_HOST = "127.0.0.1"
API_PORT = 5005
API_URL = f"http://{API_HOST}:{API_PORT}/v1/chat/completions"
ADDITIONAL_LLM_INSTRUCTION = "" # Can be "/no_think" for QWEN thinking models, so they don't output thinking tags (which breaks the pptx generator).

prompt = """
 You are a power point presentation specialist. You are asked to create
 the content for a presentation about {topic}.
 You have been given the following information to create a presentation:
 ---
 {information}.
 ---
 Structure the information in a way that it can be put in a power point
 presentation. Each slide should have a title and content, with the content
 being a summary of the information provided. Each slide should have one or
 more sentences that capture the key points of the information.
 Return the structured information as a JSON as follows.
 Your answer should only contain the JSON - no markdown formatting.
 """

prompt_template = PromptTemplate(prompt)
prompt_examples = """
  Example:
  {"slides": [
  {"title": "Slide 1", "content": "Content for slide 1"},
  {"title": "Slide 2", "content": "Content for slide 2"},
  {"title": "Slide 3", "content": "Content for slide 3"},
  ]}
 """

test_topic = "the benefits of exercise"
test_information = """
Exercise plays a crucial role in maintaining both physical and mental health.
Engaging in regular physical activity can significantly reduce the risk of
chronic diseases such as heart disease, diabetes, and obesity. It also enhances
muscular strength, flexibility, and endurance. Beyond physical benefits, exercise
contributes to improved mental health by reducing symptoms of depression and anxiety,
boosting mood through the release of endorphins, and improving cognitive function.
It fosters a sense of well-being and can be a great way to manage stress.
Overall, incorporating exercise into one's daily routine is a key factor in
achieving a healthier and more balanced lifestyle.
"""

content_prompt = (
    prompt_template.format(topic=test_topic, information=test_information)
    + prompt_examples
)

# api_key = os.getenv("OPENAI_API_KEY")
#logger.info(api_key)
#print(api_key)
# llm = OpenAI(model="gpt-5", api_key=api_key)
# llm.complete(content_prompt, True)

