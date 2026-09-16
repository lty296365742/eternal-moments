from abc import ABC, abstractmethod


class SmsClient(ABC):
    @abstractmethod
    def send_code(self, phone: str, code: str, type: str) -> bool:
        pass


class MockSmsClient(SmsClient):
    def send_code(self, phone: str, code: str, type: str) -> bool:
        # 开发期：不实际发送，任何手机号都成功
        return True


class AliyunSmsClient(SmsClient):
    def send_code(self, phone: str, code: str, type: str) -> bool:
        # 生产期：接入阿里云短信 SDK
        # 这里返回 False 表示未配置
        return False


def get_sms_client() -> SmsClient:
    from app.core.config import settings
    if settings.SMS_PROVIDER == "aliyun":
        return AliyunSmsClient()
    return MockSmsClient()
