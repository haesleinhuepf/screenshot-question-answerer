# Screenshot Question Answerer

A tool that lets you capture an image of a question and get an answer using Anthropic's large language model (LLM) [Claude](https://claude.ai).
It is available as a standalone **browser app** (`index.html`) as well as a **Python desktop app** (`screenshot_question_answerer.py`).

## Note

This is a research tool for exploring LLM-assisted user interfaces. The screenshots you take using this tool will be sent to the AI Service provider remotely and processed there. Make sure to not submit screenshots of private, personal or secret data.

![](https://github.com/haesleinhuepf/screenshot-question-answerer/blob/main/docs/demo.gif?raw=true)

## Browser App (HTML/JS)

`index.html` is a **fully standalone** browser app — no installation, no server required.

### Usage

1. Open `index.html` in any modern browser (Chrome, Firefox, Safari, Edge).  
   On a smartphone, host it on any static HTTPS web server (see note below) and open the URL.
2. Enter your [Anthropic API key](https://console.anthropic.com/) in the dialog that appears on launch.
3. Allow camera access when the browser asks.
4. Point the camera at a question and tap **Answer!**.
5. The answer is displayed full-screen. Tap **OK** to return to the camera view.

> **HTTPS required on mobile:** Most mobile browsers (Chrome on Android, Safari on iOS) only allow camera access from pages served over **HTTPS** or `localhost`. Opening `index.html` as a local file (`file://`) or over plain HTTP will result in a "Permission denied" error. A quick way to serve the file with HTTPS is to use a tool like [ngrok](https://ngrok.com/) or deploy it to any free static hosting service (e.g. GitHub Pages, Netlify).

> **Privacy note:** Your API key is kept only in memory for the current browser session and is sent exclusively to `api.anthropic.com`.

---

## Python Desktop App

### Installation

1. Create a new conda environment:
```bash
conda create -n screenshot-question-answerer python=3.10
conda activate screenshot-question-answerer
```

2. Install the required packages:
```bash
pip install pillow pyautogui pyperclip anthropic python-dotenv
```

### Configuration

1. Create a `.env` file in the same directory as the script with your Anthropic API key:
```
ANTHROPIC_API_KEY=your_api_key_here
```

2. Replace `your_api_key_here` with your actual Anthropic API key. You can get one from [Anthropic's Console](https://console.anthropic.com/).

### Usage

1. Run the script:
```bash
python screenshot_analyzer.py
```

2. The screen will darken slightly
3. Click and drag to select the region containing your question
4. Release to capture and analyze
5. Results will appear in a window and be copied to your clipboard
6. Press ESC at any time to cancel

## Setting Up a Windows Keyboard Shortcut

* Create a new Windows shortcut in the folder "%AppData%\Microsoft\Windows\Start Menu\Programs".
* Enter the target "powershell.exe -WindowStyle Hidden -Command "C:\path\to\run_analyzer.bat""
* Enter the location where the .py file is located ("C:\path\to\").
* Enter the desired shortcut, e.g. Ctrl + Alt + A
* Click "OK"

![](docs/config_screenshot.png))

Now you can use your keyboard shortcut from anywhere to launch the screenshot analyzer!

## License

This project is open source and available under the BSD-3 License. 

## Acknowledgements

The code was written mostly using [cursor](https://cursor.dev/). Hence, @haesleinhuepf is only partially responsible for the code quality ;-)
