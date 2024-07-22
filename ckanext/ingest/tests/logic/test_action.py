import mimetypes
import os
from typing import Optional

import pytest

import ckan.plugins.toolkit as tk
from ckan.tests.helpers import call_action

from ckanext.ingest import shared


@pytest.fixture(scope="session")
def source():
    data = os.path.join(os.path.dirname(__file__), "data")

    def reader(filename: str, mime: Optional[str] = None):
        if mime is None:
            mime, _enc = mimetypes.guess_type(filename)

        src = open(os.path.join(data, filename), "rb")  # noqa
        return shared.make_storage(src, mimetype=mime)

    return reader


@pytest.mark.usefixtures("with_plugins")
class TestExtractRecords:
    @pytest.mark.parametrize(
        "filename",
        ["example.csv", "example.zip", "zipped_zip.zip"],
    )
    def test_basic(self, source, filename):
        records = call_action("ingest_extract_records", source=source(filename))

        assert records == [
            {"name": "hello", "title": "Hello", "type": "dataset"},
            {"name": "world", "title": "World", "type": "dataset"},
        ]

    def test_no_source(self, source):
        with pytest.raises(tk.ValidationError):
            call_action("ingest_extract_records")

    def test_unmapped(self, source):
        records = call_action("ingest_extract_records", source=source("unmapped.csv"))
        assert records == [{"type": "dataset"}, {"type": "dataset"}]


@pytest.mark.usefixtures("with_plugins", "clean_db")
class TestImportRecords:
    @pytest.mark.parametrize(
        "filename",
        ["example.csv", "example.zip", "zipped_zip.zip"],
    )
    def test_basic(self, source, filename):
        result = call_action("ingest_import_records", source=source(filename))
        assert result == {"fail": 0, "success": 2}

    def test_no_source(self, source):
        with pytest.raises(tk.ValidationError):
            call_action("ingest_import_records")

    def test_unmapped(self, source):
        result = call_action("ingest_import_records", source=source("unmapped.csv"))
        assert result == {"fail": 2, "success": 0}
