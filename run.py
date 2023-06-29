import webview

import modul_app
from modul_app.main import app
from settings import settings

if __name__ == '__main__':
    from waitress import serve
    #
    # serve(app, host=settings.HOST, port=settings.PORT)
    # Запуск в окне
    # webview.start(http_server="127.0.0.1", http_port=8080)
    # Запуск в режиме для разработчика
    app.run(host=settings.HOST, port=settings.PORT)
