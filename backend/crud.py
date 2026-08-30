from sqlalchemy.orm import Session

from backend.models import User, Message


# -------------------------
# USER FUNCTIONS
# -------------------------

def get_user_by_google_id(
    db: Session,
    google_id: str
):
    return db.query(User).filter(
        User.google_id == google_id
    ).first()



def create_google_user(
    db: Session,
    google_id: str,
    email: str,
    name: str,
    profile_picture: str | None = None
):

    user = User(
        google_id=google_id,
        email=email,
        name=name,
        profile_picture=profile_picture
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# -------------------------
# MESSAGE FUNCTIONS
# -------------------------

def save_message(
    db: Session,
    user_id: int,
    role: str,
    content: str
):

    message = Message(
        user_id=user_id,
        role=role,
        content=content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_chat(
    db: Session,
    user_id: int
):

    return db.query(Message).filter(
        Message.user_id == user_id
    ).order_by(
        Message.id
    ).all()


def get_recent_messages(
    db: Session,
    user_id: int,
    limit: int = 20
):

    return db.query(Message).filter(
        Message.user_id == user_id
    ).order_by(
        Message.id.desc()
    ).limit(limit).all()[::-1]