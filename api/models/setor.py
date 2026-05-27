from sqlalchemy import String
from sqlalchemy.dialects.oracle import NUMBER
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base

class Setor(Base):
    __tablename__ = "setores"

    id: Mapped[int] = mapped_column(NUMBER, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    descricao: Mapped[str] = mapped_column(String(100), nullable=False)

    enderecos: Mapped[list["Endereco"]] = relationship("Endereco", back_populates="setor")
