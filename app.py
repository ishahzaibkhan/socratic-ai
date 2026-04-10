from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, load_prompt
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_core.runnables.config import RunnableConfig
from typing import cast
import chainlit as cl
from template import prompt_template, introduction
chat_history = []

gpt_model = "openai/gpt-oss-120b"

@cl.on_chat_start
async def on_chat_start():
    text_content = introduction

    elements = [
        cl.Text(name="👋 Welcome to Socratic AI — Your Learning Guide",
                content=text_content, display="inline")
    ]

    await cl.Message(
        content="Let's get started!",
        elements=elements
    ).send()
    model = ChatGroq(model_name=gpt_model,
                     temperature=1, streaming=True)

    template = ChatPromptTemplate.from_messages([
        ("system", prompt_template),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{question}"),
    ])

    runnable = template | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cast(Runnable, cl.user_session.get(
        "runnable"))

    msg = cl.Message(content="")
    async for chunk in runnable.astream({"question": message.content, "chat_history": chat_history}, config=RunnableConfig()):
        await msg.stream_token(chunk)
    human_chat = ("human", message.content)
    chat_history.append(human_chat)
    assistant_chat = ("assistant", msg.content)
    chat_history.append(assistant_chat)
    await msg.send()