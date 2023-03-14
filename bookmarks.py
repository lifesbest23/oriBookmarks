# script for storing origami bookmarks
# class representing the database
from dataclasses import dataclass, field, asdict

import hashlib
import json
import logging
import os

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
class OrigamiModel:
    page: int
    modelname: str
    designer: str
    papersize: int
    lastpage: int = -1
    stepcount: int = -1
    difficulty: int = -1
    importance: int = -1
    notes: str = None


@dataclass
class Book:
    title: str
    author: str
    filepath: str
    pdfhash: str = ""
    pages: int = -1
    models: list[OrigamiModel] = field(default_factory=list)

    def __post_init__(self):
        if self.pdfhash:
            return

        (path, filename) = os.path.split(self.filepath)
        self.path = path
        self.filename = filename

        self.pdfhash = get_hash(self.filepath)
        self.pages = 10

    def get_last_model(self) -> OrigamiModel | None:
        if self.models:
            return self.models[-1]
        return None

    def get_model(self, page: int) -> OrigamiModel | None:
        next_matching_model = next(
            (model for model in self.models if model.page == page), None)
        return next_matching_model

    def add_model(self, model: OrigamiModel):
        old = self.get_model(model.page)
        if old:
            self.models.remove(old)

        self.models.append(model)

    def get_sorted_models(self) -> list[OrigamiModel]:
        return sorted(self.models, key=lambda x: x.page)


class BookmarkDB:
    books: list[Book]

    def __init__(self, path: str = "/home/lucas/tmp/bookmark-tests/"):
        self.logger = logging.getLogger("DB")
        self.logger.setLevel(logging.DEBUG)

        self.books = list()
        self.path = path + DB_NAME
        # load from file into list of Books
        data = None
        with open(self.path, "r") as json_file:
            data = json.load(json_file)

        if data is None:
            self.log.warn(f"Json DB file {self.path} could not be read")
            data = {}

        for b in data:
            model_list = b.pop("models")
            models = [OrigamiModel(**model_data) for model_data in model_list]
            self.books.append(Book(models=models, **b))

    def db_save(self):
        with open(self.path, "w") as json_file:
            json.dump([asdict(book) for book in self.books], json_file)
            self.logger.debug(f"Saved json db to {self.path}")

    def get_book(self, path) -> Book | None:
        hash_t = get_hash(path)

        next_matching_book = next(
            (book for book in self.books if book.pdfhash == hash_t), None)
        self.logger.debug("Found book %s in db: %s", path,
                          str(next_matching_book))
        return next_matching_book

    def db_get_book_authors(self) -> list[str]:
        return list(b.author for b in self.books)

    def db_insert_book(self, book: Book):
        old = self.get_book(book.filepath)
        if old:
            self.books.remove(old)

        self.books.append(book)

    def db_get_designers(self) -> list[str]:
        designers = []
        for book in self.books:
            for model in book.models:
                designers.append(model.designer)
        return designers

    def db_get_sizes(self) -> list[int]:
        sizes = []
        for book in self.books:
            for model in book.models:
                sizes.append(model.size)
        return sizes
