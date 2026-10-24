"""In-memory data layer (DAO) for status notes."""
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from itertools import count
from threading import Lock


@dataclass
class Note:
    id: int
    author: str
    text: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

    def to_dict(self) -> dict:
        return asdict(self)


class NoteStore:
    def __init__(self) -> None:
        self._notes: list[Note] = []
        self._ids = count(1)
        self._lock = Lock()

    def add(self, author: str, text: str) -> Note:
        with self._lock:
            note = Note(id=next(self._ids), author=author, text=text)
            self._notes.append(note)
            return note

    def list(self) -> list[Note]:
        with self._lock:
            return list(reversed(self._notes))


store = NoteStore()
store.add("ops-bot", "Cluster is healthy. Have a great sprint!")
