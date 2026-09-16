import json
import logging
from abc import ABC, abstractmethod

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)

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
        prompt = f"""你是一位拥有20年情感表达经验的高级情感专家。

请根据以下信息生成一段祝福语：
- 接收者与用户的关系：{relationship}
- 节假日名称：{event_title}
- 接收者称呼/姓名：{receiver_name}

要求：
1. 真诚自然，避免空洞套话
2. 根据关系调整语言风格
3. 2-4句话，50-120字
4. 不要使用表情符号、网络流行语或陈旧表达
5. 直接输出祝福语正文"""
        return self._chat(prompt)

    def recommend_gifts(self, relationship: str, receiver_name: str,
                        event_title: str) -> list:
        prompt = f"""你是一位资深礼物选品博主。

请根据以下信息推荐3-5款适合的礼品：
- 收礼人与用户的关系：{relationship}
- 纪念日类型：{event_title}
- 收礼者称呼/姓名：{receiver_name}

要求：
1. 因人选礼，价格合理
2. 推荐知名品牌，优先京东/天猫在售商品
3. 每个推荐需说明具体推荐理由

严格按以下JSON数组格式输出，不要输出任何其他内容：
[
  {{
    "name": "商品名称",
    "price": 参考价格（数字，单位元）,
    "reason": "推荐理由（一句话，20-50字）",
    "purchase_url": "推荐购买链接"
  }}
]"""
        content = self._chat(prompt).strip()
        if content.startswith("```"):
            lines = content.splitlines()
            lines = lines[1:]
            if lines and lines[-1].strip().startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()
        try:
            return json.loads(content)
        except ValueError:
            logger.warning("AI 礼物推荐返回非 JSON 内容，回退到模拟推荐: %s", content[:200])
            return MockAIClient().recommend_gifts(relationship, receiver_name, event_title)


def get_ai_client() -> AIClient:
    if settings.AI_PROVIDER == "volcano_ark" and settings.VOLCANO_ARK_API_KEY:
        return VolcanoArkClient()
    return MockAIClient()
