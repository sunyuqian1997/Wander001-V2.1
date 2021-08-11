from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from entity.LogContent import LogContent
from entity.TravelLog import TravelLog


class Storage(object):
    _mysql_engine = None

    def __init__(self):
        self._mysql_engine = create_engine("mysql+pymysql://wander:wander@localhost:3306/wander_storage?charset=utf8mb4",
                                           pool_pre_ping=True, max_overflow=5)

    def save_travel_log(self, travel_log: TravelLog, log_content=None, log_session=None):
        DBsession = sessionmaker(bind=self._mysql_engine)
        db_session = DBsession()
        try:
            # 生成一条记录旅行目的地，描述场景的旅行内容
            db_session.add(travel_log)

            if log_content is not None:
                db_session.flush()
                log_content.travel_log_id = travel_log.id
                db_session.add(log_content)

            if log_session is not None:
                # 设置log_session
                log_session.travel_log_id = travel_log.id

            db_session.commit()
        except:
            db_session.rollback()
            raise Exception(10006)

        return "本次行动记录已储存于2021年位点的时空终端"

    def get_travel_log_by_id(self, travel_log_id):
        DBsession = sessionmaker(bind=self._mysql_engine)
        session = DBsession()
        try:
            travel_log = session.query(TravelLog).filter_by(id=travel_log_id).first()
            return travel_log
        except:
            session.rollback()
            raise Exception(1008)

    def save_travel_log_content(self, log_content: LogContent):
        DBsession = sessionmaker(bind=self._mysql_engine)
        session = DBsession()
        try:
            session.add(log_content)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
            # raise Exception(10007)

        return "本次行动记录已更新"
