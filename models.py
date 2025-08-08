from datetime import datetime
from app import db
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin
from sqlalchemy import UniqueConstraint

class ChoreTemplate(db.Model):
    __tablename__ = 'chore_templates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)      # e.g., "Walk the dog"
    category = db.Column(db.String(50), nullable=False)   # e.g., "Pet Care"
    is_active = db.Column(db.Boolean, default=True)

# (IMPORTANT) This table is mandatory for Replit Auth, don't drop it.
#class User(UserMixin, db.Model):
#    __tablename__ = 'users'
#    id = db.Column(db.String, primary_key=True)
#    email = db.Column(db.String, unique=True, nullable=True)
#    first_name = db.Column(db.String, nullable=True)
#    last_name = db.Column(db.String, nullable=True)
#    profile_image_url = db.Column(db.String, nullable=True)
#    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    
#    created_at = db.Column(db.DateTime, default=datetime.now)
#    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# (IMPORTANT) This table is mandatory for Replit Auth, don't drop it.
#class OAuth(OAuthConsumerMixin, db.Model):
#    user_id = db.Column(db.String, db.ForeignKey(User.id))
#    browser_session_key = db.Column(db.String, nullable=False)
#    user = db.relationship(User)

#    __table_args__ = (UniqueConstraint(
#        'user_id',
#        'browser_session_key',
#        'provider',
#        name='uq_user_browser_session_key_provider',
#    ),)
 
