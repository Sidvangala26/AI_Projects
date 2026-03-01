from agents import GuardrailFunctionOutput, function_tool, input_guardrail
from agents import Agent, Runner
from models import NameCheckOutput
from send_email import send_email_from_llm



@function_tool
def send_email(subject:str, body:str):
    """Send out an email with the given body"""
    send_email_from_llm(subject, body)
    return {"status": "success"}



@input_guardrail
async def guardrail_against_name(ctx, agent, message):
        guardrail_agent = Agent( 
        name="Name check",
        instructions="Check if the user is including someone's personal name in what they want you to do.",
        output_type=NameCheckOutput,
        model="gpt-4o-mini")
        result = await Runner.run(guardrail_agent, message, context=ctx.context)
        is_name_in_message = result.final_output.is_name_in_message
        return GuardrailFunctionOutput(output_info={"found_name": result.final_output},tripwire_triggered=is_name_in_message)