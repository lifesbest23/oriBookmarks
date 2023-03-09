# script for storing origami bookmarks
# class representing the database
from dataclasses import dataclass

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

DB_NAME = "myOrigamiBookmarks.json"


def get_hash(filePath) -> str:
    # calculate pdf hash
    hasher = hashlib.md5()

    with open(filePath, "rb") as afile:
        buf = afile.read()
        hasher.update(buf)

    return hasher.hexdigest()


@dataclass
class Book:
    title: str
    author: str
    filepath: str
    pdfhash: str = ""
    pages: int = -1

    def __post_init__(self):
        if self.pdfhash:
            return

        (path, filename) = os.path.split(self.filepath)
        self.path = path
        self.filename = filename

        self.pdfhash = get_hash(self.filepath)
        self.pages = 10

@dataclass
class OrigamiModel:
    page: int
    modelname: str
    designer: str
    papersize: str
    stepcount: int = -1
    difficulty: int = -1
    importance: int = -1
    notes: str = ""


class BookmarkDB:

    def __init__(self, path: str = "/home/lucas/tmp/bookmark-tests/"):
        self.logger = logging.getLogger("DB")
        self.logger.setLevel(logging.DEBUG)

        self.path = path + DB_NAME

    def db_get_book_authors(self) -> list[str]:
        return list([book["author"] for book in self.books])

    def db_get_book(self, path) -> dict | None:
        hash = get_hash(path)

        next_matching_book = next(
            (book for book in self.books if book["hash"] == hash), None)
        self.logger.debug("Found book %s in db: %s", path,
                          str(next_matching_book))
        return next_matching_book

    def db_insert_book(self, path, title, author):
        pass
        # Insert the current page, path, title, and author into the bookmarks table

    def db_get_designers(self) -> list:
        self.cursor.execute('''SELECT DISTINCT (designer) FROM bookmarks''')

        return self.cursor.fetchall()

    def db_get_sizes(self) -> list:
        self.cursor.execute('''SELECT DISTINCT (papersize) FROM bookmarks''')

        return self.cursor.fetchall()

    def db_get_bookmarks(self, bhash: int) -> list | None:
        book = next((book for book in self.books if book["hash"] == bhash),
                    None)
        if book is None:
            return None

        bookmarks = (mark for mark in self.bookmarks
                     if mark["bookid"] == bhash)
        return bookmarks

    def db_has_bookmark(self, bhash: int, page: int) -> dict | None:
        marks = self.db_get_bookmarks(bhash)
        if marks is None:
            return None

        print(marks)
        existing_mark = next((mark for mark in marks if mark["page"] == page),
                             None)
        return existing_mark

    def db_insert_bookmark(self, mark: dict):
        pass

    def db_close(self):
        pass
