"""Configuración centralizada: lee variables de entorno una sola vez para todo el proyecto."""
import os

from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app/data/pedidos.db")
