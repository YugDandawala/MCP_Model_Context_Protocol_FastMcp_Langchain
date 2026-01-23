# Currently not working need to figure out the tool use through composio

import os
from dotenv import load_dotenv
from composio import Composio
from langchain_openai import ChatOpenAI
from langchain_classic.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import StructuredTool
# Load environment variables
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

composio = Composio(api_key='ak_vWGIRo6k8XWxhlH2Le7M')
external_user_id = "pg-test-88b7b415-f1fa-4772-83f2-6e6755a99892"

print("🔗 Connecting GitHub Account...")
try:
    git_auth_request = composio.connected_accounts.link(
        user_id=external_user_id,
        auth_config_id="ac_aBQIbnM0Ugjp"
    )
    print("👉 Visit:", git_auth_request.redirect_url)
    connected_account = git_auth_request.wait_for_connection(timeout=300)
    print(f"✅ GitHub connected: {connected_account.id}")
except Exception as e:
    print(f"⚠️ GitHub connection skipped:", e)

print("📦 Fetching all MCP tools...")
raw_tools = composio.tools.get(
    user_id=external_user_id,
    toolkits=["45dd63e6-0ae7-43f9-9550-0cf3e80c09d8"]
)

# 2. MANUAL CONVERSION FUNCTION (Fixed for KeyError)
def convert_to_langchain(composio_tool_dict):
    """Wraps a Composio dict into a LangChain StructuredTool"""
    
    # Extract the identifier (try 'slug' first, then 'name')
    tool_id = composio_tool_dict.get('slug') or composio_tool_dict.get('name')
    tool_desc = composio_tool_dict.get('description', 'No description provided')

    if not tool_id:
        print(f"⚠️ Skipping tool due to missing ID: {composio_tool_dict}")
        return None

    def tool_wrapper(**kwargs):
        return composio.tools.execute(
            user_id=external_user_id,
            slug=tool_id,
            arguments=kwargs
        )

    return StructuredTool.from_function(
        func=tool_wrapper,
        name=tool_id, 
        description=tool_desc
    )

# Convert and filter out None values
mcp_tools = [convert_to_langchain(t) for t in raw_tools]
mcp_tools = [t for t in mcp_tools if t is not None]

print(f"✅ Found {len(mcp_tools)} tools in the MCP server.")
if len(mcp_tools) > 0:
    print("🛠️ Available tools:", [t.name for t in mcp_tools])

# 2. LLM SETUP
llm = ChatOpenAI(
    model="mistralai/devstral-2512:free",
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)

Prompt_template = """
You are an expert research assistant. Follow this flow:
1. Research using COMPOSIO_SEARCH_DUCK_DUCK_GO.
2. Create a PDF using TEXT_TO_PDF_CONVERT_TEXT_TO_PDF(this saves the file to internal memory).
3. Upload to GitHub using GITHUB_CREATE_OR_UPDATE_FILE_CONTENTS(this sends the saved file to the repo).

GITHUB CONFIGURATION:
- Owner: {github_owner}
- Repo: {github_repo}
- Path: {file_path}
- Commit Message: {commit_message}

Use this EXACT format:
You have access to all the following tools {tool_names} : {tools}
Thought: [Your reasoning]
Action: [tool_name]
Action Input: [JSON object with arguments]
Observation: [Tool output]
... (repeat as needed)
Thought: I have uploaded the file.
Final Answer: [Summary of what you did]

Question: {input}
Thought: {agent_scratchpad}
"""
prompt = PromptTemplate.from_template(Prompt_template)

# 4. AGENT INITIALIZATION
agent = create_react_agent(llm, mcp_tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=mcp_tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=8 # Increased iterations for complex multi-tool tasks
)

# 5. EXECUTION
topic = input("Enter research topic: ").strip()

try:
    result = agent_executor.invoke({
        "input": f"Research '{topic}' and upload the PDF report.",
        "github_owner": "YugDandawala",
        "github_repo": "AI-Podcast-Assistant",
        "file_path": "Topic_Report.pdf",
        "commit_message": "Topic report PDF file added"
    })
    print("\n✅ DONE:", result["output"])
except Exception as e:
    print(f"\n❌ Error: {e}")
# from google import genai

# # Use your actual API key here
# client = genai.Client(api_key="AIzaSyBHYrkZ8qi_J4uuYBSZlzVXxBDI_q8dLlU")

# print("Models supporting generateContent:")
# # Iterate through the models list using the client
# for m in client.models.list():
#     # In the new SDK, check for 'generateContent' in the supported_actions
#     if 'generateContent' in m.supported_actions:
#         print(f"- {m.name}")