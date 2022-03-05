import mimetypes
import os
from typing import Optional
from werkzeug.datastructures import FileStorage
import pytest
from ckan.tests.helpers import call_action

@pytest.fixture(scope="session")
def source():
    data = os.path.join(
        os.path.dirname(__file__),
        "data"
    )
    def reader(filename: str, mime: Optional[str] = None):
        if mime is None:
            mime, _enc = mimetypes.guess_type(filename)

        src = open(os.path.join(data, filename), "rb")
        return FileStorage(src, content_type=mime)

    return reader



class TestExtractRecords:
    @pytest.mark.parametrize("filename", ["example.csv", "example.zip", "zipped_zip.zip"])
    def test_basic(self, source, filename):
        records = call_action("ingest_extract_records", source=source(filename))
        assert records == [{'name': 'hello', 'title': 'Hello', 'type': 'dataset'},
                           {'name': 'world', 'title': 'World', 'type': 'dataset'}]

    def test_unmapped(self, source):
        records = call_action("ingest_extract_records", source=source("unmapped.csv"))
        assert records == [{'type': 'dataset'},
                           {'type': 'dataset'}]