"""从章节目录 .env 或环境变量读取 URL、API Key、模型名。"""
from dataclasses import dataclass
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Settings:
    base_url: str
    api_key: str
    model: str


def load_settings():
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=False)
    names = ("OPENAI_BASE_URL", "OPENAI_API_KEY", "OPENAI_MODEL")
    values = [os.getenv(name, "").strip() for name in names]
    missing = [name for name, value in zip(names, values)
               if not value or value in ("your-api-key", "your-model-name")]
    if missing:
        raise ValueError("请在 .env 中填写：" + ", ".join(missing))
    if values[0].rstrip("/").endswith("/chat/completions"):
        raise ValueError("OPENAI_BASE_URL 填基础 URL，例如 https://api.openai.com/v1。")
    return Settings(*values)


def make_client(settings):
    from openai import OpenAI
    return OpenAI(base_url=settings.base_url, api_key=settings.api_key,
                  timeout=30.0, max_retries=0)
