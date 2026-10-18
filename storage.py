"""Project-relative defaults and isolated, temporary web-session workspaces."""
from pathlib import Path
import tempfile

PROJECT_DIR = Path(__file__).resolve().parent
SAMPLE_DIR = PROJECT_DIR / 'data'


def _writable(path):
    try:
        with tempfile.TemporaryFile(dir=path):
            return True
    except OSError:
        return False


WORK_DIR = PROJECT_DIR if _writable(PROJECT_DIR) else Path(tempfile.gettempdir()) / 'document-qa'
DATA_DIR = str(WORK_DIR / 'data')
VECTOR_STORE_PATH = str(WORK_DIR / 'vector_store')
MAX_UPLOAD_BYTES = 20 * 1024 * 1024


def save_upload(directory, name, content):
    """Save supported uploads inside their workspace; return whether bytes changed."""
    if not name or '/' in name or '\\' in name or Path(name).name != name:
        raise ValueError('Please use a filename without folder separators.')
    if Path(name).suffix.lower() not in {'.pdf', '.txt', '.docx'}:
        raise ValueError('Supported formats are PDF, TXT and DOCX.')
    if not content or len(content) > MAX_UPLOAD_BYTES:
        raise ValueError('Each document must be nonempty and smaller than 20 MB.')
    target = Path(directory) / name
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file() and target.read_bytes() == content:
        return False
    target.write_bytes(content)
    return True
