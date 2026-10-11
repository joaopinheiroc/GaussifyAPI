from datetime import datetime, timezone
from api.extensions import db


class Calculation(db.Model):
    __tablename__ = "calculations"

    id = db.Column(db.Integer, primary_key = True)

    mean = db.Column(db.Float, nullable=False)
    std_dev = db.Column(db.Float, nullable=False)
    target_x = db.Column(db.Float, nullable=False)

    probability = db.Column(db.Float, nullable=False)

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    __table_args__ = (
        db.CheckConstraint('std_dev > 0', name='check_std_dev_positive'),
        db.CheckConstraint('probability >= 0 AND probability <= 1', name='check_probability_range'),
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "mean": self.mean,
            "std_dev": self.std_dev,
            "target_x": self.target_x,
            "probability": self.probability,
            "created_at": self.created_at.isoformat()
        }
    def __repr__(self) -> str:
        return f"<Calculation id={self.id} probability={self.probability:.4f}>"