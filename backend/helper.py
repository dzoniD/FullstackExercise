import models
from sqlalchemy.orm import Session

def get_or_create_tag(name: str, db: Session) -> models.Tag:
    tag = db.query(models.Tag).filter(models.Tag.name == name).first()
    if not tag:
        tag = models.Tag(name=name)
        db.add(tag)
    
    return tag

