import asyncio
import operator
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, ToolMessage, SystemMessage
from mcp_client import get_tools

# Initialize LLM
llm = ChatOllama(model = "llama3.1:8b")

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]

async def main():
    # 1. Load Tools
    expense_tools = await get_tools()
    print(f"✅ Loaded {len(expense_tools)} tools.")
    for tool in expense_tools:
        print(tool.name)
    
    # 2. Bind Tools to LLM
    llm_with_tools = llm.bind_tools(expense_tools)
 
    builder = StateGraph(AgentState)
    
    async def agent_node(state: AgentState):
        result = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [result]}
    
    builder.add_node("agent", agent_node)
    builder.add_node("tools", ToolNode(expense_tools,handle_tool_errors=True))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")
    
    app = builder.compile()
    
    # 4. Run Interaction
    prompt = input("\nWhat would you like to record? ")
    
    # SYSTEM PROMPT: Forces the 3B model to act
    # In agent.py, update your inputs section:
    inputs = {
        "messages": [
            SystemMessage(content="""You are a precise Expense and File Assistant. 
            
            LOCAL FILE SYSTEM CONTEXT:
            - Your project root is: /home/nt020/Downloads/MCP/
            - You can use the 'LocalFileSystem__list_directory' tool to see files.
            
            EXPENSE CONTEXT:
            - Current Date: January 2026.
            - Always use 'expense_tracker__add_expense' for new entries.
            - When adding an expense, extract the location or reason and put it in the 'note' field.
            - If the user mentions a specific mode of transport (cab, train), put that in 'subcategory'.
            - Always use the 'expense_tracker:add_expense' tool.
            
              Example: "spent 400 on cab from Surat" 
              -> amount: 400, category: "Travel", subcategory: "Cab", note: "from Surat"
                          
            If the user asks to see files, always start by listing the directory: /home/nt020/Downloads/MCP/
            """),
            HumanMessage(content=prompt)
        ]
    }
    inputs = {
        "messages": [
            HumanMessage(content=prompt)
        ]
    }

    async for chunk in app.astream(inputs, stream_mode="values"):
        last_message = chunk["messages"][-1]
        if isinstance(last_message, AIMessage) and last_message.tool_calls:
            for tc in last_message.tool_calls:
                print(f"🛠️  Model is calling: {tc['name']} with {tc['args']}")
        elif isinstance(last_message, ToolMessage):
            print(f"✅ Database Response: {last_message.content}")
        elif isinstance(last_message, AIMessage) and not last_message.tool_calls:
            print(f"🤖 Agent: {last_message.content}")

if __name__ == "__main__":
    asyncio.run(main())


# import asyncio
# import operator
# from typing import Annotated, TypedDict, Union
# from langgraph.graph import StateGraph, START, END
# from langgraph.prebuilt import ToolNode, tools_condition
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.messages import HumanMessage, BaseMessage, AIMessage, ToolMessage,SystemMessage
# from mcp_client import get_github_tools
# import os 
# from dotenv import load_dotenv

# load_dotenv()
# # 1. Initialize LLM with the stable alias
# llm = ChatGoogleGenerativeAI(
#     model = "gemini-2.0-flash",
#     temperature = 0.2,
#     google_api_key = os.getenv("GOOGLE_API_KEY")
# )

# # 2. Define State with an 'add' reducer so messages append to the list
# class AgentState(TypedDict):
#     messages: Annotated[list[BaseMessage], operator.add]

# async def main():
#     github_tools = await get_github_tools()
#     llm_with_tools = llm.bind_tools(github_tools)
    
#     builder = StateGraph(AgentState)
    
#     async def agent_node(state: AgentState):
#         # Pass the entire message history
#         result = await llm_with_tools.ainvoke(state["messages"])
#         return {"messages": [result]}
    
#     builder.add_node("agent", agent_node)
#     builder.add_node("tools", ToolNode(github_tools))

#     builder.add_edge(START, "agent")
#     builder.add_conditional_edges("agent", tools_condition)
#     builder.add_edge("tools", "agent")
#     # Note: Removed the direct edge from agent to END because 
#     # tools_condition handles the routing to END when no tools are called.
    
#     app = builder.compile()
    
#     prompt = input("Prompt: ")
    
#     # Add a SystemMessage to give the agent permanent context
#     inputs = {
#         "messages": [
#             SystemMessage(content="You are a GitHub assistant and you access to this owner account.The default repository owner is 'YugDandawala'."),
#             HumanMessage(content=prompt)
#         ]
#     }
    
#     # Use a loop to watch the agent work through the tools
#     async for chunk in app.astream(inputs, stream_mode="values"):
#         last_message = chunk["messages"][-1]
#         if isinstance(last_message, AIMessage) and last_message.tool_calls:
#             print(f"🛠️ Agent is calling tool: {last_message.tool_calls[0]['name']}")
#         elif isinstance(last_message, ToolMessage):
#             print(f"✅ Tool {last_message.name} completed.")
# if __name__ == "__main__":
#     asyncio.run(main())

# Read the Chat.txt file from the AI-Podcast-Assistant repository. Analyze the dialogue and classify the participants into 'Human' and 'AI'.Create a new file named Chat.md in the same repository. Format the content to look like a modern chat interface using the following style.Header: Use a clean title like '# 🗨️ Conversation History'.Human Messages: Use a bold label like '👤 Human:' followed by the message.AI Messages: Use a bold label like '🤖 AI Assistant:' and wrap the AI's response in a blockquote (>) to give it a distinct background look.Separation: Place a horizontal rule (---) between each back-and-forth exchange.Ensure the flow is chronological and easy to read for someone who wasn't part of the chat.