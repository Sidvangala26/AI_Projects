from langchain_core.tools import Tool

from send_email import send_email_from_llm


tool_email = Tool(
    name="send_email_notification",
    func=send_email_from_llm,
    description="useful when you want to send an email with a subject and email body"
)