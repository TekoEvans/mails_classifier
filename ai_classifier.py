from groq import Groq
from dotenv import load_dotenv
import os
from main import *

load_dotenv()


client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_response_from_ai(mail):
    prompt = [
        # message system
        {"role": "system", "content": read_file_text("context.txt")},

        # message user
        {"role": "user", "content": f'{read_file_text("prompt.txt")} \n et voici le mail:{mail}' }
    ]

    resp = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=prompt,
        temperature=0,
        max_tokens=200,
    )

    return resp.choices[0].message.content



if __name__=="__main__":
    mails = get_mails()
    for mail in mails:
        reponse =get_response_from_ai(mail)
        print(reponse)


    