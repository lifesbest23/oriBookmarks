# script for storing origami bookmarks
# class representing the database

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
                author text,
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
                id integer primary key,
                path text,
                title text,
                author text,
                pages integer,
                hash blob
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
                "id": row[0],
                "filename": row[1],
                "title": row[2],
                "author": row[3],
                "pages": row[4],
                "hash": row[5]
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
                "author": row[3],
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
        (_, path) = os.path.split(path)
        hash = get_hash(path)

        pages = 100
        # Insert the current page, path, title, and author into the bookmarks table
        self.conn.execute('''
                INSERT INTO books (path, title, author, pages, hash)
                          VALUES (?, ?, ?, ?, ?)''',
                          (path, title, author, pages, hash))

    def db_exit(self):
        # Save the changes
        self.conn.commit()

        # Close the database connection
        self.conn.close()
