from agents import Agent, Runner, guardrail, trace, function_tool
import asyncio
from dotenv import load_dotenv
from openai import api_key
from openai.types.responses import ResponseTextDeltaEvent
from llm_tools import guardrail_against_name, send_email
from system_prompts import  email_agent_instructions, html_instructions, instructions1, instructions2, instructions3, sales_manager_instructions, subject_instructions
import os

load_dotenv(override=True)

os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

sales_agent1 = Agent(
        name="Professional Sales Agent",
        instructions=instructions1,
        model="gpt-4o-mini",
)

sales_agent2 = Agent(
        name="Engaging Sales Agent",
        instructions=instructions2,
        model="gpt-4o-mini",
)

sales_agent3 = Agent(
        name="Busy Sales Agent",
        instructions=instructions3,
        model="gpt-4o-mini",
)

sales_picker = Agent(
    name="sales_picker",
    instructions="You pick the best cold sales email from the given options. \
Imagine you are a customer and pick the one you are most likely to respond to. \
Do not give an explanation; reply with the selected email only.",
    model="gpt-4o-mini"
)

async def stream_output():
    result = Runner.run_streamed(sales_agent1, input="Write a cold sales email")
    async for event in result.stream_events():
        if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
            print(event.data.delta, end="", flush=True)


async def parallel_llm_calls():
    message = "Write a cold sales email"

    with trace("Parallel cold emails"):
        results = await asyncio.gather(
                Runner.run(sales_agent1, message),
                Runner.run(sales_agent2, message),
                Runner.run(sales_agent3, message)
        )
    outputs = [result.final_output for result in results]
    emails = "Cold sales emails:\n\n" + "\n\nEmail:\n\n".join(outputs)
    best = await Runner.run(sales_picker, emails)
    print(f"Best sales email:\n{best.final_output}")


async def sales_manager():
        description = "Write a cold sales email"

        tool1 = sales_agent1.as_tool(tool_name="sales_agent1", tool_description=description)
        tool2 = sales_agent2.as_tool(tool_name="sales_agent2", tool_description=description)
        tool3 = sales_agent3.as_tool(tool_name="sales_agent3", tool_description=description)

        subject_writer = Agent(name="Email subject writer", instructions=subject_instructions, model="gpt-4o-mini")
        subject_tool = subject_writer.as_tool(tool_name="subject_writer", tool_description="Write a subject for a cold sales email")

        html_converter = Agent(name="HTML email body converter", instructions=html_instructions, model="gpt-4o-mini")
        html_tool = html_converter.as_tool(tool_name="html_converter",tool_description="Convert a text email body to an HTML email body")

        email_tools = [subject_tool, html_tool, send_email]
        emailer_agent = Agent(name="Email Manager",
                                        instructions=email_agent_instructions,
                                        tools=email_tools,
                                        model="gpt-4o-mini",
                                        handoff_description="Convert an email to HTML and send it")

        tools_list = [tool1, tool2, tool3]
        handoffs = [emailer_agent]
        guardrails = [guardrail_against_name]
        
        sales_manager = Agent(name="Sales Manager", instructions=sales_manager_instructions, 
                                        tools=tools_list, model="gpt-4o-mini", handoffs=handoffs,
                                        input_guardrails=guardrails)
        message = "Send a cold sales email addressed to 'Dear CEO' from Head of AI Department"
        with trace("Sales manager"):
                result = await Runner.run(sales_manager, message)

if __name__ == "__main__":
#     asyncio.run(stream_output())
#     asyncio.run(parallel_llm_calls())
        asyncio.run(sales_manager())