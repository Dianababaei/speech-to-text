"""
Lexicon model for storing medical/domain-specific terms and corrections
"""
from sqlalchemy import Column, Integer, String, UniqueConstraint, Index

from src.database import Base


class Lexicon(Base):
    """
    Lexicon model for storing domain-specific terms and their corrections
    
    Attributes:
        id: Integer primary key (auto-increment)
        term: Medical/domain-specific term
        correction: Corrected spelling
        frequency: Usage count for learning system
        source: Origin of the term (fda, rxnorm, who, user_feedback)
    """
    __tablename__ = "lexicon"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    term = Column(String(255), nullable=False)
    correction = Column(String(255), nullable=False)
    frequency = Column(Integer, nullable=False, default=0)
    source = Column(String(50), nullable=False)
    
    # Unique constraint on (term, source) to prevent duplicates
    __table_args__ = (
        UniqueConstraint('term', 'source', name='uq_lexicon_term_source'),
        Index('idx_lexicon_term', 'term'),  # Index for fast lookup
    )
    
    def __repr__(self):
        return (
            f"<Lexicon(id={self.id}, "
            f"term='{self.term}', "
            f"correction='{self.correction}', "
            f"source='{self.source}', "
            f"frequency={self.frequency})>"
        )
