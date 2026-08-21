"""Persistencia de conversaciones y pedidos (componente de almacenamiento)."""
import os
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/data/pedidos.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Mensaje(Base):
    __tablename__ = "mensajes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String, index=True, nullable=False)
    rol = Column(String, nullable=False)  # "user" | "assistant"
    contenido = Column(Text, nullable=False)
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(String, index=True, nullable=False)
    producto_id = Column(String, nullable=False)
    producto_nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    cantidad = Column(Integer, default=1)
    estado = Column(String, default="pendiente")  # pendiente | confirmado | cancelado
    creado_en = Column(DateTime, default=lambda: datetime.now(timezone.utc))


def init_db():
    Base.metadata.create_all(bind=engine)


def guardar_mensaje(chat_id: str, rol: str, contenido: str):
    with SessionLocal() as session:
        session.add(Mensaje(chat_id=chat_id, rol=rol, contenido=contenido))
        session.commit()


def obtener_historial(chat_id: str, limite: int = 12) -> list[dict]:
    with SessionLocal() as session:
        registros = (
            session.query(Mensaje)
            .filter(Mensaje.chat_id == chat_id)
            .order_by(Mensaje.creado_en.desc())
            .limit(limite)
            .all()
        )
    registros.reverse()
    return [{"role": r.rol, "content": r.contenido} for r in registros]


def crear_pedido(chat_id: str, producto: dict, cantidad: int = 1) -> Pedido:
    with SessionLocal() as session:
        pedido = Pedido(
            chat_id=chat_id,
            producto_id=producto["id"],
            producto_nombre=producto["nombre"],
            precio=producto["precio"],
            cantidad=cantidad,
        )
        session.add(pedido)
        session.commit()
        session.refresh(pedido)
        return pedido
