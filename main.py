import logging
from gui import AudiobookSyncApp

if __name__ == "__main__":
    logging.basicConfig(filename='audiobook_sync.log', level=logging.ERROR, format='%(asctime)s %(levelname)s:%(message)s')
    app = AudiobookSyncApp()
    app.run()
