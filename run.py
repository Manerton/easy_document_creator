import webview

import modul_app
from modul_app.main import app

if __name__ == '__main__':
    # webview.start(http_server="127.0.0.1", http_port=8080)
    app.run(host="127.0.0.1", port=8080)
