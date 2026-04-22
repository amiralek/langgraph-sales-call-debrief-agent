\# LangGraph Sales Call Debrief Agent



A terminal-based LangGraph agent that analyzes a sales call transcript, extracts structured deal information, drafts a follow-up email, flags deal risks, and pauses for human review when needed.



\## What it does



This project takes a sample sales call transcript and runs it through a LangGraph workflow that:



\- Extracts prospect information, objections, commitments, and next steps

\- Simulates updating a CRM record

\- Simulates creating a follow-up task

\- Drafts a professional follow-up email

\- Flags risks such as competitor mentions, budget concerns, and timeline stalls

\- Triggers human review for medium/high-risk deals

\- Produces a final structured JSON report



\## Why this project matters



This is a small but realistic example of agentic business automation.



It shows how to combine:

\- LLM-based extraction and drafting

\- deterministic Python business logic

\- LangGraph state management

\- conditional routing

\- human-in-the-loop review



\## Project structure



```text

src/

&#x20; state.py       # Shared state schema

&#x20; prompts.py     # LLM prompts

&#x20; nodes.py       # Business logic + model calls

&#x20; graph.py       # LangGraph orchestration

data/

&#x20; sample\_transcript.txt   # Demo transcript

main.py          # Terminal runner

output\_report.json # Example final output

```



\## How the workflow runs



1\. `extract\_info` parses the transcript into structured fields

2\. `update\_crm` creates a simulated CRM update

3\. `create\_task` creates a simulated follow-up task

4\. `draft\_email` writes a follow-up email

5\. `flag\_risks` identifies risk signals

6\. If risk is low, the agent auto-approves

7\. If risk is medium/high, the agent pauses for human review

8\. `build\_report` creates the final output JSON



\## Tech stack



\- Python

\- LangGraph

\- LangChain

\- NVIDIA Build API

\- Llama 3.1 70B Instruct



\## Run locally



\### 1. Clone the repo

```bash

git clone <your-repo-url>

cd <repo-folder>

```



\### 2. Create and activate a virtual environment

```bash

python -m venv .venv

.venv\\Scripts\\activate

```



\### 3. Install dependencies

```bash

pip install -r requirements.txt

```



\### 4. Create a `.env` file

Add your NVIDIA API key:



```env

NVIDIA\_API\_KEY=your\_api\_key\_here

```



\### 5. Run the project

```bash

python main.py

```



\## Example output



The project writes a final structured report to:



```text

output\_report.json

```



This report includes:

\- extracted deal info

\- CRM payload

\- task payload

\- drafted email

\- risk flags

\- human review metadata



\## Notes



\- This project currently uses a sample transcript from the `data/` folder

\- CRM and task creation are simulated

\- Human review happens in the terminal

\- This is a proof of concept designed to show LangGraph orchestration patterns



\## Next improvements



\- Replace dummy transcript input with uploaded/live call data

\- Replace simulated CRM/task actions with real integrations

\- Add FastAPI or web UI

\- Persist checkpoints with Postgres instead of in-memory saver

