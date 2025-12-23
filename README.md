# 🤖 Personal AI Clone (With Tool Use)

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-green)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange)

## 🧠 Project Overview
This project builds a **Personal AI Clone** that represents me professionally 24/7. Unlike a static resume, this chatbot can answer dynamic questions about my history and **take action**.

It features a **Tool-Calling Loop** that allows the AI to:
1.  **Read my Resume/Portfolio:** Uses RAG (Retrieval-Augmented Generation) to answer questions based on my actual data.
2.  **Capture Leads:** If a recruiter wants to chat, the AI extracts their email and sends a **Real-Time Push Notification** to my phone via Pushover.
3.  **Learn:** If asked a question it doesn't know, it logs the query so I can update its knowledge base.

## 🏗️ Architecture
```mermaid
graph TD
    User[User Question] --> Chat[Gradio Interface]
    Chat --> Agent{AI Agent (GPT-4o)}
    
    subgraph Knowledge Base
    Agent -- Retrieve Context --> PDF[Resume.pdf]
    Agent -- Retrieve Context --> Web[Portfolio Website]
    end
    
    subgraph Action Tools
    Agent -- "User wants to hire?" --> Tool1[record_user_details]
    Agent -- "Don't know answer?" --> Tool2[record_unknown_question]
    Tool1 & Tool2 --> API[Pushover API]
    API --> Phone((My Phone))
    end

```

## 🛠️ Features

* **Context-Aware:** Answers strictly from provided documents (no hallucinations).
* **Function Calling:** Recognizes intent (e.g., "Contact Me") and executes Python functions.
* **Real-Time Alerts:** Integrates with Pushover for instant notifications.
* **Interactive UI:** Deployed via Gradio.

## 🚀 How to Run Locally

1. **Clone the Repo:**

```bash
git clone https://github.com/Sama-ndari/personal-ai-clone.git

```

2. **Install Deps:**

```bash
pip install -r requirements.txt

```

3. **Setup Environment:**
Create `.env`:

```bash

OPENAI_API_KEY=sk-...
PUSHOVER_USER=d...uefphbxuo9e27dfco2e8nphv8bopce...
PUSHOVER_TOKEN=...qr8eihh7xsnop8kkqq1hh8ajju7ev...x

```

4. **Add Data:**
Place your `resume.pdf` in the `me/` folder.
5. **Run:**

```bash
python app.py

```

## 🌐 How to Host on Hugging Face Spaces

This project is ready to deploy on Hugging Face for free.

1. **Create a New Space:**
* Go to [huggingface.co/spaces](https://huggingface.co/spaces) and click **"Create new Space"**.
* **Name:** `personal-ai-clone`
* **SDK:** Select **Gradio**.
* **Hardware:** CPU Basic (Free) is sufficient.


2. **Upload Files:**
* Upload `app.py`, `requirements.txt`, and your `me/` folder (containing your resume).
* *Note: Ensure your `requirements.txt` includes `openai`, `gradio`, `python-dotenv`, `requests`, `beautifulsoup4`, and `pypdf`.*


3. **Set Environment Variables (Secrets):**
* Go to your Space's **Settings** tab.
* Scroll down to **"Variables and secrets"**.
* Click **"New secret"** and add your keys one by one:
* `OPENAI_API_KEY`
* `PUSHOVER_USER`
* `PUSHOVER_TOKEN`




4. **Launch:**
* The Space will automatically build and launch. Once the status turns **"Running"**, your personal AI clone is live and accessible via the provided URL!



## 📦 Tech Stack

* **AI:** OpenAI GPT-4o-mini
* **Orchestration:** Python (Custom Tool Loop)
* **Ingestion:** `pypdf`, `BeautifulSoup`
* **Frontend:** Gradio
* **Notifications:** Pushover

---

*Created by [Samandari*](https://github.com/Sama-ndari)


