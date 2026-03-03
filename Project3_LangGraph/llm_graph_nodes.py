import random
from models import State
from langchain_openai import ChatOpenAI

def our_first_node(old_state: State) -> State:
    nouns = ["Cabbages", "Unicorns", "Toasters", "Penguins", "Bananas", "Zombies", "Rainbows", "Eels", "Pickles", "Muffins"]
    adjectives = ["outrageous", "smelly", "pedantic", "existential", "moody", "sparkly", "untrustworthy", "sarcastic", "squishy", "haunted"]
    reply = f"{random.choice(nouns)} are {random.choice(adjectives)}"
    messages = [{"role": "assistant", "content": reply}]
    new_state = State(messages=messages)
    return new_state


def chatbot_node(old_state: State) -> State:
    llm = ChatOpenAI(model="gpt-4o-mini")
    response = llm.invoke(old_state.messages)
    new_state = State(messages=[response])
    return new_state