# Audiobook Sync

## Setup

1. Create a virtual environment:
   ```sh
   python -m venv venv
   
2. Activate the virtual environment:

    On Windows:
    ```sh
    .\venv\Scripts\activate
    ```
    
    On macOS/Linux:
    ```sh
    source venv/bin/activate
    ```

3. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up Google Cloud Speech-to-Text:

   * Follow the Google Cloud Speech-to-Text Quickstart Guide to enable the API and set up authentication.


5. Run the application:
    ```sh
   python main.py
    ```
   

Usage
   ```sh
   Click "Load eBook" to select and load an ePub file.
   Click "Load Audiobook" to select and load an audiobook file (MP3 or WAV).
   The application will display the text of the eBook and prepare for synchronization.
   ```
