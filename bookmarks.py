# script for storing origami bookmarks
# class representing the database

import errno
import hashlib
import json
import logging
import os
import shlex
import sqlite3
import subprocess
import sys

# Create a Database class
# Exposes all author names
# Exposes all Book names
# Exposes all Creator Names


DB_NAME = "myOrigamiBookmarks.db"


def get_hash(filePath) -> str:
    # calculate pdf hash
    hasher = hashlib.md5()

    with open(filePath, "rb") as afile:
        buf = afile.read()
        hasher.update(buf)

    return hasher.hexdigest()


class Book:
    def __init__(self, filename, path, author="", hash="", title="", pages=0):
        self.filename = filename
        self.path = path
        filePath = path + "/" + filename
        if hash == "":
            if os.path.isfile(filePath):
                hash = get_hash(filePath)
            else:
                raise FileNotFoundError(errno.ENOENT,
                                        os.strerror(errno.ENOENT), filename)
        self.author = author
        self.title = title
        self.hash = hash
        self.pages = pages
        self.id = -1

    def getFromFilePath(filePath):
        (path, filename) = os.path.split(filePath)

        return Book(filename, path)

    def setId(self, id: int):
        if (id > 0):
            self.id = id


class BookmarkDB:

    def __init__(self, path: str = "/home/lucas/tmp/bookmark-tests/"):
        self.logger = logging.getLogger("DB")
        self.logger.setLevel(logging.DEBUG)

        self.path = path + DB_NAME
        # Connect to the database
        self.conn = sqlite3.connect('bookmarks.db')
        self.cursor = self.conn.cursor()

        # Create the bookmarks table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookmarks (
                id integer primary key,
                page integer,
                modelname text,
                designer text,
                papersize integer default 0,
                stepcount integer default 0,
                difficulty integer default 0,
                importance integer default 0,
                notes text default "",
                bookid integer
            )''')

        # Create the books table if it doesn't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                filename text,
                title text,
                author text,
                pages integer,
                hash blob primary key,
                path text
            )''')

        self.db_retreive_books()
        self.db_retreive_bookmarks()

    def db_retreive_books(self):
        self.cursor.execute('SELECT * from books')
        rows = self.cursor.fetchall()

        self.logger.debug("Retreiving books from DB")
        self.books = []
        for row in rows:
            book = {
                "filename": row[0],
                "title": row[1],
                "author": row[2],
                "pages": row[3],
                "hash": row[4],
                "path": row[5]
            }
            self.logger.debug("Found Book: %s", str(book))
            self.books.append(book)

    def db_retreive_bookmarks(self):
        self.cursor.execute('SELECT * from bookmarks')
        rows = self.cursor.fetchall()

        self.logger.debug("Retreiving bookmarks from DB")
        self.bookmarks = []
        for row in rows:
            bookmark = {
                "id": row[0],
                "page": row[1],
                "modelname": row[2],
                "designer": row[3],
                "papersize": row[4],
                "stepcount": row[5],
                "difficulty": row[6],
                "importance": row[7],
                "notes": row[8],
                "bookid": row[9],
            }
            self.logger.debug("Found Bookmark: %s", str(bookmark))
            self.bookmarks.append(bookmark)

    def db_get_book_authors(self) -> list[str]:
        return set([book["author"] for book in self.books])

    def db_get_book(self, path) -> dict | None:
        hash = get_hash(path)

        next_matching_book = next(
            (book for book in self.books if book["hash"] == hash),
            None)
        self.logger.debug("Found book %s in db: %s",
                          path, str(next_matching_book))
        return next_matching_book

    def db_insert_book(self, path, title, author):
        hash = get_hash(path)
        (path, filename) = os.path.split(path)

        pages = 100
        # Insert the current page, path, title, and author into the bookmarks table
        self.cursor.execute('''
                INSERT OR REPLACE INTO books (filename, title, author, pages, hash, path)
                          VALUES (?, ?, ?, ?, ?, ?)''',
                            (filename, title, author, pages, hash, path))

    def db_get_designers(self) -> list:
        self.cursor.execute('''SELECT DISTINCT (designer) FROM bookmarks''')

        return self.cursor.fetchall()

    def db_get_sizes(self) -> list:
        self.cursor.execute('''SELECT DISTINCT (papersize) FROM bookmarks''')

        return self.cursor.fetchall()

    def db_get_bookmarks(self, bhash: int) -> list | None:
        book = next((book for book in self.books if book["hash"] == bhash))
        if book is None:
            return None

        bookmarks = (mark for mark in self.bookmarks if mark["bookid"] == bhash)
        return bookmarks

    def db_has_bookmark(self, bookid: int, page: int) -> dict | None:
        marks = self.db_get_bookmarks(bookid)
        if marks is None:
            return None

        existing_mark = next(mark for mark in marks if mark["page"] == page)
        return existing_mark

    def db_insert_bookmark(self, mark: dict):
        try:
            args = (mark["page"], mark["modelname"], mark["designer"],
                    mark["papersize"], mark["stepcount"], mark["difficulty"],
                    mark["importance"], mark["notes"], mark["bookid"])
            self.cursor.execute('''
                INSERT OR REPLACE INTO bookmarks
                (
                    page,
                    modelname,
                    designer,
                    papersize,
                    stepcount,
                    difficult,
                    importance,
                    notes,
                    bookid
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', args)
        except Exception:
            self.logger.warn("Error getting mark arguments for insert")

    def db_close(self):
        # Save the changes
        self.conn.commit()

        # Close the database connection
        self.conn.close()
