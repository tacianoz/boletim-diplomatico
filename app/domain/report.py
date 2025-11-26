"""
Report domain model
"""
from dataclasses import dataclass
from typing import List
from app.domain.document import Document


@dataclass
class Report:
    """Represents a compiled report"""
    documents: List[Document]
    compiled_text: str
    
    def get_documents_by_type(self, tipo: str) -> List[Document]:
        """Get documents filtered by type"""
        return [doc for doc in self.documents if doc.tipo == tipo]

