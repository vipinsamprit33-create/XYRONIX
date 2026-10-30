import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class GroqLLM:
    def __init__(self, model="openai/gpt-oss-20b"):
        self.model = model
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found in environment."
            )

        self.client = Groq(api_key=api_key)

    def generate(self, prompt):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI assistant for NUNVIZHI, "
                        "a campus energy and traffic intelligence "
                        "platform. Use only provided evidence. "
                        "Clearly state uncertainty."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=1200
        )

        return response.choices[0].message.content or ""
