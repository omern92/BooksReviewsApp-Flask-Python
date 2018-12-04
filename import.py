import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('postgres://ormczhitombrps:a803eb8a703e37662d85994f20b727c27bb7f6a3cf333854a47f986ab556c2de@ec2-54-246-101-215.eu-west-1.compute.amazonaws.com:5432/dc8k9mvfk8k0rt')
db = scoped_session(sessionmaker(bind=engine))


def main():
    db.execute("CREATE TABLE Books (name VARCHAR NOT NULL, \
                                    year INTEGER NOT NULL, \
                                    author VARCHAR NOT NULL, \
                                    book_num VARCHAR PRIMARY KEY)")

    with open(r"C:\Users\nahum\Desktop\project1\books.csv", "r") as f:
        reader = csv.reader(f)
        next(reader)
        for isbn, title, author, year in reader:
            try:
                db.execute("INSERT INTO Books (name, year, author, book_num) VALUES (:title, :year, :author, :book_num)",
                           {"title": title, "year": year, "author": author, "book_num": isbn})
                print(f"{title} Added to the Books Database.")
            except Exception as e:
                print(f"{title} DIDNT ADD TO THE DATABASE------- {e}")
                db.rollback()
        db.commit()


if __name__ == "__main__":
    main()
