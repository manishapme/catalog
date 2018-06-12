import datetime
from sqlalchemy import(
    create_engine,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    relationship,
    sessionmaker,
)


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'  # NOTE 'user' is reserved table in postgres

    id = Column(Integer, primary_key=True)
    username = Column(String(32), index=True, nullable=False)
    email = Column(String(64), nullable=False)
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_date': self.created_date,
            'last_updated': self.last_updated,
        }


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')
    items = relationship('Item', back_populates='category')
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    @property
    def serialize(self):
        item_dict = {item.id: item.serialize for item in self.items }
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
            'created_date': self.created_date,
            'last_updated': self.last_updated,
            'items': {item.id: item.serialize for item in self.items },
        }


class Item(Base):
    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String)
    url = Column(String(128))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship('Category', back_populates='items')
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')
    created_date = Column(DateTime, default=datetime.datetime.utcnow)
    last_updated = Column(DateTime, onupdate=datetime.datetime.utcnow)

    def update_item(self, **kwargs):
        """Update existing item data."""

        self.name = kwargs.get('name', self.name)
        self.description = kwargs.get('description', self.description)
        self.url = kwargs.get('url', self.url)
        self.category_id = kwargs.get('category_id', self.category_id)
        session.commit()

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'url': self.url,
            'category_id': self.category_id,
            'user_id': self.user_id,
            'created_date': self.created_date,
            'last_updated': self.last_updated,
        }

def add_category(name, user_id=None):
    """Add new category."""

    category = Category(name=name, user_id=user_id)
    session.add(category)
    session.commit()
    return category


def add_item(name, description, url, category_id, user_id=None):
    """Add new item."""

    item = Item(name=name, description=description, url=url,
                category_id=category_id, user_id=user_id)
    session.add(item)
    session.commit()
    return item


def add_user(username, email):
    """Add new user."""

    user = User(username=username, email=email)
    session.add(user)
    session.commit()
    return user


def delete_category(category_id):
    """Delete one or all categories"""

    if category_id:
        session.query(Category).filter_by(id=category_id).delete()
    else:
        session.query(Category).delete()
    session.commit()


def delete_item(item_id):
    """Delete one or all items"""

    if item_id:
        session.query(Item).filter_by(id=item_id).delete()
    else:
        session.query(Item).delete()
    session.commit()


def delete_user(user_id):
    """Delete one or all users"""

    if user_id:
        session.query(User).filter_by(id=user_id).delete()
    else:
        session.query(User).delete()
    session.commit()


def get_category(category_id):
    """Get one or all categories"""

    if category_id:
        return session.query(Category).filter_by(id=category_id).order_by(Category.name.asc())  # noqa
    else:
        return session.query(Category).order_by(Category.name.asc())


def get_category_items(category_id):
    """Get all items in given category"""

    if category_id:
        return session.query(Item).filter_by(category_id=category_id).order_by(Item.name.asc())  # noqa
    else:
        return session.query(Item).order_by(Item.id.desc())


def get_item(item_id):
    """Get one or all items"""

    if item_id:
        return session.query(Item).filter_by(id=item_id).one()
    else:
        return session.query(Item).all()


def get_user(user_id):
    """Get one or all users"""

    if user_id:
        return session.query(User).filter_by(id=user_id).one()
    else:
        return session.query(User).all()


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def connect_to_db():
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    engine = create_engine('postgresql:///catalog')
    Base.metadata.create_all(engine)
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


session = connect_to_db()
