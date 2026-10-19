from pathlib import Path
#current working directory
root_dir = Path(".")

#folder to create
folders = [
    "app/api",
    "app/core",
    "app/rag",
    "app/services",
    "data",
    "templates",
    "static",
    "uploads",
    "tests",
]



# Files to create
files = [
    "app/main.py",
    "ingest_sample_kb.py",
    "requirements.txt",
    "run.py",
    ".env",
]


# Create folders
for folder in folders:
    (root_dir / folder).mkdir(parents=True, exist_ok=True)


# Create files
for file in files:
    (root_dir / file).touch(exist_ok=True)



print("Project structure created successfully.")