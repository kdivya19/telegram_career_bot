# import os
# from dotenv import load_dotenv
# from langchain_google_community import GmailToolkit
# from langchain_google_community.gmail.utils import get_gmail_credentials, build_gmail_service
# from langchain.agents import create_agent
# from langchain_core.messages import HumanMessage, AIMessage

# load_dotenv()

# # ప్రతి యూజర్ యొక్క చాట్ హిస్టరీని సేవ్ చేయడానికి గ్లోబల్ డిక్షనరీ
# session_histories = {}
# _agent = None

# def get_agent_instance():
#     """this helps to initialize the agent only once"""
#     credentials = get_gmail_credentials(
#         "token.json",
#         "credentials.json",
#         scopes=["https://mail.google.com/"],
#     )
#     api_resource = build_gmail_service(credentials=credentials)
#     toolkit = GmailToolkit(api_resource=api_resource)
#     gmail_tools = toolkit.get_tools()

#     # జెమిని ఏజెంట్ క్రియేషన్ [1]
#     gmail_agent = create_agent(
#         model="google_genai:gemini-2.5-flash-lite", # [1]
#         tools=gmail_tools,
#         system_prompt=(
#             "You are a professional Gmail assistant and a helpful conversational companion. "
#             "1. If the user explicitly asks you to draft or write an email, strictly use the 'create_gmail_draft' tool. "
#             "Use placeholders like [My Name] for any missing information and call the tool immediately. "
#             "Once the draft is created, clearly confirm to the user that the draft has been created in their Gmail. "
#             "2. If the user asks general questions (like 'how long will it take?', 'who are you?', 'hello', etc.), "
#             "DO NOT call any Gmail tools. Just answer them naturally, politely, and conversationally based on the chat history."
#         )
#     )
#     return gmail_agent

# def run_gmail_agent(user_id: int, user_message: str) -> str:
#     """
#     takes the user id and message and maintains the short term memory of the gemini-agent
#     """
#     global _agent
#     if _agent is None:
#         _agent = get_agent_instance()

#     # 1. ఒకవేళ ఈ యూజర్ కి హిస్టరీ లేకపోతే కొత్తగా క్రియేట్ చేయాలి
#     if user_id not in session_histories:
#         session_histories[user_id] = []

#     # 2. కొత్త యూజర్ మెసేజ్ ని హిస్టరీ కి యాడ్ చేయాలి
#     session_histories[user_id].append(HumanMessage(content=user_message))

#     # 3. పూర్తి హిస్టరీ ని ఏజెంట్ కి పంపాలి
#     response = _agent.invoke({
#         "messages": session_histories[user_id]
#     })

#     # 4. అప్‌డేట్ అయిన పూర్తి హిస్టరీ ని సేవ్ చేయాలి
#     session_histories[user_id] = response["messages"]

#     # 5. చివరి మెసేజ్ నుండి సురక్షితంగా రిప్లై టెక్స్ట్ ని ఎక్స్‌ట్రాక్ట్ చేయడం [1]
#     last_message = response["messages"][-1]
#     reply_text = ""
    
#     # content_blocks లోపల మొదటి ఎలిమెంట్ ని  ఇండెక్స్ ద్వారా కరెక్ట్ గా యాక్సెస్ చేస్తున్నాం
#     if hasattr(last_message, "content_blocks") and last_message.content_blocks:
#         blocks = last_message.content_blocks
#         if isinstance(blocks, list) and len(blocks) > 0:
#             first_block = blocks  # ఇక్కడ ఇండెక్స్  సరిగ్గా యాడ్ చేసాను!
#             if isinstance(first_block, dict):
#                 reply_text = first_block.get("text", "")
#             elif isinstance(first_block, str):
#                 reply_text = first_block
                
#     # ఒకవేళ పైన లాజిక్ ద్వారా టెక్స్ట్ రాకపోతే .content ని వాడుతుంది
#     if not reply_text and hasattr(last_message, "content") and last_message.content:
#         reply_text = last_message.content
        
#     if not reply_text:
#         reply_text = "No response from AI Agent."

#     return reply_text




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

# ప్రతి యూజర్ యొక్క చాట్ హిస్టరీని సేవ్ చేయడానికి గ్లోబల్ డిక్షనరీ
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
        
        # MIME Message క్రియేషన్
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        
        # ఇమెయిల్ బాడీని ప్లెయిన్ టెక్స్ట్ లాగా యాడ్ చేస్తున్నాం (లింకులు ఉండవు)
        message.attach(MIMEText(body, 'plain'))
        
        # లోకల్ ఫోల్డర్ నుండి resume.pdf ని అటాచ్ చేస్తున్నాం
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
        
        # జీమెయిల్ డ్రాఫ్ట్ క్రియేట్ చేయడం
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
    """ఏజెంట్ ని కేవలం ఒక్కసారి మాత్రమే ఇనిషియలైజ్ చేయడానికి సహాయపడుతుంది"""
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
    
    # కస్టమ్ టూల్ ని యాడ్ చేస్తున్నాం
    gmail_tools = toolkit.get_tools()
    all_tools = gmail_tools + [create_draft_with_resume]

    # జెమిని ఏజెంట్ క్రియేషన్ (లింకులు లేకుండా కఠినమైన రూల్స్ తో)
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
    యూజర్ ఐడీ మరియు మెసేజ్ ని తీసుకుని, షార్ట్-టర్మ్ మెమొరీని 
    మెయింటైన్ చేస్తూ జెమిని ఏజెంట్ ని రన్ చేస్తుంది.
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