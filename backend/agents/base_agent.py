# backend/agents/base_agent.py

from abc import ABC, abstractmethod
from typing import Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing import TypedDict
from groq import BadRequestError


# ─── State ────────────────────────────────────────────────────────────────────
# This is the shared memory that flows between every node in the graph.
# Think of it as a context object passed through the entire agent run.
#
# Annotated[list, add_messages] means:
#   - messages is a list
#   - when a node returns new messages, add_messages APPENDS them to the list
#   - instead of replacing the whole list
# This is how conversation history accumulates automatically.

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# ─── Base Agent ───────────────────────────────────────────────────────────────

class BaseAgent(ABC):

    # Default model — subclasses can override this by redefining the class variable.
    # Exactly like a protected field in Java that subclasses can shadow.
    #
    # class ShoppingAgent(BaseAgent):
    #     MODEL_NAME = "llama3-8b-8192"  # overrides the base
    MODEL_NAME = "llama-3.3-70b-versatile"

    def __init__(self):
        # Initialize the Groq LLM with the model name.
        # temperature=0 means deterministic output — no randomness.
        # For a shopping agent, we want consistent, predictable tool calls
        # not creative variation.
        self.llm = ChatGroq(
            model=self.MODEL_NAME,
            temperature=0
        )

        # get_tools() is abstract — defined by the subclass.
        # bind_tools() attaches the tool schemas to the LLM so it knows
        # what tools are available and what arguments they expect.
        self.tools = self.get_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)

        # Build a dict of {tool_name: tool_function} for fast lookup.
        # When the LLM says "call search_products", we look it up here
        # and execute it. Like a HashMap<String, Function> in Java.
        self.tools_map = {tool.name: tool for tool in self.tools}

        # Build the LangGraph graph once at init time.
        # We compile it and store it — no need to rebuild on every request.
        self.graph = self._build_graph()

    # ─── Abstract methods — subclasses must implement these ──────────────────

    @abstractmethod
    def get_tools(self) -> list:
        """Return a list of @tool decorated functions for this agent."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt string for this agent."""
        pass

    # ─── Graph construction ───────────────────────────────────────────────────

    def _build_graph(self):
        # StateGraph is the LangGraph graph builder.
        # We pass AgentState so the graph knows the shape of shared state.
        graph_builder = StateGraph(AgentState)

        # Add the two nodes.
        # First arg is the node name (used in edge definitions).
        # Second arg is the function to call when that node is activated.
        graph_builder.add_node("agent", self._agent_node)
        graph_builder.add_node("tools", self._tools_node)

        # Entry point — the first node to run when graph.invoke() is called.
        graph_builder.set_entry_point("agent")

        # Conditional edge from agent node.
        # After agent_node runs, call _should_continue to decide next node.
        # The dict maps return values of _should_continue to node names.
        graph_builder.add_conditional_edges(
            "agent",
            self._should_continue,
            {
                "tools": "tools",  # if _should_continue returns "tools" → go to tools node
                "end": END         # if _should_continue returns "end" → stop
            }
        )

        # After tools node always go back to agent node — unconditional edge.
        graph_builder.add_edge("tools", "agent")

        # compile() validates the graph (checks for disconnected nodes etc.)
        # and returns a runnable object.
        return graph_builder.compile()

    # ─── Node 1: Agent node ───────────────────────────────────────────────────
    # Receives current state, calls the LLM, returns the LLM's response.
    # The response is either a final text answer or a tool call request.

    def _agent_node(self, state: AgentState) -> dict:
        # Prepend the system prompt to the message list on every LLM call.
        # SystemMessage sets the agent's personality and instructions.
        system_message = SystemMessage(content=self.get_system_prompt())
        messages_with_system = [system_message] + state["messages"]

        # Groq/LLaMA occasionally generates malformed JSON in tool calls
        # (e.g. using ";" instead of "," as a separator). We catch that 400
        # error and retry once with an explicit correction hint. The hint is
        # appended as a HumanMessage so the LLM sees its own mistake and
        # generates a valid call on the second attempt.
        MAX_RETRIES = 2
        for attempt in range(MAX_RETRIES):
            try:
                response = self.llm_with_tools.invoke(messages_with_system)
                return {"messages": [response]}
            except BadRequestError as e:
                if attempt < MAX_RETRIES - 1:
                    # Extract the failed generation detail if available
                    error_detail = ""
                    try:
                        error_detail = e.response.json()["error"].get("failed_generation", "")
                    except Exception:
                        pass

                    correction = (
                        "Your previous tool call contained invalid JSON "
                        "(e.g. a semicolon used instead of a comma between arguments). "
                        "Please retry using strictly valid JSON for all tool arguments."
                    )
                    if error_detail:
                        correction += f" Malformed output was: {error_detail}"

                    messages_with_system = messages_with_system + [
                        HumanMessage(content=correction)
                    ]
                else:
                    raise

    # ─── Node 2: Tools node ───────────────────────────────────────────────────
    # Looks at the last AIMessage, finds all tool call requests in it,
    # executes each tool, and returns ToolMessages with the results.

    def _tools_node(self, state: AgentState) -> dict:
        # The last message is always an AIMessage with tool_calls
        # (we only reach this node if _should_continue returned "tools")
        last_message = state["messages"][-1]
        tool_results = []

        for tool_call in last_message.tool_calls:
            # tool_call looks like:
            # {"id": "abc123", "name": "search_products", "args": {"search": "headphones", "max_price": 1000}}

            tool_name = tool_call["name"]
            tool_args = tool_call["args"]

            # Look up the actual function in our tools_map and call it.
            # ** unpacks the dict as keyword arguments.
            # tools_map["search_products"](search="headphones", max_price=1000)
            tool_function = self.tools_map[tool_name]
            result = tool_function.invoke(tool_args)

            # ToolMessage wraps the result and links it back to the tool call
            # via tool_call_id. The LLM needs this ID to match result to request.
            tool_results.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
            )

        return {"messages": tool_results}

    # ─── Conditional edge function ────────────────────────────────────────────
    # Called after every agent node run.
    # Returns "tools" if LLM requested tool calls, "end" if it gave a final answer.

    def _should_continue(self, state: AgentState) -> str:
        last_message = state["messages"][-1]

        # tool_calls is a list — non-empty means the LLM wants to call tools
        if last_message.tool_calls:
            return "tools"
        return "end"

    # ─── Public run method ────────────────────────────────────────────────────
    # This is what agent_routes.py (the /chat endpoint) will call.
    # Takes the user message and conversation history, returns the agent's response.

    def run(self, user_message: str, history: list = None) -> str:
        if history is None:
            history = []

        # Build the full message list: history + new user message
        # HumanMessage wraps the user's text in LangChain's message format
        messages = history + [HumanMessage(content=user_message)]

        # graph.invoke() runs the full loop until it hits END.
        # It returns the final state — the complete messages list.
        final_state = self.graph.invoke({"messages": messages})

        # The last message in final state is the LLM's final answer.
        return final_state["messages"][-1].content