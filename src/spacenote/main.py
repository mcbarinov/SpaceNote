import uvicorn

from spacenote.core.app import App
from spacenote.core.config import CoreConfig
from spacenote.web.config import WebConfig
from spacenote.web.server import create_fastapi_app


def main() -> None:
    core_config = CoreConfig()
    web_config = WebConfig()
    app = App(core_config)
    fastapi_app = create_fastapi_app(app, web_config)
    uvicorn.run(fastapi_app, host=web_config.host, port=web_config.port)


if __name__ == "__main__":
    main()
