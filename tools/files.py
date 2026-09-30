from pathlib import Path

def find_files(name: str, root: Path | None = None, limit: int = 20):
    root = root or Path.home(); target = name.strip().lower()
    if not target: return []
    matches=[]
    try:
        for path in root.rglob('*'):
            if len(matches)>=limit: break
            if path.is_file() and target in path.name.lower(): matches.append(str(path))
    except (OSError, PermissionError): pass
    return matches
