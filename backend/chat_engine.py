import os
from groq import Groq
from .knowledge_base import kb
from dotenv import load_dotenv

load_dotenv()

# Configure Groq
api_key = os.getenv("GROQ_API_KEY")
if api_key:
    client = Groq(api_key=api_key)
else:
    client = None
    print("WARNING: GROQ_API_KEY not found in .env")

class ChatEngine:
    def __init__(self):
        self.system_prompt = """You are the AI Sales and Support agent for Nexova. 
        Your goal is to answer questions about Nexova based ONLY on the provided context.
        Be helpful, professional, and concise. 
        If the answer is not in the context, say: "I don't have that info, but I can connect you to a human agent."
        """

    async def get_response(self, user_message: str) -> str:
        # 1. Retrieve context
        context = kb.search(user_message)
        
        # 2. Construct prompt
        system_instructions = """You are the AI Sales Agent for Nexova.
        Your goal is to answer questions about Nexova based ONLY on the provided context.
        Be helpful, professional, and concise.
        """

        messages = [
            {"role": "system", "content": f"{system_instructions}\n\nContext:\n{context}"},
            {"role": "user", "content": user_message}
        ]

        if not client:
            return "Error: AI is not configured (Missing Groq API Key)."

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=1024
            )
            return response.choices[0].message.content
                
        except Exception as e:
            print(f"Groq Error: {e}")
            return "I'm having trouble connecting to my brain right now. Please try again."
chat_engine = ChatEngine()
