from google.adk.agents import Agent

from personal_accountant import prompt, model

personal_accountant_agent = Agent(
    model=model.LIGHT_MODEL,
    name="personal_accountant_agent",
    description="A helpful personal accountant",
    instruction=prompt.PERSONAL_ACCOUNTANT_PROMPT,
    sub_agents=[],
)

root_agent = personal_accountant_agent
