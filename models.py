from sqlalchemy import Integer, String, Column, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from flask_login import UserMixin
import datetime

from config import Base

class User(Base,UserMixin):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key = True)
    firstname = Column(String(20), nullable=False)
    lastname = Column(String(20), nullable=False)
    username = Column(String(20), nullable=False, unique=True)
    email = Column(String(20), nullable=False)
    password = Column(String(12), nullable=False)
    posts = relationship('Post', backref='author')
    comments = relationship('Comments', backref = 'author')
   

    def get_id(self):
        return self.id

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
        
class Contact(Base):
    __tablename__ = 'Contacts'

    id = Column(Integer, primary_key = True)
    fullname = Column(String(50), nullable = False)
    email = Column(String(20), nullable=False)
    message = Column(String(500), nullable=False)

class Post(Base):
    __tablename__ = 'Posts'
    id = Column(Integer, primary_key = True)
    title = Column(String(100), nullable=False)
    posted_date = Column(DateTime, nullable=False, default = datetime.datetime.now())
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('Users.id'), nullable=False)
    comments = relationship('Comments', backref='post')

class Comments(Base):
    __tablename__ = 'Comments'
    id = Column(Integer, primary_key = True)
    text = Column(Text, nullable=False)
    posted_on = Column(DateTime, nullable=False, default = datetime.datetime.now())
    name = Column(String(50), nullable = False)
    email = Column(String(40), nullable = False)
    author_id = Column(Integer, ForeignKey('Users.id', ondelete='CASCADE'), nullable=False)
    post_id = Column(Integer, ForeignKey('Posts.id', ondelete='CASCADE'), nullable=False)