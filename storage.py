"""
Storage paths - single source of truth for where the app writes data.

On hosts with a read-only filesystem (e.g. Streamlit Community Cloud), the app
directory cannot be written to. Only /tmp is writable there (ephemeral: wiped
when the app restarts or wakes from sleep). Locally, nothing changes: we keep
using the project directory.
"""

import os
import tempfile


def _writable(path: str) -> bool:
    """Check whether a directory is writable by probing a temp file."""
    try:
        os.makedirs(path, exist_ok=True)
        probe = os.path.join(path, ".write_probe")
        with open(probe, "w") as f:
            f.write("ok")
        os.remove(probe)
        return True
    except OSError:
        return False


# Writable base dir: the project dir locally, /tmp on read-only hosts
WORK_DIR = "." if _writable(".") else tempfile.gettempdir()

# Where user uploads are saved (bundled sample docs stay in ./data)
DATA_DIR = os.path.join(WORK_DIR, "data")

# ChromaDB vector store - must be writable, hence WORK_DIR-based
VECTOR_STORE_PATH = os.path.join(WORK_DIR, "vector_store")
