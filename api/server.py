# reference: https://github.com/Jscina/PyPass/blob/master/server.py
import threading
from dataclasses import dataclass, field
from typing import Self

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles


@dataclass
class Server:
    """Server class for the PyPass application"""

    server: FastAPI
    static_files: StaticFiles
    host: str = "0.0.0.0"
    port: int = 8000
    use_multiprocess_import: bool = False
    debug: bool = False
    __server_process: threading.Thread | None = field(init=False, default=None)

    @property
    def server_process(self) -> threading.Thread | None:
        assert self.__server_process is not None, "No server process found"
        return self.__server_process

    def __post_init__(self) -> None:
        self.server.mount("/static", self.static_files, name="static")

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.server_process.join()

    def __start_server(self) -> None:
        """Starts the uviorn server"""
        uvicorn.run(app=self.server, host=self.host, port=self.port)

    def __create_server_process(self) -> threading.Thread:
        thread = threading.Thread(
            target=self.__start_server
        )  # todo: not sure why Process is not working
        thread.daemon = True
        return thread

    def start_server(self) -> None:
        if self.__server_process is None:
            self.__server_process = self.__create_server_process()
        self.__server_process.start()


# For local testing in the browser
def main() -> None:
    app = FastAPI()
    static_files = StaticFiles(directory="app/static")

    with Server(app, static_files, host="127.0.0.1") as server:
        server.start_server()
        try:
            while True:
                continue
        except KeyboardInterrupt:
            server.stop_server()
            print("Server stopped.")


if __name__ == "__main__":
    main()
