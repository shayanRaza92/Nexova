# Nexova

Nexova is an AI-powered chatbot that automates sales and customer support over WhatsApp. Instead of hiring a team to reply to every message manually, Nexova does it for you — instantly, 24/7, and always in the right tone.

You feed it your business knowledge (products, FAQs, policies), connect it to WhatsApp, and it handles customer conversations on its own. It can answer questions, take orders, and respond consistently — no matter how many people message at once.

## What It Actually Does

- A customer visits your website and types a question into the chat widget
- The AI reads your knowledge base, generates an accurate answer, and sends it back
- That same answer also gets delivered directly to the customer's WhatsApp
- If someone messages your WhatsApp number directly, the bot picks it up and auto-replies
- There's also a Telegram bot that does the same thing on Telegram

So basically, one AI brain connected to your website, WhatsApp, and Telegram — all at once.

## How It's Built

The project has two main parts:

### Backend (Python + FastAPI)

The backend is a FastAPI server that handles everything behind the scenes.

- **main.py** — Sets up the FastAPI app and enables CORS so the frontend can talk to it.
- **routes.py** — Handles incoming requests. There are three main routes:
  - `/chat` — Simple chat endpoint for the website simulator.
  - `/chat-whatsapp` — Takes a phone number and a message from the website chat widget, generates an AI response, and sends it to the customer's WhatsApp via the Whapi API.
  - `/webhook` — Receives incoming WhatsApp messages (from Whapi's webhook) and auto-replies using AI.
- **chat_engine.py** — The brain of the bot. It uses the Groq API to run a large language model (LLama 3.3 70B). When a message comes in, it searches the knowledge base for relevant context, builds a prompt, and sends it to the LLM to get a response.
- **knowledge_base.py** — A simple keyword-based search over a text file. It splits the file into paragraphs and scores them based on how many words from the user's query appear in each paragraph. The top results become the "context" that the AI uses to answer.
- **telegram_bot.py** — A standalone Telegram bot using the python-telegram-bot library. It listens for messages and responds using the same AI engine.

### Frontend (HTML + CSS + JavaScript)

The frontend is a single-page landing website.

- **index.html** — The main page with a hero section, features, how-it-works steps, testimonials, a footer, and a WhatsApp chat widget. The chat widget lets visitors enter their phone number and ask questions — the AI responds in the chat and also sends the reply to their WhatsApp.
- **styles.css** — All the styling. Dark theme with glassmorphism cards, gradient accents, smooth animations, and fully responsive design that works on phones, tablets, and desktops.
- **simulator.html** — A simpler page that looks like a WhatsApp conversation. It sends messages to the `/chat` endpoint and shows the AI's replies. Useful for quick testing.

### Data

- **data/dummy_data.txt** — The knowledge base. This is where you put all the information the AI should know about your business. Right now it has sample data about Nexova's features, how it works, success stories, and a demo food menu with prices.

## How to Set It Up

### 1. Clone the repo

```
git clone https://github.com/your-username/nexova.git
cd nexova
```

### 2. Install dependencies

Make sure you have Python 3.9+ installed, then:

```
pip install -r requirements.txt
```

### 3. Set up your API keys

Copy the example environment file and fill in your real keys:

```
cp .env.example .env
```

Then open `.env` and add:

- **GROQ_API_KEY** — Sign up at [console.groq.com](https://console.groq.com) and create an API key.
- **WHAPI_TOKEN** — Sign up at [whapi.cloud](https://whapi.cloud), connect your WhatsApp, and copy your token.
- **TELEGRAM_TOKEN** — Talk to [@BotFather](https://t.me/BotFather) on Telegram, create a bot, and copy the token.

### 4. Run the backend

```
uvicorn backend.main:app --reload
```

The API will start at `http://localhost:8000`.

### 5. Open the frontend

Just open `frontend/index.html` in your browser. The chat widget will connect to the local backend.

### 6. (Optional) Run the Telegram bot

```
python backend/telegram_bot.py
```

## Setting Up WhatsApp Webhooks

For the auto-reply feature (when someone messages your WhatsApp directly), you need to set up a webhook on Whapi:

1. Go to your [Whapi dashboard](https://panel.whapi.cloud/)
2. Set the webhook URL to your server's `/webhook` endpoint
3. For local testing, use a tunnel like [ngrok](https://ngrok.com): `ngrok http 8000`

## Project Structure

```
nexova/
├── backend/
│   ├── main.py              # FastAPI app setup
│   ├── routes.py            # API endpoints
│   ├── chat_engine.py       # AI response generation
│   ├── knowledge_base.py    # Knowledge search
│   └── telegram_bot.py      # Telegram bot
├── frontend/
│   ├── index.html           # Main landing page
│   ├── styles.css           # All styles
│   └── simulator.html       # WhatsApp chat simulator
├── data/
│   └── dummy_data.txt       # Business knowledge base
├── .env.example             # Template for API keys
├── .gitignore               # Files excluded from Git
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

## Technologies Used

| Technology | What It Does |
|---|---|
| FastAPI | Backend framework for handling API requests |
| Groq + LLama 3.3 70B | AI model for generating intelligent responses |
| Whapi.cloud | Sends and receives WhatsApp messages via API |
| python-telegram-bot | Handles Telegram bot communication |
| HTML/CSS/JavaScript | Frontend landing page and chat widget |

## Notes

- The `.env` file is in `.gitignore` so your API keys never get pushed to GitHub.
- The `.env.example` file shows what keys you need without exposing any real values.
- The knowledge base is just a plain text file — no database needed. Replace `dummy_data.txt` with your own business info.
- For production, you'd want to swap the simple keyword search with vector embeddings for better accuracy.
