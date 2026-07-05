from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI


def get_llm() -> ChatOpenAI:
    load_dotenv()

    api_key = os.getenv("OPENROUTER_API_KEY")
    model = os.getenv("OPENROUTER_MODEL")
    temperature = float(os.getenv("OPENROUTER_TEMPERATURE", "0"))

    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set")

    if not model:
        raise ValueError("OPENROUTER_MODEL is not set")

    llm = ChatOpenAI(
        model=model,
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1",
        temperature=temperature,
    )

    return llm