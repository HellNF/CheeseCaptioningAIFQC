import sys
from pathlib import Path

# Aggiunge root del progetto al path così i test trovano src.data.*
sys.path.insert(0, str(Path(__file__).parents[1]))
