from datetime import UTC, datetime

from . import db

# Поля, которые разрешаю заполнять и менять через API.
EDITABLE_FIELDS = ('title', 'text', 'source', 'added_by')


class Opinion(db.Model):
    """Мнение о фильме."""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)
    source = db.Column(db.String(256))
    # Передаю функцию, а не её результат: так время считается
    # для каждой новой записи, а не один раз при запуске сервера.
    timestamp = db.Column(
        db.DateTime, index=True, default=lambda: datetime.now(UTC)
    )
    added_by = db.Column(db.String(64))

    def to_dict(self):
        """Вернуть мнение в виде словаря."""
        return dict(
            id=self.id,
            title=self.title,
            text=self.text,
            source=self.source,
            timestamp=self.timestamp,
            added_by=self.added_by,
        )

    def from_dict(self, data):
        """Заполнить поля мнения значениями из словаря."""
        # Беру только разрешённые поля и только те, что пришли в data.
        for field in EDITABLE_FIELDS:
            if field in data:
                setattr(self, field, data[field])
