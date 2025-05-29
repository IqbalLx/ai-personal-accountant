from google.adk.agents import Agent, LoopAgent, SequentialAgent
from google.adk.tools.tool_context import ToolContext

from personal_accountant import model
from personal_accountant.sub_agents.spend_retriever import prompt
from personal_accountant.tools.database import query_database


def exit_loop(tool_context: ToolContext):
    """Call this function ONLY when the critique indicates no further changes are needed, signaling the iterative process should end."""
    print(f"  [Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    # Return empty dict as tools should typically return JSON-serializable output
    return {}


initial_query_generator_agent = Agent(
    model=model.HEAVY_MODEL,
    name="initial_query_generator_agent",
    description="A initial query generator agent",
    instruction=prompt.QUERY_GENERATOR_PROMPT,
    output_key="sql_query",
)

query_refinement_agent = Agent(
    model=model.HEAVY_MODEL,
    name="query_refinement_agent",
    description="A query refinement agent",
    instruction=prompt.QUERY_REFINEMENT_PROMPT,
    disallow_transfer_to_parent=True,
    output_key="sql_query",
)

query_executor_agent = Agent(
    model=model.LIGHT_MODEL,
    name="query_executor_agent",
    description="A query executor agent",
    instruction=prompt.QUERY_EXECUTOR_PROMPT,
    disallow_transfer_to_parent=True,
    tools=[query_database, exit_loop],
)

query_loop_agent = LoopAgent(
    name="query_loop_agent",
    description="A query loop agent",
    sub_agents=[query_executor_agent, query_refinement_agent],
    max_iterations=5,
)

answer_agent = Agent(
    model=model.LIGHT_MODEL,
    name="answer_agent",
    description="A answer agent",
    instruction=prompt.ANSWER_PROMPT,
)

spend_retriever_agent = SequentialAgent(
    name="spend_retriever_agent",
    description="A spend retriever agent",
    sub_agents=[initial_query_generator_agent, query_loop_agent, answer_agent],
)
