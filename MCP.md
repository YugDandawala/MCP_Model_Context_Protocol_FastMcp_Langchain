# Model Context Protocol (MCP)

💡 Introduction 

The **Model Context Protocol (MCP)** provides a standardized client-server architecture for connecting large language models (LLMs) to external tools, data sources, and systems. It enables modular extensions beyond traditional function calling by separating AI reasoning from action execution.

---

# Why MCP is needed ❓

🧩 The Problem of Fragmentation 

The modern AI landscape is fragmented, leading to siloed knowledge and inefficient workflows:

*   AI in Notion couldn't talk to AI in Slack.
*   VS Code coding assistants knew nothing about discussions in MS Teams.
*   Users found themselves living in multiple AI worlds, juggling between various assistants.

🎯 The Vision vs. The Reality 

The ultimate goal is a unified AI partner that can understand a user's complete work context and solve any related problem. Users do not want five different AI tools; they want one cohesive solution. The core challenge is **Context**.

🧠 What is Context? 

Context is everything an AI can "see" when it generates a response. More formally, Context refers to the information (conversation history, external documents, etc.) that the LLM uses to generate a response.

*   **Example:** While chatting with ChatGPT, past messages form the context.
*   When a Software Engineer wants to use multiple tools or services, the lack of unified context leads to "Copy Paste Hell," which is neither time nor cost-effective.

##🛠️ The Solution: Function Calling 

The initial solution was the implication of tools—building functions that allow LLMs to perform actions according to predefined tool specifications.

🚧 The Problem with Tools 

While function calling is a step forward, it introduces significant integration and maintenance challenges:

*   **Integration Problem:** An N (clients) * M (servers) integration matrix.
*   **Development Nightmare:** Different authentication methods, data formats, API patterns, and error handling for every tool.
*   **Maintenance Problem:** High overhead for keeping numerous integrations up-to-date.
*   **Security Fragmentation:** Managing security across many disparate systems.
*   **Cost and Time Wastage.**

---

🏗️ MCP Architecture 

MCP solves the fragmentation problem by introducing a standardized client-server model.

## The Core Components

The MCP architecture defines a clear separation of concerns between the Host/Client and the Server.

```text
     --------------------------------------------------------------------------------------
    |                                                    ______                            |
    | Host(to host the system) (--> Have ! MCP Clients ) ______> connects to ! MCP Servers |
    |                                                                                      |  
    |        Their is One-One relation between MCP Client -> MCP Server                    | 
    |             ~  The Number of MCP Clients ==  MCP Servers                             |
     --------------------------------------------------------------------------------------
```

⚙️ MCP Servers: The Heavy Lifters 

The MCP Server is responsible for the heavy lifting, abstracting away the complexity of external systems.

*   **Error Handling**
*   **Tool & Resource Exposure:** Making external capabilities available to the LLM.
*   **Context Provisioning:** Feeds the LLM relevant, up-to-date data from external systems (e.g., databases, web searches) to ground its responses.
*   **Security & Management**
*   **API Rate Limiting**
*   **Authentication**
*   **Workflow Orchestration**
*   **Data Transformation**

✨ Benefits of the Server Model 

1.  **Simplified Integration:** N clients and M servers only require M + N integrations, drastically reducing complexity.
2.  **No Maintenance Overhead**
3.  **Reduced Cost and Time**
4.  **Better Security**

💻 MCP Clients: The AI Interface 

The MCP Client is the interface between the LLM (the AI) and the MCP Server. The client's role is to simply connect to the server using the standardized MCP language and utilize all the tools, resources, and services that the particular MCP Server provides.

🔄 The Client's Role in the MCP Cycle 

The client is responsible for three key phases in the interaction loop:

1.  **Discovery:** The client initiates the process by asking the server what capabilities it offers. This is done via the `tools/list` and `resources/list` operations.
2.  **Tool Negotiation:** Based on the user's request and the LLM's reasoning, the client determines which tool or resource is needed.
3.  **Execution:** The client sends a standardized request to the server to execute the action (e.g., `tools/call`) or retrieve data (`resources/read`). The client then receives the structured result and presents it back to the LLM for final response generation.

---

🛠️ How MCP works? 

MCP operates through a set of standardized primitives, a common data layer, and a flexible transport layer.

🧱 MCP Server Primitives 

MCP Primitives are the fundamental building blocks that the Server exposes to the Client.

### Tools, Resources, and Prompts

*   **Tools:** Actions the AI asks the server to perform (e.g., "create a GitHub issue").
*   **Resources:** Structured data sources that the AI can read (e.g., "read the contents of a GitHub repository").
*   **Prompts:** Predefined prompt templates or instructions that the server offers to help shape the AI's behavior.

**Example Prompt Primitive:**

```json
{
  "name": "issue_report_prompt",
  "description": "Write clear, detailed GitHub issues",
  "messages": [
    {
      "role": "system", 
      "content": "Always include: Title, Steps to Reproduce, Expected, Actual, Environment"
    }
  ]
}
```

🔗 Primitives - Standard Operations 

The protocol defines standard methods for interacting with each primitive:

| Primitive | Operation | Description |
| :--- | :--- | :--- |
| **Tools** | `tools/list` | Client asks the server: "What tools do you provide?" |
| | `tools/call` | Client tells the server: "Please run this tool with these arguments." |
| **Resources** | `resources/list` | Client asks: "What resources are available?" |
| | `resources/read` | Client says: "Give me the content of this resource (e.g., a GitHub repo)." |
| | `resources/subscribe/unsubscribe` | Client subscribes or unsubscribes from updates. |
| **Prompts** | `prompts/list` | Client asks: "What prompt templates do you provide?" |
| | `prompts/get` | Client fetches a specific prompt template. |

## MCP Data Layer: The Language of Communication 💬

The data layer is the language and grammar of the MCP ecosystem that everyone agrees upon to communicate. In MCP, **JSON RPC 2.0** serves as the foundation.

### JSON RPC 2.0 (Remote Procedure Call)

A Remote Procedure Call (RPC) allows a program to execute a function on another computer as if it were local, hiding the details of network communication and data transfer. This abstraction makes it easier to build distributed applications.

**Client Request Example (`tools/call`):**

```json
{
  "jsonrpc": "2.0",
  "id": "req-123",
  "method": "tools/call",
  "params": {
    "name": "get-weather",
    "arguments": {
      "location": "San Francisco",
      "days": 2
    }
  }
}
```

**Server Response Example (Success):**

```json
{
  "jsonrpc": "2.0",
  "id": "req-123",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "The weather in San Francisco for the next 2 days will be partly cloudy with temperatures around 62°F (16°C)."
      }
    ],
    "isError": false
  }
}
```

**Server Response Example (Error):**

```json
{
  "jsonrpc": "2.0",
  "id": "req-123",
  "error": {
    "code": -32602,
    "message": "Invalid params",
    "data": {
      "field": "days",
      "reason": "Must be a positive number",
      "received": -2
    }
  }
}
```

**Notifications (No Response Required):**

```json
{
  "jsonrpc": "2.0",
  "method": "notifications/progress",
  "params": {
    "operation": "file_upload",
    "progress": 0.75,
    "message": "Uploading chunk 3 of 4..."
  }
}
```

### Why JSON RPC for the Data Layer? ✅

*   It’s lightweight.
*   Supports bi-directional communication (requests can be sent by either Client or Server).
*   Supports batching (can send multiple requests at one time).
*   Supports notifications.
*   It is transport-agnostic (can send any type of request: HTTP, STDIO, etc.).

## MCP Transport Layer 📡

The Transport Layer is the mechanism that moves JSON-RPC messages between the Client and Server. The choice of transport depends on the type of server.

🌐 MCP Server Types 

MCP defines two main types of servers based on their deployment and transport mechanism:

```text
                            MCP Server
                            /       \
                          /           \
                        /               \
        (HTTP/SSE)Remote(Tp T)         local(STDIO)(Transport type)
    - A remote server is a program   - A local server is a program
      running on another computer      running on your own computer.   
      that you connect to over a
      network(github,slack etc).
```

---

🔄 MCP Life-cycle 

The MCP Life Cycle describes the complete sequence of steps that govern how a Host (client) and a Server establish, use, and end a connection during a session.

## Stages of the MCP Lifecycle 🚦

```text
                   Stages of MCP Lifecycle
                    /         |         \ 
                   /          |          \
                  /           |           \
                 /            |            \
    Initialization        Operation        Shut-Down   
```

## Initialization: Establishing the Connection 👋

This phase ensures the client and server agree on the terms of communication.

*   **Phase 1: Client Request**
    *   The Client sends an `initialize` request containing: MCP protocol info, client capabilities, and client implementation info.
*   **Phase 2: Server Response**
    *   The Server sends its own capabilities and info: MCP protocol version, server capabilities, and server implementation info.
*   **Phase 3: Ready Notification**
    *   After successful initialization, the client **MUST** send an `initialized` notification to indicate it is ready to begin normal operations. (Connection successful client-server).

### Connection Rules

*   The client **SHOULD NOT** send requests other than PINGS before the server has responded to the `initialize` request.
*   The server **SHOULD NOT** send requests other than PINGS and logging before receiving the `initialized` notification.
*   **PING** is a standard JSON-RPC request to check if a connected client or server is still responsive and the connection is alive.

### Version Negotiation 🤝

*   If the Protocol Versions of requests are different (e.g., "2025-03-26" version), the server maintains a `SUPPORTED_PROTOCOL_VERSIONS` list.
*   The server checks if the requested version is available and negotiates the highest mutually supported version.

### Capability Negotiation 🎛️

Client and server capabilities establish which protocol features will be available during the session.

*   **Client Capabilities Examples:** `root`, `sampling` (server asks to use AI), `elicitation` (client provides incomplete information).
*   **Server Capabilities Examples:** `prompts`, `resources`, `tools`, `logging`.

## Operation: Message Exchange 💬

During the operation phase, the client and server exchange messages according to the negotiated capabilities.

*   All communication must respect the negotiated protocol version.
*   Only capabilities that were successfully negotiated can be used.

🛑 Shut-Down: Terminating the Session 

No special JSON RPC shutdown message is defined. The transport layer is responsible for signaling termination.

### Client-Initiated Shutdown (SHOULD)

1.  Close input stream to the child process (server).
2.  Wait for the server to exit.
3.  Send `SIGTERM` if the server does not exit in time.
4.  Send `SIGKILL` if still unresponsive.

### Server-Initiated Shutdown (MAYBE)

The server may close the output stream to the client if an internal error occurs, a function is not working, tools change, or any other situation that necessitates termination. The client should be able to handle this unexpected closure.
