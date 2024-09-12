import io
import logging
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Créer un objet StringIO pour capturer les logs
log_capture_string = io.StringIO()

# Configurer le logger pour écrire dans le StringIO
ch = logging.StreamHandler(log_capture_string)
ch.setLevel(logging.DEBUG)

# Ajouter le handler à la configuration de logging
logging.basicConfig(handlers=[ch], level=logging.DEBUG)

# Utiliser l'outil Serper pour l'agent
search_tool = SerperDevTool()

# Créer un agent avec verbose=True
researcher = Agent(
  role='Researcher',
  goal='Discover emerging technologies in {topic}',
  verbose=True,
  memory=True,
  backstory="You have a deep knowledge of technology trends and breakthroughs.",
  tools=[search_tool]
)

# Créer une tâche pour cet agent
research_task = Task(
  description="Find and summarize key points about the next big tech trend in {topic}.",
  expected_output="A concise report on the most promising trends in {topic}.",
  tools=[search_tool],
  agent=researcher,
)

# Créer le crew avec l'agent et la tâche
crew = Crew(
  agents=[researcher],
  tasks=[research_task],
  process=Process.sequential
)

# Lancer le processus du crew
crew.kickoff(inputs={'topic': 'AI in vision'})

# Récupérer les logs depuis le StringIO
logs = log_capture_string.getvalue()

# Afficher ou stocker les logs dans une variable
print(logs)

# Si tu veux utiliser la variable logs plus tard
captured_logs = logs
with open('captured_logs.txt', 'w') as f:
    f.write(captured_logs) 