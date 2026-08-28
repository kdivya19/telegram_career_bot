import os
from dotenv import load_dotenv  # 1. GEMINI_API_KEY from .env
from langchain_google_community import GmailToolkit
# importing build_gmail_service and get_gmail_credentials correctly
from langchain_google_community.gmail.utils import get_gmail_credentials, build_gmail_service
from langchain.agents import create_agent # [1]

# Loading env variables at script starting
load_dotenv()

# 1. logging in credentials.json
print("[INFO] గూగుల్ అథెంటికేషన్ ప్రాసెస్ స్టార్ట్ అవుతోంది...")
credentials = get_gmail_credentials(
    "token.json",        # 1st place token_file
    "credentials.json",  # 2nd place client_secrets_file
    scopes=["https://mail.google.com/"],
)
# Using deprecated build_resource_serviceinstead of build_gmail_service
api_resource = build_gmail_service(credentials=credentials)

# 2. creating Gmail Toolkit 
toolkit = GmailToolkit(api_resource=api_resource)
gmail_tools = toolkit.get_tools()

# 3. building agent with Google Gemini model
# (GEMINI_API_KEY ఉంis there in .env)
gmail_agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite", # [2]
    tools=gmail_tools,
    system_prompt=(
        "You are a professional Gmail assistant. "
        "When asked to create an email draft, strictly use the 'create_gmail_draft' tool. "
        "Do not send the email directly."
    )
)

# # 4. Test run - Creating draft using gemini
# print("[INFO] invoking the agent...")
# response = gmail_agent.invoke({
#     "messages": [
#         {"role": "user", "content": "Draft an email to hr@google.com applying for Python Developer position."}
#     ]
# })

# print("\n--- Agent Execution Output ---")
# print(response["messages"][-1].content_blocks)


# 4. Test run - Creating draft using geminiం
print("[INFO] ఏజెంట్ ని ఇన్వోక్ చేస్తున్నాం...")
response = gmail_agent.invoke({
    "messages": [
        {
            "role": "user", 
            # changing prompt more strictly
            "content": (
                "Draft an email to hr@google.com applying for Python Developer position. "
                "Use placeholders like [My Name] for any missing information and "
                "call the tool to create the draft immediately without asking me any questions."
            )
        }
    ]
})

print("\n--- Agent Execution Output ---")
print(response["messages"][-1].content_blocks)
