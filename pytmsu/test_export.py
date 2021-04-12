from .export import export_files

import pytest

def check_how_many_files():


def test_export_files(tmsu, all_files, folder="export"):
    """Checks that it exports all files"""
    number_of_pictures_in_db = all_files
    
    export_files(tm, all_files, folder="export")

