import groq

from web.config.utils import get_settings


def get_summary(text: str) -> str:
    client = groq.Client(api_key=get_settings().GROQ_API_KEY)
    response = client.chat.completions.create(
        model="gemma2-9b-it",
        messages=[
            {
                "role": "user",
                "content": f"Summarize the following text: {text}",
            }
        ],
    )
    return response.choices[0].message.content
