"""
Document domain model
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Document:
    """Represents a scraped document"""
    tipo: str
    title: str
    link: str
    date: date
    content: Optional[str] = None
    summary: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            'tipo': self.tipo,
            'title': self.title,
            'link': self.link,
            'date': self.date,
            'content': self.content,
            'summary': self.summary
        }

