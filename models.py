from datetime import date

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True)

class Document(Base):
    __tablename__ = 'documents'


    path: Mapped[str]
    date: Mapped[date]
    text: Mapped["DocumentText | None"] = relationship(
        back_populates="document",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

class DocumentText(Base):
    __tablename__ = 'documents_text'


    id_doc: Mapped[int] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        unique=True,
    )
    text: Mapped[str]
    document: Mapped[Document] = relationship(back_populates="text")

