from sqlalchemy import Column, Integer, String, TIMESTAMP, text, JSON, Text, BigInteger
from sqlalchemy.dialects.mysql import LONGTEXT
from common.entity_base import Base


class TravelLog(Base):
    __tablename__ = 'travel_log'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    talker_id = Column(String(100))
    talker_name = Column(String(50))
    talker_gender = Column(String(8))
    talker_province = Column(String(20))
    talker_city = Column(String(20))
    talking_time = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    address = Column(String(100))
    location = Column(JSON)
    future_year = Column(Integer)
    content = Column(Text)
    photo = Column(LONGTEXT)
    style = Column(Integer)


