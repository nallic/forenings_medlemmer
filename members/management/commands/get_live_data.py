from zipfile import ZipFile
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import DatabaseError
from members.models import Department, Union, Address
import requests
import shutil

MODELS_TO_LOAD = ["address", "union", "department"]


class Command(BaseCommand):
    help = "Gets public data and loads it into the system"

    def handle(self, *args, **options):
        in_database = (
            len(Department.objects.all()),
            len(Union.objects.all()),
            len(Address.objects.all()),
        )
        if in_database != (0, 0, 0):
            raise DatabaseError(
                "Du forsøgte at indsætte data i en ikke tom database. Det må man ikke "
            )

        temp_dir = "temp_dump"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

        print("Downloading data File")
        response = requests.get(
            "http://members.codingpirates.dk/static/public_data.zip"
        )
        if response.status_code != 200:
            raise ConnectionError("Could not get zip file")

        print("Unzipping")
        with open(f"{temp_dir}/dump.zip", "wb+") as zip:
            zip.write(response.content)

        with ZipFile(f"{temp_dir}/dump.zip", "r") as zipObj:
            zipObj.extractall(temp_dir)

        print("Reading dumps files")
        for model in MODELS_TO_LOAD:
            call_command("loaddata", f"{temp_dir}/{model}.json")

        # Remove temp dir
        shutil.rmtree(temp_dir)
