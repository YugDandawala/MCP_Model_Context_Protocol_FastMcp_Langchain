# Model Context Protocol (MCP)

Model Context Protocol (MCP) provides a standardized client-server architecture for connecting large language models (LLMs) to external tools, data sources, and systems. It enables modular extensions beyond traditional function calling by separating AI reasoning from action execution.

## Table of Contents

- [Introduction to MCP](#introduction-to-mcp)
- [Why MCP is Needed](#why-mcp-is-needed)
  - [The Problem of Fragmentation](#the-problem-of-fragmentation)
  - [The Vision vs The Reality](#the-vision-vs-the-reality)
  - [What is Context?](#what-is-context)
  - [The Solution - Function Calling](#the-solution---function-calling)
- [MCP Architecture Overview](#mcp-architecture-overview)
  - [MCP Servers](#mcp-servers)
  - [MCP Clients](#mcp-clients)
- [How MCP Works](#how-mcp-works)
  - [MCP Server Primitives](#mcp-server-primitives)
  - [Primitives - Standard Operations](#primitives---standard-operations)
  - [MCP Data Layer](#mcp-data-layer)
    - [JSON RPC 2.0](#json-rpc-20)
    - [Why JSON RPC for Data Layer?](#why-json-rpc-for-data-layer)
  - [MCP Transport Layer](#mcp-transport-layer)
  - [MCP - Types of Server](#mcp---types-of-server)
- [MCP Life-Cycle](#mcp-life-cycle)
  - [Initialization](#initialization)
  - [Operation](#operation)
  - [Shut-Down](#shut-down)

## Introduction to MCP

Model Context Protocol (MCP) provides a standardized client-server architecture for connecting large language models (LLMs) to external tools, data sources, and systems. It enables modular extensions beyond traditional function calling by separating AI reasoning from action execution.

## Why MCP is Needed

### The Problem of Fragmentation

The modern AI landscape is fragmented, leading to significant inefficiencies. For instance, an AI assistant integrated into a note-taking application like Notion cannot communicate with an AI assistant in a collaboration tool like Slack. Similarly, a coding assistant in VS Code remains unaware of discussions happening in MS Teams. This forces users to juggle multiple AI assistants, effectively living in multiple, isolated AI worlds.

### The Vision vs The Reality

The ultimate user desire is a single, unified AI partner capable of understanding their complete workflow and solving any work-related problem. Users do not want to manage five different AI tools; they want a unified solution that addresses the core problem of **Context**.

### What is Context?

Context is everything an AI can "see" when it generates a response. More formally, Context refers to the information (such as conversation history, external documents, etc.) that the LLM uses to generate a response. For example, when chatting with an LLM like ChatGPT, the past messages form the context.

When a software engineer needs to use multiple tools or services, the lack of unified context often leads to "Copy Paste Hell," which is neither time nor cost-effective.

### The Solution - Function Calling

The initial solution to this problem was the implementation of Tools, which allows LLMs to perform actions according to predefined functions.

> [!WARNING]
> **The Problem With Tools**
> While function calling is a step forward, it introduces a new set of challenges:
> - **Integration Problem:** The number of integrations grows exponentially (N clients * M tools).
> - **Development Nightmare:** Developers face different authentication methods, data formats, API patterns, and error handling across various tools.
> - **Maintenance Problem:** Maintaining numerous fragmented integrations is costly and time-consuming.
> - **Security Fragmentation:** Security management becomes complex and fragmented.

## MCP Architecture Overview

MCP establishes a clear client-server relationship to manage complexity.

```text
 --------------------------------------------------------------------------------------
|                                                    ______                            |
| Host(to host the system) (--> Have ! MCP Clients ) ______> connects to ! MCP Servers |
|                                                                                      |  
|        Their is One-One relation between MCP Client -> MCP Server                    | 
|             ~  The Number of MCP Clients ==  MCP Servers                             |
 --------------------------------------------------------------------------------------
```

### MCP Servers

The MCP Server is designed to handle the heavy lifting and abstraction required for tool integration. Its responsibilities include:

- **Tool & Resource Exposure:** Providing a standardized interface for tools and data sources.
- **Context Provisioning:** Feeding the LLM relevant, up-to-date data from external systems (e.g., databases, web searches) to ground its responses.
- **Security & Management:** Centralizing authentication, security, and API rate limiting.
- **Workflow Orchestration:** Managing complex, multi-step actions.
- **Data Transformation:** Handling necessary data format conversions.
- **Error Handling:** Centralizing and standardizing error responses.

> [!NOTE]
> **Benefits of MCP Servers**
> By centralizing logic in the server, the integration complexity is reduced from N clients and M servers to a simple M + N integrations. This results in:
> 1. Reduced maintenance overhead.
> 2. Lower cost and time expenditure.
> 3. Improved security posture.

### MCP Clients

The MCP Client is lightweight and only needs to connect to the server using the agreed-upon protocol language. It gains access to all tools, resources, and services that the connected MCP Server provides, abstracting away the underlying complexity.

## How MCP Works

### MCP Server Primitives

The MCP Server exposes its capabilities through a set of core primitives:

- **Tools:** Actions the AI can ask the server to perform (e.g., sending an email, creating a file).
- **Resources:** Structured data sources that the AI can read (e.g., a GitHub repository, a database).
- **Prompts:** Predefined prompt templates or instructions that the server offers to help shape the AI's behavior.

For example, a Prompt primitive might look like this:

```json
{
  "name": "issue_report_prompt",
  "description": "Write clear, detailed GitHub issues",
  "messages": [{
    "role": "system", 
    "content": "Always include: Title, Steps to Reproduce, Expected, Actual, Environment"
  }]
}
```

### Primitives - Standard Operations

The MCP protocol defines standard operations for interacting with these primitives:

1.  **Tools**
    - `tools/list`: Client asks the server: "What tools do you provide?"
    - `tools/call`: Client tells the server: "Please run this tool with these arguments."

2.  **Resources**
    - `resources/list`: Client asks: "What resources are available?"
    - `resources/read`: Client says: "Give me the content of this resource (e.g., a GitHub repo)."
    - `resources/subscribe/unsubscribe`: Client subscribes or unsubscribes from updates.

3.  **Prompts**
    - `prompts/list`: Client asks: "What prompt templates do you provide?"
    - `prompts/get`: Client fetches a specific prompt template.

### MCP Data Layer

The data layer is the language and grammar of the MCP ecosystem that all components agree upon for communication. In MCP, **JSON RPC 2.0** serves as the foundation of the data layer.

#### JSON RPC 2.0

JSON RPC (JavaScript Object Notation – Remote Procedure Call) allows a program to execute a function on another computer as if it were local, abstracting away the details of network communication and data transfer. This abstraction is crucial for building distributed applications.

**Client Request Example**

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

**Notifications (Do not require a Response)**

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

**Server Response Example**

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

**Error Response**

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

#### Why JSON RPC for Data Layer?

JSON RPC was chosen for the MCP data layer due to several key advantages:
- **Lightweight:** It has minimal overhead, making communication fast.
- **Bi-directional Communication:** It supports requests originating from both the Client and the Server.
- **Batching:** Multiple requests can be sent in a single batch.
- **Notifications:** It supports messages that do not require a response.
- **Transport-Agnostic:** It can be used over any transport mechanism (e.g., HTTP, WebSockets, STDIO).

### MCP Transport Layer

The Transport Layer is the mechanism responsible for moving JSON-RPC messages between the Client and Server. The choice of transport is flexible and depends on the deployment type of the server.

### MCP - Types of Server

The transport layer is dictated by whether the server is remote or local.

```text
                        MCP Server
                        /       \
                      /         \
                      /           \
    (HTTP/SSE)Remote(Tp T)         local(STDIO)(Transport type)
- A remote server is a program   - A local server is a program
  running on another computer      running on your own computer.   
  that you connect to over a
  network(github,slack etc).
```

## MCP Life-Cycle

The MCP Life Cycle describes the complete sequence of steps that govern how a Host (client) and a Server establish, use, and end a connection during a session.

```text
               Stages of MCP Lifecycle
                /         |         \ 
               /          |          \
              /           |           \
             /            |            \
Initialization        Operation        Shut-Down   
```

### Initialization

The Initialization phase ensures a successful handshake and capability negotiation between the client and server.

1.  **Phase 1 (Client Request):** The Client sends an `initialize` request containing the MCP protocol information, client capabilities, and client implementation details.
2.  **Phase 2 (Server Response):** The Server responds with its own capabilities and information, including the MCP protocol version, server capabilities, and server implementation details.
3.  **Phase 3 (Client Notification):** After a successful exchange, the client **MUST** send an `initialized` notification to indicate it is ready to begin normal operations, confirming the connection is successful.

> [!NOTE]
> **Connection Readiness**
> - The client **SHOULD NOT** send requests other than PINGS before the server has responded to the `initialize` request.
> - The server **SHOULD NOT** send requests other than PINGS and logging messages before receiving the `initialized` notification.

> [!TIP]
> **PING and Version Negotiation**
> - **PING** is a standard JSON-RPC request used to check if a connected client or server is still responsive and the connection is alive.
> - **Version Negotiation** occurs if the protocol versions differ (e.g., "2025-03-26"). The client and server maintain a list of supported protocol versions and check for compatibility upon connection.
> - **Capability Negotiation** establishes which protocol features (e.g., `tools`, `resources`, `logging`) will be available during the session.

### Operation

During the Operation phase, the client and server exchange messages according to the negotiated capabilities. Both parties must respect the negotiated protocol version and only use the capabilities that were successfully established during the Initialization phase.

### Shut-Down

No special JSON RPC shutdown message is defined; the Transport Layer is responsible for signaling termination.

**Client-Initiated Shutdown (SHOULD):**
- Close the input stream to the child process (server).
- Wait for the server to exit gracefully.
- Send `SIGTERM` if the server does not exit in time.
- Send `SIGKILL` if the server remains unresponsive.

**Server-Initiated Shutdown (MAYBE):**
The server may close the output stream to the client if an internal error occurs, if functions are not working, or if there are changes in tools. The client should be able to handle this unexpected connection closure.