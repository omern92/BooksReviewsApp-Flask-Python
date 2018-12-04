from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('postgres://ormczhitombrps:a803eb8a703e37662d85994f20b727c27bb7f6a3cf333854a47f986ab556c2de@ec2-54-246-101-215.eu-west-1.compute.amazonaws.com:5432/dc8k9mvfk8k0rt')
db = scoped_session(sessionmaker(bind=engine))

db.execute("ALTER TABLE post ADD COLUMN rating INTEGER")
db.commit()
