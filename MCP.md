# Model Context Protocol (MCP): A Standard for LLM Tooling

## Table of Contents
- [Introduction](#introduction)
  - [Defining the Model Context Protocol (MCP)](#defining-the-model-context-protocol-mcp)
- [Why MCP is Needed](#why-mcp-is-needed)
  - [The Problem of AI Fragmentation](#the-problem-of-ai-fragmentation)
  - [The Vision vs. The Reality](#the-vision-vs-the-reality)
  - [Understanding Context](#understanding-context)
  - [Limitations of Traditional Function Calling](#limitations-of-traditional-function-calling)
- [MCP Architecture](#mcp-architecture)
  - [The Client-Server Relationship](#the-client-server-relationship)
  - [MCP Servers: The Heavy Lifters](#mcp-servers-the-heavy-lifters)
  - [MCP Clients: The Orchestrators](#mcp-clients-the-orchestrators)
- [How MCP Works?](#how-mcp-works)
  - [MCP Primitives: The Building Blocks](#mcp-primitives-the-building-blocks)
    - [Tools](#tools)
    - [Resources](#resources)
    - [Prompts](#prompts)
  - [Standard Operations and API](#standard-operations-and-api)
  - [The MCP Data Layer: JSON-RPC 2.0](#the-mcp-data-layer-json-rpc-20)
    - [Client Request Example](#client-request-example)
    - [Server Response Example](#server-response-example)
    - [Error Response Example](#error-response-example)
    - [Notifications](#notifications)
    - [Why JSON-RPC?](#why-json-rpc)
  - [The MCP Transport Layer](#the-mcp-transport-layer)
    - [Remote vs. Local Servers](#remote-vs-local-servers)
- [MCP Life-cycle](#mcp-life-cycle)
  - [Initialization Phase](#initialization-phase)
  - [Operation Phase](#operation-phase)
  - [Shut-Down Phase](#shut-down-phase)

---

# Introduction

## Defining the Model Context Protocol (MCP)

The Model Context Protocol (MCP) establishes a standardized client-server architecture designed to seamlessly connect large language models (LLMs) with external tools, data sources, and complex systems.

MCP moves beyond traditional, tightly-coupled function calling by separating the AI's core reasoning and planning capabilities from the actual execution of actions. This separation enables modular, scalable, and secure extensions for AI agents.

# Why MCP is Needed

## The Problem of AI Fragmentation

Before MCP, the AI landscape was highly fragmented, leading to significant productivity bottlenecks:

*   **Siloed Intelligence:** An AI assistant integrated into Notion could not access or communicate with an AI assistant in Slack.
*   **Context Gaps:** A coding assistant in VS Code lacked awareness of related discussions happening in MS Teams.
*   **User Burden:** Users were forced to juggle multiple, disconnected AI assistants, leading to a poor, inefficient experience.

## The Vision vs. The Reality

The core user desire was for a single, unified AI partner capable of understanding and acting across their entire work environment. The reality was a "Copy Paste Hell" where users manually moved information between systems to provide the necessary context, wasting both time and cost.

## Understanding Context

Context is the foundational element that allows an AI to generate relevant and grounded responses.

> [!IMPORTANT]
> **Formal Definition:** Context refers to the information (e.g., conversation history, external documents, system state) that the LLM utilizes to formulate a response. For example, in a chat application, past messages form the context.

## Limitations of Traditional Function Calling

The initial solution to the context problem was **Function Calling**, where tools were built to allow LLMs to perform actions. However, this approach introduced a new set of problems:

*   **Integration Nightmare (N * M Problem):** Integrating N clients with M tools requires N x M integrations, leading to a massive development and maintenance burden.
*   **Inconsistent Standards:** Different tools use disparate authentication methods, data formats, API patterns, and error handling mechanisms.
*   **Security Fragmentation:** Managing security across numerous, disparate integrations becomes complex and error-prone.
*   **Maintenance Overhead:** High cost and time wastage due to constant updates and fixes across a fragmented tool ecosystem.

# MCP Architecture

MCP solves the fragmentation problem by introducing a clear, standardized client-server model.

## The Client-Server Relationship

The architecture is based on a one-to-one relationship between an MCP Client and an MCP Server.

\`\`\`text
 --------------------------------------------------------------------------------------
|                                                    ______                            |
| Host(to host the system) (--> Have ! MCP Clients ) ______> connects to ! MCP Servers |
|                                                                                      |  
|        Their is One-One relation between MCP Client -> MCP Server                    | 
|             ~  The Number of MCP Clients ==  MCP Servers                             |
 --------------------------------------------------------------------------------------
\`\`\`

## MCP Servers: The Heavy Lifters

The MCP Server is responsible for the heavy lifting, acting as the single, standardized gateway to external systems.

**Key Responsibilities:**

*   **Tool & Resource Exposure:** Exposing a unified set of capabilities (Tools, Resources, Prompts) to the client.
*   **Context Provisioning:** Feeding the LLM relevant, up-to-date data from external systems (e.g., databases, web searches) to ground its responses.
*   **Workflow Orchestration:** Managing complex, multi-step actions requested by the client.
*   **Security & Management:** Handling authentication, API rate limiting, and centralized error handling.
*   **Data Transformation:** Ensuring data formats are consistent between the external system and the MCP standard.

**Benefits of the Server-Centric Model:**

1.  **Simplified Integration:** Reduces the integration complexity from N x M to M + N (M clients + N servers).
2.  **Reduced Overhead:** Centralized maintenance, leading to lower cost and time wastage.
3.  **Enhanced Security:** Centralized security management and authentication.

## MCP Clients: The Orchestrators

The MCP Client is the component that resides within the host application (e.g., Notion, VS Code, Slack). Its primary role is to facilitate the LLM's interaction with the external world via the MCP Server.

The client's role is central to the **MCP Cycle**:

### 1. Discovery
The client initiates the process by asking the server what capabilities it provides. This is done using standard operations like \`tools/list\`, \`resources/list\`, and \`prompts/list\`.

### 2. Tool Negotiation
Based on the user's request, the LLM (via the client) determines which tool is necessary. The client then communicates the intent and required arguments to the server.

### 3. Execution
The client instructs the server to perform the action using the \`tools/call\` method. The client simply connects to the server using the same language (JSON-RPC 2.0) and utilizes all the services the server provides, abstracting away the complexity of the underlying external systems.

# How MCP Works?

## MCP Primitives: The Building Blocks

MCP defines three core primitives that the Server exposes to the Client:

### Tools
These are **Actions** the AI asks the server to perform, such as sending an email, creating a GitHub issue, or running a build script.

### Resources
These are **Structured Data Sources** that the AI can read to gather information, such as a GitHub repository, a database, or a document store.

### Prompts
These are **Predefined Prompt Templates or Instructions** that the server offers to help shape the AI's behavior for specific tasks.

**Example Prompt Primitive:**

\`\`\`json
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
\`\`\`

## Standard Operations and API

The MCP defines a standard set of operations for interacting with its primitives:

| Primitive | Operation | Description |
| :--- | :--- | :--- |
| **Tools** | \`tools/list\` | Client asks the server: "What tools do you provide?" |
| | \`tools/call\` | Client tells the server: "Please run this tool with these arguments." |
| **Resources** | \`resources/list\` | Client asks: "What resources are available?" |
| | \`resources/read\` | Client says: "Give me the content of this resource (e.g., a GitHub repo)." |
| | \`resources/subscribe/unsubscribe\` | Client subscribes or unsubscribes from updates to a resource. |
| **Prompts** | \`prompts/list\` | Client asks: "What prompt templates do you provide?" |
| | \`prompts/get\` | Client fetches a specific prompt template. |

## The MCP Data Layer: JSON-RPC 2.0

The Data Layer is the agreed-upon language and grammar of the MCP ecosystem. **JSON-RPC 2.0** serves as the foundation for all communication.

> [!NOTE]
> **JSON-RPC** (JavaScript Object Notation – Remote Procedure Call) allows a program to execute a function on another computer as if it were local, abstracting away network communication details.

### Client Request Example

\`\`\`json
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
\`\`\`

### Server Response Example

\`\`\`json
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
\`\`\`

### Error Response Example

\`\`\`json
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
\`\`\`

### Notifications

JSON-RPC also supports **Notifications**, which are requests that do not require a response, enabling asynchronous communication (e.g., progress updates).

\`\`\`json
{
  "jsonrpc": "2.0",
  "method": "notifications/progress",
  "params": {
    "operation": "file_upload",
    "progress": 0.75,
    "message": "Uploading chunk 3 of 4..."
  }
}
\`\`\`

### Why JSON-RPC?

*   **Lightweight:** Minimal overhead for fast communication.
*   **Bi-directional:** Supports requests initiated by both the Client and the Server.
*   **Batching:** Allows multiple requests to be sent in a single transaction.
*   **Transport-Agnostic:** Can be sent over any transport mechanism (HTTP, WebSockets, STDIO, etc.).

## The MCP Transport Layer

The Transport Layer is the mechanism responsible for moving the JSON-RPC messages between the Client and Server. The choice of transport is determined by the server type.

### Remote vs. Local Servers

| Server Type | Transport Type | Description |
| :--- | :--- | :--- |
| **Remote Server** | HTTP/SSE | A program running on another computer that the client connects to over a network (e.g., GitHub, Slack). |
| **Local Server** | STDIO | A program running on the user's own computer, communicating via standard input/output streams. |

# MCP Life-cycle

The MCP Life Cycle defines the complete sequence of steps for how a Host (client) and a Server establish, use, and terminate a connection during a session.

## Stages of MCP Lifecycle

\`\`\`text
                   Stages of MCP Lifecycle
                    /         |         \ 
                   /          |          \
                  /           |           \
                 /            |            \
    Initialization        Operation        Shut-Down   
\`\`\`

## Initialization Phase

This phase establishes the connection and negotiates capabilities.

1.  **Client Initialization:** The Client sends an \`initialize\` request containing its MCP protocol information, capabilities, and implementation details.
2.  **Server Response:** The Server responds with its own protocol version, capabilities, and implementation information.
3.  **Client Ready Notification:** After a successful handshake, the Client **MUST** send an \`initialized\` notification to signal it is ready to begin normal operations.

> [!IMPORTANT]
> **Connection Protocol:**
> *   The client **SHOULD NOT** send requests other than PINGS before the server has responded to the \`initialize\` request.
> *   The server **SHOULD NOT** send requests other than PINGS and logging before receiving the \`initialized\` notification.
> *   **PING** is a standard JSON-RPC request to check if a connected client or server is still responsive and the connection is alive.

### Version Negotiation

If the protocol versions differ (e.g., "2025-03-26"), the server maintains a list of \`SUPPORTED_PROTOCOL_VERSIONS\` and checks if the client's requested version is compatible.

### Capability Negotiation

Client and server capabilities establish which protocol features will be available during the session.

*   **Client Capabilities Examples:** \`root\`, \`sampling\` (server asks to use AI), \`elicitation\` (client provides incomplete information).
*   **Server Capabilities Examples:** \`prompts\`, \`resources\`, \`tools\`, \`logging\`.

## Operation Phase

During this phase, the client and server exchange messages according to the negotiated contract.

*   All communication **MUST** respect the negotiated protocol version.
*   The client and server **MUST** only use capabilities that were successfully negotiated during the Initialization Phase.

## Shut-Down Phase

No special JSON-RPC shutdown message is defined; the Transport Layer is responsible for signaling termination.

### Client-Initiated Shutdown (SHOULD)

1.  Close the input stream to the child process (server).
2.  Wait for the server to exit gracefully.
3.  Send \`SIGTERM\` if the server does not exit in time.
4.  Send \`SIGKILL\` if the server remains unresponsive.

### Server-Initiated Shutdown (MAYBE)

The server may close the connection by closing the output stream to the client. This typically occurs due to internal errors, changes in available tools, or other exceptional situations, which the client must be prepared to handle.