import os
from pathlib import Path

from webdav3.client import Client as Client_


class Client(Client_):
    """Modified `webdav3.Client` class to include additional methods."""

    def mkdir_recursive(self, remote_path: str) -> None:
        """
        Recursive version of `mkdir()` method, equivalent to `mkdir -p ...` on Unix.

        The WebDAV standard forbids the `MKCOL` (`mkdir`) method from creating intermediate directories when creating
        remote path. This method works around this limitation by splitting a remote path into a list of paths and
        creating each in turn.

        E.g. for a path 'foo/bar/baz', this method will create directories for:
        - 'foo'
        - 'foo/bar'
        - 'foo/bar/baz'

        Note: This method assumes the remote_path is to a file not a directory. The end element of the path, which is
        assumed to be a file name, is therefore skipped.

        E.g. for a path `foo/bar/baz.txt`, only the `foo` and `foo/bar` elements will be considered.

        Internally this method calls the standard `webdav3.mkdir()` method.
        """
        remote_path_ = ""
        for path in remote_path.split("/")[:-1]:
            if path == "":
                continue

            remote_path_ = f"{remote_path_}/{path}"
            webdav_client.mkdir(remote_path=remote_path_)

base_path = "/remote.php/dav/files"
endpoint = f"{base_path}/{os.environ['OC_USERNAME']}"
source_path = Path(os.environ['SRC_PATH'])
target_path = (
    f"{os.environ['TARGET_PATH']}/{source_path.name}"
)

webdav_client = Client(
    options={
        "webdav_hostname": os.environ['OC_HOSTNAME'],
        "webdav_login": os.environ['OC_USERNAME'],
        "webdav_password": os.environ['OC_PASSWORD'],
        "webdav_root": endpoint,
    }
)

print(f"Uploading '{source_path.name}' to '{'/'.join(target_path.split('/')[:-1])}/'")
webdav_client.mkdir_recursive(remote_path=target_path)
webdav_client.upload_file(local_path=source_path, remote_path=target_path)
