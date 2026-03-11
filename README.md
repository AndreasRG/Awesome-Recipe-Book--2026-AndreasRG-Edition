# Awesome Recipe Book - 2026 AndreasRG Edition
### This project is designed for educational purposes only. All rights remain with the original provider -> MIT (License included in repository)

This is the "Awesome recipe cookbook - 2026 AndreasRG Edition" repository. It is an upgraded version of its parent repository. The objective is to recreate and improve the "Awsome Recipe Book" web application using modern coding and better practices: "https://github.com/cookbookio/awsome_recipe_cookbook".

Key upgrades include:

- SQLite3 → SQLAlchemy (async ORM)

- Flask → FastAPI

- Updated architecture and cleaner project structure

- More maintainable and scalable codebase

- Safer SQL methods

#### For the development tree, go to the project's Kanban board: "https://github.com/users/AndreasRG/projects/1/views/1"
<br>

---
### ⚠️  SECURITY VULNERABILITIES - SECURE AUTHENTICATION LOGIC IS MISSING AT THE MOMENT, seed_database() ALSO DANGER, USE AT OWN RISK ⚠️
---
<br>

## How to install and launch via bash:

Clone the repository to your machine in terminal by "git clone https://github.com/AndreasRG/recipe-book-project-exam-summer-26.git". 

Enter the "optimized-project" folder in terminal by "cd C: ..path/optimized-project".

Make sure to have Python 3.12.x installed by either option (note: requires admin rights):
- Windows via Chocolatey: "choco install python --version=3.12"
- macOS via Homebrew: "brew install python@3.12" then "brew link python@3.12"
- Linux (Ubuntu): "sudo apt update" then "sudo apt install python3.12 python3.12-venv python3.12-dev"

Install .venv environment using terminal by "python -m venv .venv".

- Windows PowerShell:
  - Activate .venv environment in terminal by ".venv\Scripts\Activate.ps1".

- Windows CMD:
  - Activate .venv environment in terminal by ".venv\Scripts\Activate.bat".

- macOS/Linux:
  - Activate .venv environment in terminal by "source .venv/bin/activate".

Install dependencies using terminal with requirements.txt by "pip install -r requirements.txt".

Launch the application in terminal by "python app.py".

The application will now start on "http://localhost:5000".

To stop the application do "ctrl + c" in the running terminal.

<br>

## How to install and launch via Docker:

Clone the repository to your machine. 

Enter the "optimized-project" folder in terminal by "cd C:..path../optimized-project".

Install and launch the application in terminal using Docker by "docker-compose up --build".

The application will now start on "http://localhost:5000".

To stop the application type "docker-compose down" in the running terminal or kill directly from Docker container.

<br>

---
### ⚠️  FOR USAGE INSTRUCTION, GO TO RESPECTIVE README FOR APP, ROUTERS AND SERVICES  ⚠️
---

<br><br><br>

## Source Documentation list:

### Core Libraries:
Python 3.12: https://docs.python.org/3.12/  
FastAPI: https://fastapi.tiangolo.com/  
SQLAlchemy: https://docs.sqlalchemy.org/en/20/  
Uvicorn: https://www.uvicorn.org/  
Jinja2 Templates: https://jinja.palletsprojects.com/

### Async & Web Stack:  
AnyIO: https://anyio.readthedocs.io/  
WebSockets: https://websockets.readthedocs.io/  
httptools: https://github.com/MagicStack/httptools

### Pydantic & Typing:  
Pydantic v2: https://docs.pydantic.dev/  
typing_extensions: https://pypi.org/project/typing-extensions/

### Database & Drivers:  
aiosqlite: https://github.com/omnilib/aiosqlite  
greenlet: https://greenlet.readthedocs.io/

### Development Tools:  
watchfiles: https://github.com/samuelcolvin/watchfiles  
python-dotenv: https://github.com/theskumar/python-dotenv  
PyYAML: https://pyyaml.org/

test