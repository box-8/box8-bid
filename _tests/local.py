import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from crewai import Agent, Task, Crew, Process
from utils.Session import *

#define the agent - note no tools so its only going to tell you what it knows
researcher = Agent(
    role='researcher',
    goal='Uncoverer information about emerging cybersecurity vulnerabilities',
    backstory='You are a Top CyberSecurity researcher tasked with finding detailed information about emerging Cybersecurity vulnerabilities.',
    verbose=True,
    allow_delegation=False,
    llm=ChooseLLM("groq")
)

#define the agent - note no tools so its only going to tell you what it knows
writer = Agent(
    role='A writer of a popular cybersecurity newsletter',
    goal='Generate a detailed Cybersecurity newsletter',
    backstory='You are a Top CyberSecurity writer known for writing detailed and engaging newsletters',
    verbose=True,
    allow_delegation=False,
    llm=ChooseLLM("groq")
)

#define the tasks
task1 = Task(description='Investigate emerging cybersecurity vulnerabilities that have come out in the past few months', agent=researcher, expected_output='Text research')
task2 = Task(description='Write a compelling and detailed newsletter about cybersecurity vulnerabilities emerging in the past few months, make sure each vulnerability recieves its own section the newsletter', agent=writer, expected_output='A refined finalized version of report in text format')

#get working
crew = Crew(
    agents=[researcher,writer],
    tasks=[task1,task2],
    verbose=True,
    process=Process.sequential
)

result = crew.kickoff()

print(result)