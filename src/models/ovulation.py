from datetime import datetime
from src.models.user import db

class Ovulation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ovulation_date = db.Column(db.Date, nullable=False)
    basal_body_temperature = db.Column(db.Float, nullable=True)
    cervical_mucus = db.Column(db.String(50), nullable=True)  # dry, sticky, creamy, watery, egg-white
    symptoms = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Ovulation {self.ovulation_date}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'ovulation_date': self.ovulation_date.isoformat() if self.ovulation_date else None,
            'basal_body_temperature': self.basal_body_temperature,
            'cervical_mucus': self.cervical_mucus,
            'symptoms': self.symptoms,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

