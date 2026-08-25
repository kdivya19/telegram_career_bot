import os
from dotenv import load_dotenv  # 1. .env లోని GEMINI_API_KEY ని లోడ్ చేయడానికి
from langchain_google_community import GmailToolkit
# build_gmail_service మరియు get_gmail_credentials లను కరెక్ట్ గా ఇంపోర్ట్ చేసాము
from langchain_google_community.gmail.utils import get_gmail_credentials, build_gmail_service
from langchain.agents import create_agent # [1]

# స్క్రిప్ట్ ప్రారంభంలోనే ఎన్విరాన్‌మెంట్ వేరియబుల్స్ ని లోడ్ చేస్తున్నాం
load_dotenv()

# 1. credentials.json ఉపయోగించి లాగిన్ పర్మిషన్ పొందడం
print("[INFO] గూగుల్ అథెంటికేషన్ ప్రాసెస్ స్టార్ట్ అవుతోంది...")
credentials = get_gmail_credentials(
    "token.json",        # మొదటి స్థానంలో token_file
    "credentials.json",  # రెండో స్థానంలో client_secrets_file
    scopes=["https://mail.google.com/"],
)
# డిప్రెకేట్ అయిన build_resource_service కి బదులుగా కొత్త build_gmail_service ని వాడుతున్నాం
api_resource = build_gmail_service(credentials=credentials)

# 2. Gmail Toolkit క్రియేట్ చేయడం
toolkit = GmailToolkit(api_resource=api_resource)
gmail_tools = toolkit.get_tools()

# 3. Google Gemini మోడల్ తో ఏజెంట్ ని బిల్డ్ చేయడం [2]
# (మీ .env లో GEMINI_API_KEY ఉందని నిర్ధారించుకోండి)
gmail_agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite", # [2]
    tools=gmail_tools,
    system_prompt=(
        "You are a professional Gmail assistant. "
        "When asked to create an email draft, strictly use the 'create_gmail_draft' tool. "
        "Do not send the email directly."
    )
)

# # 4. టెస్ట్ రన్ - జెమిని ద్వారా డ్రాఫ్ట్ క్రియేట్ చేయడం
# print("[INFO] ఏజెంట్ ని ఇన్వోక్ చేస్తున్నాం...")
# response = gmail_agent.invoke({
#     "messages": [
#         {"role": "user", "content": "Draft an email to hr@google.com applying for Python Developer position."}
#     ]
# })

# print("\n--- Agent Execution Output ---")
# print(response["messages"][-1].content_blocks)


# 4. టెస్ట్ రన్ - జెమిని ద్వారా డ్రాఫ్ట్ క్రియేట్ చేయడం
print("[INFO] ఏజెంట్ ని ఇన్వోక్ చేస్తున్నాం...")
response = gmail_agent.invoke({
    "messages": [
        {
            "role": "user", 
            # ప్రాంప్ట్ ని మరింత స్పష్టంగా మార్చాము
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