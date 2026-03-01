
import gradio as gr
from basic_agent_functions import agent_chat

gr.ChatInterface(agent_chat).launch()