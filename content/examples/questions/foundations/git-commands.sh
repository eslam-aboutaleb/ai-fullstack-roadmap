git init
printf '.venv/\n.env\n' > .gitignore
git add .gitignore lesson.py
git diff --cached
git commit -m "Add reproducible policy example"
