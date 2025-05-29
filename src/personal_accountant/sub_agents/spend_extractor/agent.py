from google.adk.agents import Agent

from personal_accountant import model
from personal_accountant.types.type import SpendingAgentOutput
from personal_accountant.sub_agents.spend_extractor import prompt

spend_extractor_agent = Agent(
    model=model.LIGHT_MODEL,
    name="spend_extractor_agent",
    description="A spending or expenses formatter",
    instruction=prompt.SPEND_EXTRACTOR_PROMPT,
    output_schema=SpendingAgentOutput,
    output_key="structured_spending",
)
