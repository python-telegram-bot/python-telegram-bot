#!/usr/bin/env python
#
# A library that provides a Python interface to the Telegram Bot API
# Copyright (C) 2015-2024
# Leandro Toledo de Souza <devs@python-telegram-bot.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser Public License for more details.
#
# You should have received a copy of the GNU Lesser Public License
# along with this program.  If not, see [http://www.gnu.org/licenses/].
import os
from pathlib import Path
from tempfile import TemporaryFile, mkstemp

import pytest

from telegram import File, FileCredentials, Voice
from telegram.error import TelegramError
from tests.auxil.files import data_file
from tests.auxil.slots import mro_slots


@pytest.fixture(scope="module")
def file(bot):
    file = File(
        TestFileBase.file_id,
        TestFileBase.file_unique_id,
        file_path=TestFileBase.file_path,
        file_size=TestFileBase.file_size,
    )
    file.set_bot(bot)
    file._unfreeze()
    return file


@pytest.fixture(scope="module")
def encrypted_file(bot):
    # check https://github.com/python-telegram-bot/python-telegram-bot/wiki/\
    # PTB-test-writing-knowledge-base#how-to-generate-encrypted-passport-files
    # if you want to know the source of these values
    fc = FileCredentials(
        "Oq3G4sX+bKZthoyms1YlPqvWou9esb+z0Bi/KqQUG8s=",
        "Pt7fKPgYWKA/7a8E64Ea1X8C+Wf7Ky1tF4ANBl63vl4=",
    )
    ef = File(
        TestFileBase.file_id,
        TestFileBase.file_unique_id,
        TestFileBase.file_size,
        TestFileBase.file_path,
    )
    ef.set_bot(bot)
    ef.set_credentials(fc)
    return ef


@pytest.fixture(scope="module")
def encrypted_local_file(bot):
    # check encrypted_file() for the source of the fc values
    fc = FileCredentials(
        "Oq3G4sX+bKZthoyms1YlPqvWou9esb+z0Bi/KqQUG8s=",
        "Pt7fKPgYWKA/7a8E64Ea1X8C+Wf7Ky1tF4ANBl63vl4=",
    )
    ef = File(
        TestFileBase.file_id,
        TestFileBase.file_unique_id,
        TestFileBase.file_size,
        file_path=str(data_file("image_encrypted.jpg")),
    )
    ef.set_bot(bot)
    ef.set_credentials(fc)
    return ef


@pytest.fixture(scope="module")
def local_file(bot):
    file = File(
        TestFileBase.file_id,
        TestFileBase.file_unique_id,
        file_path=str(data_file("local_file.txt")),
        file_size=TestFileBase.file_size,
    )
    file.set_bot(bot)
    return file


class TestFileBase:
    file_id = "NOTVALIDDOESNOTMATTER"
    file_unique_id = "adc3145fd2e84d95b64d68eaa22aa33e"
    file_path = (
        "https://api.org/file/bot133505823:AAHZFMHno3mzVLErU5b5jJvaeG--qUyLyG0/document/file_3"
    )
    file_size = 28232
    file_content = "Saint-Saëns".encode()  # Intentionally contains unicode chars.


class TestFileWithoutRequest(TestFileBase):
    def test_slot_behaviour(self, file):
        for attr in file.__slots__:
            assert getattr(file, attr, "err") != "err", f"got extra slot '{attr}'"
        assert len(mro_slots(file)) == len(set(mro_slots(file))), "duplicate slot"

    def test_de_json(self, bot):
        json_dict = {
            "file_id": self.file_id,
            "file_unique_id": self.file_unique_id,
            "file_path": self.file_path,
            "file_size": self.file_size,
        }
        new_file = File.de_json(json_dict, bot)
        assert new_file.api_kwargs == {}

        assert new_file.file_id == self.file_id
        assert new_file.file_unique_id == self.file_unique_id
        assert new_file.file_path == self.file_path
        assert new_file.file_size == self.file_size

    def test_to_dict(self, file):
        file_dict = file.to_dict()

        assert isinstance(file_dict, dict)
        assert file_dict["file_id"] == file.file_id
        assert file_dict["file_unique_id"] == file.file_unique_id
        assert file_dict["file_path"] == file.file_path
        assert file_dict["file_size"] == file.file_size

    def test_equality(self, bot):
        a = File(self.file_id, self.file_unique_id, bot)
        b = File("", self.file_unique_id, bot)
        c = File(self.file_id, self.file_unique_id, None)
        d = File("", "", bot)
        e = Voice(self.file_id, self.file_unique_id, 0)

        assert a == b
        assert hash(a) == hash(b)
        assert a is not b

        assert a == c
        assert hash(a) == hash(c)

        assert a != d
        assert hash(a) != hash(d)

        assert a != e
        assert hash(a) != hash(e)

    async def test_download(self, monkeypatch, file):
        async def test(*args, **kwargs):
            return self.file_content

        monkeypatch.setattr(file.get_bot().request, "retrieve", test)
        out_file = await file.download_to_drive()

        try:
            assert out_file.read_bytes() == self.file_content
        finally:
            out_file.unlink(missing_ok=True)

    @pytest.mark.parametrize(
        "custom_path_type", [str, Path], ids=["str custom_path", "pathlib.Path custom_path"]
    )
    async def test_download_custom_path(self, monkeypatch, file, custom_path_type):
        async def test(*args, **kwargs):
            return self.file_content

        monkeypatch.setattr(file.get_bot().request, "retrieve", test)
        file_handle, custom_path = mkstemp()
        custom_path = Path(custom_path)
        try:
            out_file = await file.download_to_drive(custom_path_type(custom_path))
            assert out_file == custom_path
            assert out_file.read_bytes() == self.file_content
        finally:
            os.close(file_handle)
            custom_path.unlink(missing_ok=True)

    async def test_download_no_filename(self, monkeypatch, file):
        async def test(*args, **kwargs):
            return self.file_content

        file.file_path = None

        monkeypatch.setattr(file.get_bot().request, "retrieve", test)
        out_file = await file.download_to_drive()

        assert str(out_file)[-len(file.file_id) :] == file.file_id
        try:
            assert out_file.read_bytes() == self.file_content
        finally:
            out_file.unlink(missing_ok=True)

    async def test_download_file_obj(self, monkeypatch, file):
        async def test(*args, **kwargs):
            return self.file_content

        monkeypatch.setattr(file.get_bot().request, "retrieve", test)
        with TemporaryFile() as custom_fobj:
            await file.download_to_memory(out=custom_fobj)
            custom_fobj.seek(0)
            assert custom_fobj.read() == self.file_content

    async def test_download_bytearray(self, monkeypatch, file):
        async def test(*args, **kwargs):
            return self.file_content

        monkeypatch.setattr(file.get_bot().request, "retrieve", test)

        # Check that a download to a newly allocated bytearray works.
        buf = await file.download_as_bytearray()
        assert buf == bytearray(self.file_content)

        # Check that a download to a given bytearray works (extends the bytearray).
        buf2 = buf[:]
        buf3 = await file.download_as_bytearray(buf=buf2)
        assert buf3 is buf2
        assert buf2[len(buf) :] == buf
        assert buf2[: len(buf)] == buf

    async def test_download_encrypted(self, monkeypatch, bot, encrypted_file):
        async def test(*args, **kwargs):
            return data_file("image_encrypted.jpg").read_bytes()

        monkeypatch.setattr(encrypted_file.get_bot().request, "retrieve", test)
        out_file = await encrypted_file.download_to_drive()

        try:
            assert out_file.read_bytes() == data_file("image_decrypted.jpg").read_bytes()
        finally:
            out_file.unlink(missing_ok=True)

    async def test_download_file_obj_encrypted(self, monkeypatch, encrypted_file):
        async def test(*args, **kwargs):
            return data_file("image_encrypted.jpg").read_bytes()

        monkeypatch.setattr(encrypted_file.get_bot().request, "retrieve", test)
        with TemporaryFile() as custom_fobj:
            await encrypted_file.download_to_memory(out=custom_fobj)
            custom_fobj.seek(0)
            assert custom_fobj.read() == data_file("image_decrypted.jpg").read_bytes()

    async def test_download_file_obj_local_file_encrypted(self, monkeypatch, encrypted_local_file):
        async def test(*args, **kwargs):
            return data_file("image_encrypted.jpg").read_bytes()

        monkeypatch.setattr(encrypted_local_file.get_bot().request, "retrieve", test)
        with TemporaryFile() as custom_fobj:
            await encrypted_local_file.download_to_memory(out=custom_fobj)
            custom_fobj.seek(0)
            assert custom_fobj.read() == data_file("image_decrypted.jpg").read_bytes()

    async def test_download_bytearray_encrypted(self, monkeypatch, encrypted_file):
        async def test(*args, **kwargs):
            return data_file("image_encrypted.jpg").read_bytes()

        monkeypatch.setattr(encrypted_file.get_bot().request, "retrieve", test)

        # Check that a download to a newly allocated bytearray works.
        buf = await encrypted_file.download_as_bytearray()
        assert buf == bytearray(data_file("image_decrypted.jpg").read_bytes())

        # Check that a download to a given bytearray works (extends the bytearray).
        buf2 = buf[:]
        buf3 = await encrypted_file.download_as_bytearray(buf=buf2)
        assert buf3 is buf2
        assert buf2[len(buf) :] == buf
        assert buf2[: len(buf)] == buf


class TestFileWithRequest(TestFileBase):
    async def test_error_get_empty_file_id(self, bot):
        with pytest.raises(TelegramError):
            await bot.get_file(file_id="")

    async def test_download_local_file(self, local_file):
        assert await local_file.download_to_drive() == Path(local_file.file_path)
        # Ensure that the file contents didn't change
        assert Path(local_file.file_path).read_bytes() == self.file_content

    @pytest.mark.parametrize(
        "custom_path_type", [str, Path], ids=["str custom_path", "pathlib.Path custom_path"]
    )
    async def test_download_custom_path_local_file(self, local_file, custom_path_type):
        file_handle, custom_path = mkstemp()
        custom_path = Path(custom_path)
        try:
            out_file = await local_file.download_to_drive(custom_path_type(custom_path))
            assert out_file == custom_path
            assert out_file.read_bytes() == self.file_content
        finally:
            os.close(file_handle)
            custom_path.unlink(missing_ok=True)

    async def test_download_file_obj_local_file(self, local_file):
        with TemporaryFile() as custom_fobj:
            await local_file.download_to_memory(out=custom_fobj)
            custom_fobj.seek(0)
            assert custom_fobj.read() == self.file_content

    @pytest.mark.parametrize(
        "custom_path_type", [str, Path], ids=["str custom_path", "pathlib.Path custom_path"]
    )
    async def test_download_custom_path_local_file_encrypted(
        self, encrypted_local_file, custom_path_type
    ):
        file_handle, custom_path = mkstemp()
        custom_path = Path(custom_path)
        try:
            out_file = await encrypted_local_file.download_to_drive(custom_path_type(custom_path))
            assert out_file == custom_path
            assert out_file.read_bytes() == data_file("image_decrypted.jpg").read_bytes()
        finally:
            os.close(file_handle)
            custom_path.unlink(missing_ok=True)

    async def test_download_local_file_encrypted(self, encrypted_local_file):
        out_file = await encrypted_local_file.download_to_drive()
        try:
            assert out_file.read_bytes() == data_file("image_decrypted.jpg").read_bytes()
        finally:
            out_file.unlink(missing_ok=True)

    async def test_download_bytearray_local_file(self, local_file):
        # Check that a download to a newly allocated bytearray works.
        buf = await local_file.download_as_bytearray()
        assert buf == bytearray(self.file_content)

        # Check that a download to a given bytearray works (extends the bytearray).
        buf2 = buf[:]
        buf3 = await local_file.download_as_bytearray(buf=buf2)
        assert buf3 is buf2
        assert buf2[len(buf) :] == buf
        assert buf2[: len(buf)] == buf

    async def test_download_bytearray_local_file_encrypted(self, encrypted_local_file):
        # Check that a download to a newly allocated bytearray works.
        buf = await encrypted_local_file.download_as_bytearray()
        assert buf == bytearray(data_file("image_decrypted.jpg").read_bytes())

        # Check that a download to a given bytearray works (extends the bytearray).
        buf2 = buf[:]
        buf3 = await encrypted_local_file.download_as_bytearray(buf=buf2)
        assert buf3 is buf2
        assert buf2[len(buf) :] == buf
        assert buf2[: len(buf)] == buf
