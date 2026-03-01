import json
from openai import OpenAI
from send_email import send_email
from tools import record_unknown_question_json, record_user_details_json
from system_prompts import system_prompt, evaluator_system_prompt
from models import Evaluation
from dotenv import load_dotenv
import os


load_dotenv(override=True)

openai_api_key = os.getenv("OPENAI_API_KEY")

if openai_api_key:
    print("OPENAI_API_KEY is set")
else:
    print("OPENAI_API_KEY is not set")
openai_python_client = OpenAI(api_key=openai_api_key)

def agent_chat(message, history):
    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": message}]
    done = False
    tools = [{"type": "function", "function": record_user_details_json},
        {"type": "function", "function": record_unknown_question_json}]
    while not done:

        # This is the call to the LLM - see that we pass in the tools json

        response = openai_python_client.chat.completions.create(model="gpt-4o-mini", messages=messages, tools=tools)

        finish_reason = response.choices[0].finish_reason
        
        # If the LLM wants to call a tool, we do that!
         
        if finish_reason=="tool_calls":
            message = response.choices[0].message
            tool_calls = message.tool_calls
            results = handle_tool_calls(tool_calls)
            messages.append(message)
            messages.extend(results)
        else:
            done = True
    return response.choices[0].message.content


def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt


def evaluate(reply, message, history) -> Evaluation:
    messages = [{"role": "system", "content": evaluator_system_prompt}] + [{"role": "user", "content": evaluator_user_prompt(reply, message, history)}]
    response = openai_python_client.chat.completions.parse(model="gpt-4o-mini", messages=messages, response_format=Evaluation)
    return response.choices[0].message.parsed


def rerun(reply, message, history, feedback):
    updated_system_prompt = system_prompt + "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = [{"role": "system", "content": updated_system_prompt}] + history + [{"role": "user", "content": message}]
    response = openai_python_client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    return response.choices[0].message.content

def handle_tool_calls(tool_calls):
    results = []
    for tool_call in tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        print(f"Tool called: {tool_name}", flush=True)
        if tool_name == "record_user_details":
            result = record_user_details(**arguments)
        elif tool_name == "record_unknown_question":
            result = record_unknown_question(**arguments)

        results.append({"role": "tool","content": json.dumps(result),"tool_call_id": tool_call.id})
    return results

def record_user_details(email, name="Name not provided", notes="not provided"):
    send_email(name, email, "Intrest in your profile")
    return {"recorded": "ok"}

def record_unknown_question(question):
    send_email("siddardha.vangala", "siddardhavangala@gmail.com", f"This question couldnt be answered {question}")
    return {"recorded": "ok"}