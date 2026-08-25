"""Configuración compartida de pytest: usa una base de datos SQLite temporal para no tocar la real."""
import os
import tempfile

_tmp_dir = tempfile.mkdtemp(prefix="techstorebot_tests_")
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_tmp_dir}/test_pedidos.db")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-api-key")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "test-bot-token")
