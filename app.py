import os
import json
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import OpenAI
from pypdf import PdfReader
import gradio as gr

# Load environment variables from .env file
load_dotenv(override=True)

# --- Tool Implementations ---

def push(message):
    """Sends a push notification via Pushover."""
    pushover_user = os.getenv("PUSHOVER_USER")
    pushover_token = os.getenv("PUSHOVER_TOKEN")
    if not pushover_user or not pushover_token:
        print("Pushover credentials not set. Skipping notification.")
        return
    print(f"Sending push notification: {message}")
    try:
        requests.post(
            "https://api.pushover.net/1/messages.json",
            data={
                "user": pushover_user,
                "token": pushover_token,
                "message": message
            }
        )
    except requests.RequestException as e:
        print(f"Failed to send push notification: {e}")

def record_user_details(email, name="Not provided", notes="Not provided"):
    """Records user details and sends a notification."""
    push(f"New contact inquiry from {name} ({email}). Notes: {notes}")
    return {"status": "Details recorded successfully."}

def record_unknown_question(question):
    """Records a question the chatbot could not answer."""
    push(f"An unanswerable question was asked: '{question}'")
    return {"status": "Question recorded."}

# --- Tool Definitions (JSON Schema) ---

tools = [
    {
        "type": "function",
        "function": {
            "name": "record_user_details",
            "description": "Use this tool to record a user's contact details if they want to get in touch.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {"type": "string", "description": "The user's email address."},
                    "name": {"type": "string", "description": "The user's name."},
                    "notes": {"type": "string", "description": "Contextual notes from the conversation."}
                },
                "required": ["email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "record_unknown_question",
            "description": "Use this tool to record a question that could not be answered from the provided context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The exact question that could not be answered."}
                },
                "required": ["question"]
            }
        }
    }
]

# --- Main Application Class ---

class PersonalAI:
    def __init__(self):
        self.openai_client = OpenAI()
        self.name = "Jules Cesar Junior NDAYISENGA"

        self.knowledge_dir = "me/"
        # Create the directory if it doesn't exist
        if not os.path.exists(self.knowledge_dir):
            os.makedirs(self.knowledge_dir)
            print(f"Created directory: {self.knowledge_dir}")
        self.knowledge_context = self._load_knowledge_base(self.knowledge_dir)

        self.system_prompt = self._construct_system_prompt()

    def _scrape_text_from_url(self, url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for item in soup(['script', 'style']):
                item.decompose()
            return ' '.join(line.strip() for line in soup.get_text().splitlines() if line.strip())
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return ''

    def _load_knowledge_base(self, directory):
        print("Loading knowledge base...")
        full_context = []
        url_list_file = os.path.join(directory, "links.txt")

        for filename in os.listdir(directory):
            if filename.endswith('.pdf'):
                path = os.path.join(directory, filename)
                try:
                    reader = PdfReader(path)
                    pdf_text = ''.join(page.extract_text() or '' for page in reader.pages)
                    full_context.append(f'--- Content from {filename} ---\n{pdf_text}')
                    print(f'Loaded PDF: {filename}')
                except Exception as e:
                    print(f'Error reading {filename}: {e}')

        if os.path.exists(url_list_file):
            with open(url_list_file, 'r') as f:
                for url in (line.strip() for line in f if line.strip()):
                    print(f'Scraping: {url}')
                    if (scraped_text := self._scrape_text_from_url(url)):
                        full_context.append(f'--- Content from {url} ---\n{scraped_text}')
        
        print("--- Knowledge Base loading complete. ---")
        return '\n\n'.join(full_context)

    def _construct_system_prompt(self):
        return f"""You are a helpful AI assistant acting as {self.name}, representing him on his personal website. Your persona is professional, confident, and thoughtful.\n\nYour primary goal is to answer questions about {self.name}'s career, background, and skills using the provided context. Speak in the first person ('I').\n\n**Rules & Capabilities:**\n1.  **Grounded Answers:** Base your answers strictly on the context provided below. Do not invent information.\n2.  **Tool for Unknown Questions:** If you cannot answer a question from the context, you MUST use the `record_unknown_question` tool. Then, inform the user that you don't have the information.\n3.  **Tool for Contact:** If the user expresses interest in getting in touch, ask for their email, name, and any relevant notes, then use the `record_user_details` tool to capture this information.\n4.  **Polite Refusal:** Do not answer questions that are unrelated to {self.name}'s professional life. Politely decline and steer the conversation back to professional topics.\n\n--- CONTEXT ---\n{self.knowledge_context}\n--- END CONTEXT ---"""

    def _handle_tool_calls(self, tool_calls):
        tool_outputs = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)
            print(f"Executing tool: {tool_name} with args: {arguments}")

            if tool_name == "record_user_details":
                result = record_user_details(**arguments)
            elif tool_name == "record_unknown_question":
                result = record_unknown_question(**arguments)
            else:
                result = {"error": f"Tool '{tool_name}' not found."}
            
            tool_outputs.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(result)
            })
        return tool_outputs

    def chat(self, message, history):
        formatted_history = []
        for user_msg, ai_msg in history:
            formatted_history.append({"role": "user", "content": user_msg})
            formatted_history.append({"role": "assistant", "content": ai_msg})
        
        messages = [
            {"role": "system", "content": self.system_prompt},
            *formatted_history,
            {"role": "user", "content": message}
        ]

        while True:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto"
            )
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            if not tool_calls:
                return response_message.content
            
            tool_outputs = self._handle_tool_calls(tool_calls)
            messages.append(response_message)
            messages.extend(tool_outputs)

# --- Gradio Interface Launch ---

if __name__ == "__main__":
    ai_instance = PersonalAI()
    gradio_interface = gr.ChatInterface(
        ai_instance.chat,
        title="Personal AI Clone with Tools",
        description="Ask me about my professional background or ask to get in touch.",
        examples=["What is your experience with AI?", "I'd like to discuss a project with you, can I leave my email?"]
    )
    gradio_interface.launch(server_name="0.0.0.0", share=False)
