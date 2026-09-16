import json
from abc import ABC, abstractmethod

import requests

from app.core.config import settings

ARK_API_URL = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"


class AIClient(ABC):
    @abstractmethod
    def generate_blessing(self, relationship: str, receiver_name: str,
                          event_title: str, event_date: str) -> str:
        """根据事件信息生成祝福语"""

    @abstractmethod
    def recommend_gifts(self, relationship: str, receiver_name: str,
                        event_title: str) -> list:
        """根据事件信息推荐礼物列表"""


class MockAIClient(AIClient):
    def generate_blessing(self, relationship: str, receiver_name: str,
                          event_title: str, event_date: str) -> str:
        return f"亲爱的{receiver_name}，{event_title}快乐，愿您健康幸福每一天！"

    def recommend_gifts(self, relationship: str, receiver_name: str,
                        event_title: str) -> list:
        return ["一束鲜花", "手写贺卡", "暖心礼物"]


class VolcanoArkClient(AIClient):
    def _chat(self, prompt: str) -> str:
        resp = requests.post(
            ARK_API_URL,
            headers={"Authorization": f"Bearer {settings.VOLCANO_ARK_API_KEY}"},
            json={
                "model": settings.VOLCANO_ARK_MODEL,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def generate_blessing(self, relationship: str, receiver_name: str,
                          event_title: str, event_date: str) -> str:
        prompt = (
            f"我的{relationship}{receiver_name}的{event_title}是{event_date}，"
            "请写一段100字以内、温暖真诚的中文祝福语，直接输出祝福内容。"
        )
        return self._chat(prompt)

    def recommend_gifts(self, relationship: str, receiver_name: str,
                        event_title: str) -> list:
        prompt = (
            f"我的{relationship}{receiver_name}的{event_title}快到了，"
            '请推荐3个合适的礼物，以JSON数组格式返回，如 ["礼物1", "礼物2", "礼物3"]，'
            "只输出JSON。"
        )
        content = self._chat(prompt).strip()
        if content.startswith("```"):
            lines = content.splitlines()
            lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
        return json.loads(content)


def get_ai_client() -> AIClient:
    if settings.AI_PROVIDER == "volcano":
        return VolcanoArkClient()
    return MockAIClient()
