import tkinter as tk
from tkinter import ttk, font
from PIL import ImageGrab, ImageTk, Image
import pyautogui
import pyperclip
from anthropic import Anthropic
import os
from dotenv import load_dotenv
import base64
from io import BytesIO

class ScreenshotApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.attributes('-alpha', 0.0)  # Make the main window invisible
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-topmost', True)

        # Load environment variables
        load_dotenv()
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')

        # Store screen dimensions at initialization
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        # Take screenshot
        self.screenshot = ImageGrab.grab()
        
        # Create darkened version of the screenshot
        self.darkened = self.screenshot.copy()
        # Make it 50% darker
        self.darkened = Image.blend(self.darkened, Image.new('RGB', self.darkened.size, 'black'), 0.5)
        self.photo = ImageTk.PhotoImage(self.darkened)

        # Create canvas
        self.canvas = tk.Canvas(
            self.root,
            width=self.screenshot.width,
            height=self.screenshot.height,
            highlightthickness=0
        )
        self.canvas.pack()
        self.canvas.create_image(0, 0, image=self.photo, anchor='nw')

        # Variables for rectangle drawing
        self.start_x = None
        self.start_y = None
        self.selection = None
        self.selection_coords = None
        self.bright_region = None

        # Bind events
        self.canvas.bind('<Button-1>', self.start_rect)
        self.canvas.bind('<B1-Motion>', self.draw_rect)
        self.canvas.bind('<ButtonRelease-1>', self.end_rect)
        self.root.bind('<Escape>', lambda e: self.root.destroy())

        self.root.after(100, lambda: self.root.attributes('-alpha', 1.0))
        
    def start_rect(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.bright_region:
            self.canvas.delete(self.bright_region)

    def draw_rect(self, event):
        if self.bright_region:
            self.canvas.delete(self.bright_region)
            
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)
        
        # Create bright region
        region = self.screenshot.crop((x1, y1, x2, y2))
        bright_photo = ImageTk.PhotoImage(region)
        self.bright_region = self.canvas.create_image(x1, y1, image=bright_photo, anchor='nw')
        self.canvas.bright_photo = bright_photo  # Keep a reference

    def end_rect(self, event):
        if self.start_x and self.start_y:
            x1 = min(self.start_x, event.x)
            y1 = min(self.start_y, event.y)
            x2 = max(self.start_x, event.x)
            y2 = max(self.start_y, event.y)
            
            # Store selection coordinates for window positioning
            self.selection_coords = (x1, y1, x2, y2)
            
            # Capture the selected region
            self.selection = self.screenshot.crop((x1, y1, x2, y2))
            self.root.destroy()

    def show_result(self, text):
        result_window = tk.Tk()
        result_window.title("Screenshot Question Answerer")
        result_window.geometry("600x400")

        # Position the window next to the selection
        if self.selection_coords:
            x2, y1, _, y2 = self.selection_coords
            
            # Calculate window position
            window_x = min(x2 + 10, self.screen_width - 610)  # Keep window visible
            window_y = max(y1, 0)  # Ensure window stays on screen
            
            # Center vertically relative to selection
            selection_height = y2 - y1
            window_y = y1 + (selection_height // 2) - 200
            
            # Ensure window is fully visible
            if window_y + 400 > self.screen_height:
                window_y = self.screen_height - 410
            if window_y < 0:
                window_y = 0
                
            result_window.geometry(f"600x400+{window_x}+{window_y}")

        text_widget = tk.Text(result_window, wrap=tk.WORD, padx=10, pady=10)
        # Configure a larger font size
        default_font = tk.font.nametofont("TkTextFont")
        text_widget.configure(font=(default_font.actual()["family"], default_font.actual()["size"] * 2))
        text_widget.insert(tk.END, text)
        text_widget.pack(expand=True, fill='both')

        # Copy to clipboard
        pyperclip.copy(text)

        result_window.mainloop()

    def run(self):
        self.root.mainloop()

        if self.selection:
            # Convert image to base64
            buffered = BytesIO()
            self.selection.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()

            # Initialize Anthropic client
            client = Anthropic(api_key=self.anthropic_api_key)

            # Send to Claude
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Rephrase the question in the image and options if given. Answer the question two lines below behind 'Answer:'. Keep your answer concise and to the point. Do not mention the image."
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": img_str
                            }
                        }
                    ]
                }]
            )

            # Show result
            self.show_result(message.content[0].text)

if __name__ == "__main__":
    app = ScreenshotApp()
    app.run() 