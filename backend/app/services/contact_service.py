import uuid

from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


class ContactService:
    def __init__(self, db: Session):
        self.db = db

    def create_contact(self, user_id: str, data: ContactCreate) -> Contact:
        contact = Contact(
            contact_id=f"C{uuid.uuid4().hex[:8].upper()}",
            user_id=user_id,
            name=data.name,
            avatar=data.avatar,
            relationship=data.relationship,
            notes=data.notes,
        )
        self.db.add(contact)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def get_contacts(self, user_id: str, relationship: str = None, keyword: str = None,
                     page: int = 1, page_size: int = 20):
        query = self.db.query(Contact).filter(Contact.user_id == user_id)
        if relationship:
            query = query.filter(Contact.relationship == relationship)
        if keyword:
            query = query.filter(Contact.name.contains(keyword))
        total = query.count()
        contacts = query.offset((page - 1) * page_size).limit(page_size).all()

        # 补充每个联系人的纪念日数量
        # 注意：Anniversary 模型在 Task 8 才创建，此处做兼容处理；
        # Task 8 落地后应移除此 try/except 守卫。
        try:
            from app.models.anniversary import Anniversary
            for contact in contacts:
                contact.anniversary_count = self.db.query(Anniversary).filter(
                    Anniversary.contact_id == contact.contact_id,
                    Anniversary.status == 1
                ).count()
        except ImportError:
            for contact in contacts:
                contact.anniversary_count = 0

        return total, contacts

    def get_contact(self, user_id: str, contact_id: str) -> Contact:
        contact = self.db.query(Contact).filter(
            Contact.contact_id == contact_id,
            Contact.user_id == user_id
        ).first()
        if not contact:
            raise ValueError("联系人不存在")
        return contact

    def update_contact(self, user_id: str, contact_id: str, data: ContactUpdate) -> Contact:
        contact = self.get_contact(user_id, contact_id)
        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(contact, key, value)
        self.db.commit()
        self.db.refresh(contact)
        return contact

    def delete_contact(self, user_id: str, contact_id: str):
        contact = self.get_contact(user_id, contact_id)
        self.db.delete(contact)
        self.db.commit()

    def get_relationships(self, user_id: str):
        preset = [
            {"key": "father", "label": "父亲"},
            {"key": "mother", "label": "母亲"},
            {"key": "spouse", "label": "配偶"},
            {"key": "child", "label": "子女"},
            {"key": "friend", "label": "朋友"},
            {"key": "colleague", "label": "同事"},
            {"key": "grandparent", "label": "祖父母/外祖父母"},
            {"key": "sibling", "label": "兄弟姐妹"},
            {"key": "teacher", "label": "老师"},
            {"key": "other", "label": "其他"},
        ]
        # 自定义关系：查询该用户已创建但不在预置中的关系标签
        existing = self.db.query(Contact.relationship).filter(
            Contact.user_id == user_id
        ).distinct().all()
        preset_labels = {item["label"] for item in preset}
        custom = [
            {"key": f"custom_{i + 1}", "label": rel[0]}
            for i, rel in enumerate(existing)
            if rel[0] not in preset_labels
        ]
        return {"preset": preset, "custom": custom}
