import re
import argparse

from pathlib import Path
from datetime import datetime
from bs4 import BeautifulSoup

from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain_core.messages import SystemMessage

    
def html_process(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Add max size of images
    style_tag = soup.new_tag("style")
    style_tag.string = '''
        img{
            max-height:300px;
            max-width:300px;
            height:auto;
            width:auto;
        }
    '''
    soup.find("head").append(style_tag)
    
    # Replace image source to a placeholder image
    for img in soup.find_all("img"):
        img["src"] = "../../../assets/placeholder.png"

    result = soup.prettify()
    return result

def select_comments(text):
    """
    Get the content that before ``` ```
    """
    match = re.search(rf"(.*?)```(.*?)```", text, re.DOTALL)
    if match:
        return match.groups()[0]
    else:
        return False

def select_code_block(text):
    """
    Get the content that wraped by ``` ``` from the input text
    """
    match = re.search(rf"```(.*?)\n(.*?)```", text, re.DOTALL)
    if match:
        return match.groups()[1]
    else:
        return False

def get_system_message():
    message = SystemMessage(content='''
You're an expert of mobile UI/UX design.
You are familiar with HTML and CSS.
You know every detail of Material Design.
You should import the CDN <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet"/>.
The size of the mobile screen is 667x375.
'''
    )
    return message

def get_description_refinement_template():
    template = '''
Please refine the following mobile app page description into several UI sections.
Be careful, you should only give the UI sections of one single page. It should not contain too many sections.
For each section, give as much detail as possible. 
You could also give the example item for each section.

Page description:
```
{page_description}
```
    '''
    prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template=template,
            input_variables=["page_description"],
        )
    )
    prompt_template = ChatPromptTemplate.from_messages([get_system_message(), prompt])
    return prompt_template

def get_html_generation_template():
    template = '''
Please create the HTML code for a mobile app page according to the following description.

```
{page_description}
```
    '''
    prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template=template,
            input_variables=["page_description"],
        )
    )
    prompt_template = ChatPromptTemplate.from_messages([get_system_message(), prompt])
    return prompt_template

def get_html_edit_template():
    template = '''
Please edit the given HTML code based on the following instruction:

Instruction:
```
{edit_instruction}
```

```html
{html_code}
```
You should give me the full modified HTML code.
    '''
    prompt = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template=template,
            input_variables=["html_code", "edit_instruction"],
        )
    )
    prompt_template = ChatPromptTemplate.from_messages([get_system_message(), prompt])
    return prompt_template

def html_generation(prompt):
    chat_model = ChatOpenAI(model_name = "gpt-4o", temperature=1)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    output_path = Path(f"./output/{prompt}/{timestamp}").resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    log_path = output_path.joinpath("log.md")
    html_path = output_path.joinpath(f"init.html")
    
    description_refinement_prompt_template = get_description_refinement_template()
    desc_chain = LLMChain(llm=chat_model, prompt=description_refinement_prompt_template)
    desc_output = desc_chain.predict(page_description=prompt)
    with open(log_path, 'a') as f: 
        f.write(desc_output)

    html_generation_prompt_template = get_html_generation_template()
    html_chain = LLMChain(llm=chat_model, prompt=html_generation_prompt_template)
    html_output = html_chain.predict(page_description=desc_output)
    with open(log_path, 'a') as f: 
        f.write("\n\n=================================================================\n")
        f.write(html_output)
    html_output = select_code_block(html_output)
    with open(html_path, 'w') as f:
        html_output = html_process(html_output)
        f.write(html_output)
    
    return html_output, html_path

def html_edit(prompt, html_code):
    chat_model = ChatOpenAI(model_name = "gpt-4o", temperature=1)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    output_path = Path(f"./output/{prompt}/{timestamp}").resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    log_path = output_path.joinpath("log.md")
    html_path = output_path.joinpath(f"updated.html")
    
    html_edit_prompt_template = get_html_edit_template()
    html_chain = LLMChain(llm=chat_model, prompt=html_edit_prompt_template)
    html_output = html_chain.predict(html_code=html_code, edit_instruction=prompt)

    with open(log_path, 'a') as f: 
        f.write("\n\n=================================================================\n")
        f.write(html_output)
    html_output = select_code_block(html_output)
    with open(html_path, 'w') as f:
        html_output = html_process(html_output)
        f.write(html_output)
    
    return html_output, html_path

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--page_description", default="a user write an email")
    args = parser.parse_args()
        
    html_generation(args.page_description)
