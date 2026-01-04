"""Enable running the models CLI as a module.

Usage:
    python -m empathy_os.models registry
    python -m empathy_os.models tasks
    python -m empathy_os.models validate config.yaml
    python -m empathy_os.models costs
"""

from .cli import main

if __name__ == "__main__":
    exit(main())
