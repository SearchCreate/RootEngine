import sys
from pathlib import Path

# Ensure rootengine/rootengine is importable via relative imports
_rootengine_root = Path(__file__).parent
if str(_rootengine_root) not in sys.path:
    sys.path.insert(0, str(_rootengine_root))
