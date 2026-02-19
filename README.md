# Nexova

Nexova is an AI-powered chatbot that automates sales and customer support over WhatsApp. Instead of hiring a team to reply to every message manually, Nexova does it for you — instantly, 24/7, and always in the right tone.

You feed it your business knowledge (products, FAQs, policies), connect it to WhatsApp, and it handles customer conversations on its own. It can answer questions, take orders, and respond consistently — no matter how many people message at once.

## What It Actually Does

- A customer visits your website and types a question into the chat widget
- The AI reads your knowledge base, generates an accurate answer, and sends it back
- That same answer also gets delivered directly to the customer's WhatsApp
- If someone messages your WhatsApp number directly, the bot picks it up and auto-replies

One AI brain connected to your website and WhatsApp — all at once.

## How It's Built

The project uses n8n (a workflow automation tool) as its backend instead of traditional server code. Two n8n workflows handle all the logic — no Python server needed.

### n8n Workflows (The Backend)

Everything that used to be Python code is now visual n8n workflows.

**Workflow 1: Website Chat to WhatsApp**
- Receives a message from the website chat widget via webhook
- Searches the knowledge base for relevant context
- Sends the context + question to Groq's AI (LLama 3.3 70B) for a response
- Delivers the AI response to the customer's WhatsApp via Meta's WhatsApp Cloud API
- Returns the response back to the website chat widget

**Workflow 2: WhatsApp Auto-Reply**
- Receives incoming WhatsApp messages via Meta's webhook
- Parses the message and sender's phone number
- Searches the knowledge base and generates an AI response
- Sends the reply back to the customer on WhatsApp automatically

Both workflows are exported as JSON in the `n8n-workflows/` folder so they can be version-controlled and imported on any machine.

### Meta Proxy (meta_proxy.js)

A small Node.js script that sits between Meta and n8n. It handles Meta's webhook verification (a GET request) and forwards incoming WhatsApp messages (POST requests) to n8n. This is needed because n8n's webhook node doesn't handle Meta's verification challenge on its own.

### Frontend (HTML + CSS + JavaScript)

The frontend is a single-page landing website.

- **index.html** — The main page with a hero section, features, how-it-works steps, testimonials, a footer, and a WhatsApp chat widget. The chat widget lets visitors enter their phone number and ask questions — the AI responds in the chat and also sends the reply to their WhatsApp.
- **styles.css** — All the styling. Dark theme with glassmorphism cards, gradient accents, smooth animations, and fully responsive design that works on phones, tablets, and desktops.
- **simulator.html** — A simpler page that looks like a WhatsApp conversation. Useful for quick testing.

### Data

- **data/dummy_data.txt** — The knowledge base. This is where you put all the information the AI should know about your business. Right now it has sample data about Nexova's features, how it works, success stories, and a demo food menu with prices.

## How to Set It Up

### 1. Clone the repo

```
git clone https://github.com/your-username/nexova.git
cd nexova
```

### 2. Install n8n

```
npm install -g n8n
```

### 3. Set up your API keys

Copy the example environment file and fill in your real keys:

```
cp .env.example .env
```

Then open `.env` and add:

- **GROQ_API_KEY** — Sign up at [console.groq.com](https://console.groq.com) and create an API key.

### 4. Set up Meta WhatsApp Cloud API

1. Go to [developers.facebook.com](https://developers.facebook.com) and create a new app
2. Add the WhatsApp product to your app
3. Generate an access token and note your Phone Number ID
4. Add your phone number as a test recipient

### 5. Start n8n and import workflows

```
n8n start
```

Then import the workflows:

```
n8n import:workflow --input=n8n-workflows/all-workflows.json
```

Open n8n at `http://localhost:5678`, go into each workflow, and add your credentials:
- Groq API key (as a Header Auth credential)
- Meta WhatsApp access token (as a Header Auth credential)
- Update the Phone Number ID in the WhatsApp HTTP Request URL

### 6. Start the Meta proxy

```
node meta_proxy.js
```

### 7. Expose your local server (for WhatsApp auto-reply)

```
npm install -g ngrok
ngrok http 3001
```

Then set the ngrok URL as your webhook callback in the Meta Developer Dashboard.

### 8. Open the frontend

Just open `frontend/index.html` in your browser. The chat widget will connect to n8n at `http://localhost:5678/webhook/chat-whatsapp`.

## Project Structure

```
nexova/
├── frontend/
│   ├── index.html           # Main landing page + chat widget
│   ├── styles.css           # All styles
│   └── simulator.html       # WhatsApp chat simulator
├── n8n-workflows/
│   └── all-workflows.json   # Exported n8n workflows
├── meta_proxy.js            # Meta webhook verification proxy
├── data/
│   └── dummy_data.txt       # Business knowledge base
├── .env.example             # Template for API keys
├── .gitignore               # Files excluded from Git
└── README.md                # This file
```

## Technologies Used

| Technology | What It Does |
|---|---|
| n8n | Workflow automation — replaces the entire Python backend |
| Groq + LLama 3.3 70B | AI model for generating intelligent responses |
| Meta WhatsApp Cloud API | Sends and receives WhatsApp messages (free tier: 1000 conversations/month) |
| Node.js | Runs the Meta webhook verification proxy |
| HTML/CSS/JavaScript | Frontend landing page and chat widget |

## Notes

- The `.env` file is in `.gitignore` so your API keys never get pushed to GitHub.
- The `.env.example` file shows what keys you need without exposing any real values.
- The exported workflow JSON does not contain any API keys or tokens — n8n stores credentials separately in its local database.
- The knowledge base is just a plain text file — no database needed. Replace `dummy_data.txt` with your own business info.
- Meta's temporary access tokens expire every ~1 hour. For production, create a System User in Meta Business Suite to get a permanent token.
- For production, you'd want to swap the simple keyword search with vector embeddings for better accuracy.
