from .database import TmsuConnect
import os
from pathlib import Path
import re
import shutil


def export_files(tm: TmsuConnect, all_files, folder="export"):
    """Method that exports all files into the following folder structure:
    folders: year
    filename: list_of_tags
    """

    if folder == "export":
        folder = os.path.join(os.getcwd(), folder)
    no_tags = 1
    # get all tags for each file
    for tmsufile in all_files:

        contains_year = False
        f_path = tmsufile.get_file_path()
        ext = tmsufile.name.split(".")[-1]
        print(f_path)
        tags = tm.get_tags_for_file(tmsufile)
        tags = [tag.name for tag in tags if tag.name not in ["Bilder", "unclassified", "nachträglich"]]
        year_folders = []
        for tag in tags:
            # breaks if one file has multiple year tags
            if is_year(tag):
                year_folder = os.path.join(folder, tag)
                Path(year_folder).mkdir(parents=True, exist_ok=True)
                tags.remove(tag)
                year_folders.append(year_folder)
                contains_year = True

        filename = '_'.join(tags)
        filename += f".{ext}"
        if not tags:
            filename = f"BILD_{no_tags}.{ext}"
            no_tags += 1

        if not contains_year:
            Path(folder, "unklar").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f_path, os.path.join(folder, "unklar", filename))
        for year_folder in year_folders:
            print(year_folder)
            filepath = os.path.join(year_folder, filename)
            while os.path.exists(filepath):
                fname_without_extension = filename.rsplit(".")[0]
                if re.match(r"\d", fname_without_extension):
                    number = str(int(fname_without_extension[-3:-1]) + 1).rjust(3, '0')
                    fname_without_extension = fname_without_extension.rsplit("_", 1)[0] + number
                else:
                    fname_without_extension += "_001"
                filename = fname_without_extension + ext
                filepath = os.path.join(year_folder, filename)

            shutil.copyfile(f_path, os.path.join(year_folder, filename))


def is_year(tag):
    year = re.compile(r"\d{4}")
    return year.match(tag)
