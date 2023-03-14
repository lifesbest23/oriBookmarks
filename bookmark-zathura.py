#!/usr/bin/python3
# script for storing origami bookmarks
# arguments
# 1 pdf file path
# 2 page number
import os
import sys

from bookmarks import BookmarkDB, Book, OrigamiModel
from rofi_lib import Rofi, notify

BM_DIR = os.path.expanduser("~/tmp/bookmark-tests/")

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


def notify_quit(msg):
    notify(msg)
    sys.exit(1)


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
        notify_quit("No Title input, exiting")

    author = rofi.requestInput("Book Author",
                               author_array,
                               selected_row=author_row)

    if author is None:
        notify_quit("No Author input, exiting", 1000)

    if book:
        book.title = title
        book.author = author
    else:
        book = Book(title, author, filepath)
    notify(f"Put {title} by {author} into book db", 1800)

    return book


def bookmark_input(page: int, model: OrigamiModel):
    modelname = rofi.requestInput("Model Name", [])
    if modelname is None:
        notify("No Model Name input, exiting")

    designer_array = db.db_get_book_authors() + db.db_get_designers()
    designer = rofi.requestInput("Designer", designer_array)
    if designer is None:
        notify_quit("No Designer Name input, exiting")

    papersize = rofi.requestInput("Paper Size", db.db_get_sizes())
    if papersize is None:
        notify_quit("No papersize input, exiting")

    params = dict()
    for field in ["stepcount", "difficulty", "importance", "notes"]:
        value = rofi.requestInput(f"Field {field}", [])
        if value:
            params[field] = value

    new_model = OrigamiModel(page, modelname, designer, papersize, **params)

    return new_model


bookmark_opts = ["Add/Edit Bookmark"]

book = db.get_book(filepath)
if not book:
    notify("Book is not in db", 1000)
    book = book_input()
    db.db_insert_book(book)
else:
    bookmark_opts.append("Edit Book")

book = db.get_book(filepath)
if len(book.models) > 0:
    bookmark_opts.append("Add ending to last model")
    bookmark_opts.append("Show Bookmarks")

function = rofi.askOptions("Bookmarking function",
                           message=f"What subfunction to run",
                           options=bookmark_opts)

if function == "Edit Book":
    book = book_input(book)
if function == "Add/Edit Bookmark":
    bm = book.get_model(pdfPage)
    if not bm:
        bm = bookmark_input(pdfPage, book)
        book.add_model(bm)
    else:
        notify("Bookmark already present")
if function == "Add ending to last model":
    if not book.get_last_model().lastpage or \
            book.get_last_model().lastpage == -1:
        book.get_last_model().lastpage = pdfPage
        notify("Added last Page of last model")
    else:
        notify("Last Page of model was already set!")
if function == "Show Bookmarks":
    options = [
        f"P{model.page} {model.modelname} by {model.designer}"
        for model in book.get_sorted_models()
    ]
    rofi.askOptions("Models list", options=options)

db.db_insert_book(book)
db.db_save()
notify_quit("Exiting properly")
