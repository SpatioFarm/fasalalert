import sys
import subprocess

subprocess.run([sys.executable, "-m", "streamlit", "run", "src/gui/app.py"])