import os
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from googleapiclient.discovery import build
from dotenv import load_dotenv
from langchain_google_community import GmailToolkit
from langchain_google_community.gmail.utils import get_gmail_credentials, build_gmail_service
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

load_dotenv()

# Global dictionary to store every user's chat history
session_histories = {}
_agent = None

@tool
def create_draft_with_resume(to: str, subject: str, body: str) -> str:
    """
    Use this tool ONLY when the user explicitly wants to draft or write a job application email. 
    It automatically creates a Gmail draft in plain text format with the user's resume (resume.pdf) 
    physically attached from the local directory.
    """
    try:
        credentials = get_gmail_credentials(
            "token.json",
            "credentials.json",
            scopes=["https://mail.google.com/"],
        )
        try:
            service = build("gmail", "v1", credentials=credentials, static_discovery=True)
        except Exception:
            service = build_gmail_service(credentials=credentials)
        
        # MIME Message creation
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        # Adding email body as plain text
        message.attach(MIMEText(body, 'plain'))
        
        # updating resume from local folder
        resume_path = "resume.pdf"
        if not os.path.exists(resume_path) and os.path.exists("Divya_AI_ML_Resume.pdf"):
            resume_path = "Divya_AI_ML_Resume.pdf"
            
        attachment_status = ""
        
        if os.path.exists(resume_path):
            with open(resume_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f"attachment; filename={os.path.basename(resume_path)}"
                )
                message.attach(part)
            attachment_status = f"and '{os.path.basename(resume_path)}' has been successfully attached"
        else:
            attachment_status = "but no resume PDF was found in the project directory."

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        # Creating a gmail draft
        if hasattr(service, "users"):
            service = service.users()
        if hasattr(service, "drafts"):
            service = service.drafts()
        if not hasattr(service, "create"):
            raise AttributeError("The provided Gmail service object does not support draft creation.")

        draft = service.create(
            userId="me",
            body={"message": {"raw": raw_message}}
        ).execute()
        
        return f"Draft created successfully (Draft ID: {draft['id']}) {attachment_status}."
        
    except Exception as e:
        return f"Error creating draft with attachment: {str(e)}"


def get_agent_instance():
    """This is used to initialize the agent only omce"""
    credentials = get_gmail_credentials(
        "token.json",
        "credentials.json",
        scopes=["https://mail.google.com/"],
    )
    try:
        api_resource = build("gmail", "v1", credentials=credentials, static_discovery=True)
    except Exception:
        api_resource = build_gmail_service(credentials=credentials)
    toolkit = GmailToolkit(api_resource=api_resource)
    
    # Adding custom tool
    gmail_tools = toolkit.get_tools()
    all_tools = gmail_tools + [create_draft_with_resume]

    # Gemini agent creation
    gmail_agent = create_agent(
        model="google_genai:gemini-2.5-flash-lite",
        tools=all_tools,
        system_prompt=(
            "You are a professional Gmail assistant. "
            "1. If the user asks you to draft or write a job application email, you MUST use the 'create_draft_with_resume' tool. "
            "Formulate the email body professionally in plain text. "
            "CRITICAL: Do NOT include any resume links, URLs, or Google Drive placeholders in the email body. "
            "The resume will be physically attached to the email by the tool automatically. "
            "Once the draft is created using 'create_draft_with_resume', confirm clearly to the user. "
            "2. If the user asks general questions (like 'how long will it take?', 'hello', etc.), "
            "DO NOT call any Gmail tools. Just answer them naturally and conversationally based on the chat history."
        )
    )
    return gmail_agent

def run_gmail_agent(user_id: int, user_message: str) -> str:
    """
    Runs gemini agent by taking user message and user ID 
    """
    global _agent
    if _agent is None:
        _agent = get_agent_instance()

    if user_id not in session_histories:
        session_histories[user_id] = []

    session_histories[user_id].append(HumanMessage(content=user_message))

    response = _agent.invoke({
        "messages": session_histories[user_id]
    })

    session_histories[user_id] = response["messages"]

    last_message = response["messages"][-1]
    reply_text = ""
    
    if hasattr(last_message, "content_blocks") and last_message.content_blocks:
        blocks = last_message.content_blocks
        if isinstance(blocks, list) and len(blocks) > 0:
            first_block = blocks
            if isinstance(first_block, dict):
                reply_text = first_block.get("text", "")
            elif isinstance(first_block, str):
                reply_text = first_block
                
    if not reply_text and hasattr(last_message, "content") and last_message.content:
        reply_text = last_message.content
        
    if not reply_text:
        reply_text = "No response from AI Agent."

    return reply_text
