#!/usr/bin/python3
# script for storing origami bookmarks
# arguments
# 1 pdf file path
# 2 page number
import os
import sys

from bookmarks import BookmarkDB
from rofi_lib import Rofi, notify

BM_DIR = "/home/lucas/tmp/bookmark-tests/"

# parse command line arguments
if (len(sys.argv) < 3):
    print("not enough arguments, two are needed!")
    sys.exit(0)

# split file path and name
filePath = sys.argv[1]
(path, filename) = os.path.split(filePath)

if not os.path.isfile(filePath):
    notify("ERROR " + filePath + " is no valid file", 1500)
    sys.exit(1)

pdfPage = sys.argv[2]

# Main body
db = BookmarkDB(BM_DIR)
rofi = Rofi()

book = db.db_get_book(filePath)
if book is None:
    notify("Book is not in db", 1000)

    title = rofi.requestInput("Book Title", [filename.split(".", 1)[0]])

    if title is None:
        notify("No Title input, exiting")
        db.db_close()
        sys.exit(1)

    author = rofi.requestInput("Book Author", db.db_get_book_authors())

    if author is None:
        notify("No Author input, exiting", 1000)
        db.db_close()
        sys.exit(1)

    db.db_insert_book(filePath, title, author)
    notify(f"Put {title} by {author} into book db", 1800)
else:
    notify("Book is already in db")

db.db_close()
sys.exit(1)
