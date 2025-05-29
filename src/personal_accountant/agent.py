from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from personal_accountant import prompt, model
from personal_accountant.sub_agents.spend_extractor.agent import spend_extractor_agent
from personal_accountant.tools.database import save_spending

personal_accountant_agent = Agent(
    model=model.LIGHT_MODEL,
    name="personal_accountant_agent",
    description="A helpful personal accountant",
    instruction=prompt.PERSONAL_ACCOUNTANT_PROMPT,
    # sub_agents=[],
    tools=[AgentTool(agent=spend_extractor_agent), save_spending],
)

root_agent = personal_accountant_agent
