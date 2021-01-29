from typing import Tuple

from .request import PtbRequestBase
from .types import JSONDict


class PtbHttpx(PtbRequestBase):
async def do_request(self, method: str, url: str, data: JSONDict, is_files: bool,
                     read_timeout: float = None) -> Tuple[int, bytes]:
    pass
