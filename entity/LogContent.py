from sqlalchemy import Column, String, TIMESTAMP, text, Text, BigInteger, ForeignKey, TEXT
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship

from entity.TravelLog import TravelLog
from common.entity_base import Base


class LogContent(Base):
    __tablename__ = 'log_content'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    travel_log_id = Column(BigInteger(), ForeignKey("travel_log.id"))
    command = Column(String(20))
    argument = Column(TEXT)
    executed_at = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    content = Column(Text)
    photo = Column(LONGTEXT)

    travel_log = relationship(TravelLog, backref="content_of_travel_log")
