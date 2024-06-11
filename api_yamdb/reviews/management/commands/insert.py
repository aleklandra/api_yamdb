import csv
import sqlite3
import os
from django.core.management.base import BaseCommand
from pathlib import Path
from api_yamdb import settings
from reviews.models import (Categories, Genre, Review, User, Title,
                            GenreTitle, Comment)

DATA_DICT = {
    'user.csv': User,
    'categories.csv': Categories,
    'genre.csv': Genre,
    'title.csv': Title,
    'genretitle.csv': GenreTitle,
    'review.csv': Review,
    'comment.csv': Comment
}


class Command(BaseCommand):
    help = 'Insert csv into data model'

    def handle(self, *args, **options):
        dir = Path(f'{settings.BASE_DIR}/static/data')

        for file in DATA_DICT:
            with open(Path(dir, file), 'r', encoding="utf8") as f:
                dict_file = csv.DictReader(f)
                yamdb_data = [DATA_DICT[file](**row) for row in dict_file]
                DATA_DICT[file].objects.bulk_create(yamdb_data)
