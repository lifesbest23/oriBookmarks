#!/usr/bin/python3
# script for storing origami bookmarks
# arguments
# 1 pdf file path
# 2 page number
import os
import sys

from bookmarks import BookmarkDB, Book, OrigamiModel
from rofi_lib import Rofi, notify

BM_DIR = "/home/lucas/tmp/bookmark-tests/"

# parse command line arguments
if (len(sys.argv) < 3):
    print("not enough arguments, two are needed!")
    sys.exit(0)

# split file path and name
filepath = sys.argv[1]
(path, filename) = os.path.split(filepath)

if not os.path.isfile(filepath):
    notify("ERROR " + filepath + " is no valid file", 1500)
    sys.exit(1)

pdfPage = sys.argv[2]

# Main body
db = BookmarkDB(BM_DIR)
rofi = Rofi()


def book_input(book: Book = None):
    title_array = [filename.split(".", 1)[0]]
    author_array = db.db_get_book_authors()
    title_row = 0
    author_row = 0
    if book:
        title_array.append(book.title)
        title_row = len(title_array)
        author_array.append(book.author)
        author_row = len(author_array)

    title = rofi.requestInput("Book Title",
                              title_array,
                              selected_row=title_row)

    if title is None:
        notify("No Title input, exiting")
        db.db_close()
        sys.exit(1)

    author = rofi.requestInput("Book Author",
                               author_array,
                               selected_row=author_row)

    if author is None:
        notify("No Author input, exiting", 1000)
        db.db_close()
        sys.exit(1)

    new_book = Book(title, author, filepath)
    db.db_insert_book(new_book)
    notify(f"Put {title} by {author} into book db", 1800)

    return new_book


def bookmark_input(page: int, book: Book):

    modelname = rofi.requestInput("Model Name", [])
    if modelname is None:
        notify("Not Model Name input, exiting")
        db.db_close()
        sys.exit(1)

    designer_array = db.db_get_book_authors() + db.db_get_designers()
    designer = rofi.requestInput("Designer", designer_array)
    if designer is None:
        notify("Not Designer Name input, exiting")
        db.db_close()
        sys.exit(1)

    papersize = rofi.requestInput("Paper Size", db.db_get_sizes())
    if papersize is None:
        notify("Not papersize input, exiting")
        db.db_close()
        sys.exit(1)

    params = dict()
    for field in ["stepcount", "difficulty", "importance", "notes"]:
        value = rofi.requestInput(f"Field {field}", [])
        if value:
            params[field] = value

    new_model = OrigamiModel(page, modelname, designer, papersize, **params)

    return new_model


book = db.get_book(filepath)
if book:
    if rofi.askOptions("Edit Book name, or author?",
                       message=f"{book.title} ({book.author})") == "yes":
        book_input(book)
    else:
        notify("Book is already in db")
else:
    notify("Book is not in db", 1000)
    book_input()

book = db.get_book(filepath)
bm = book.get_model(pdfPage)
if not bm:
    bm = bookmark_input(pdfPage, book)
    book.add_model(bm)
else:
    notify("Bookmark already present")

db.db_insert_book(book)
db.db_save()
sys.exit(1)
