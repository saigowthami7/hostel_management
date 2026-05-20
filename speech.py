import tkinter as tk
import subprocess
import pymysql

class Speech:
    def __init__(self, root):
        self.root = root
        self.root.title("Text to Speech")

        scrn_width = self.root.winfo_screenwidth()
        scrn_height = self.root.winfo_screenheight()

        self.root.geometry(f"{scrn_width}x{scrn_height}+0+0")

        self.conn = pymysql.connect(
            host="localhost",
            user="root",
            password="#$aigow12345",
            database="tts_app"
        )

        self.cursor = self.conn.cursor()

        mainTitle = tk.Label(
            self.root,
            text="Text to Speech",
            bg="blue",
            fg="white",
            bd=5,
            relief="groove",
            font=("Arial", 40, "bold")
        )
        mainTitle.pack(side="top", fill="x")

        mainFrame = tk.Frame(self.root, bg="sky blue", bd=5, relief="ridge")
        mainFrame.place(x=400, y=90, width=450, height=550)

        textLabel = tk.Label(
            mainFrame,
            text="Enter your text:",
            bg="sky blue",
            font=("Arial", 20, "bold")
        )
        textLabel.grid(row=0, column=0, padx=20, pady=30)

        self.text = tk.Text(
            mainFrame,
            bd=3,
            width=35,
            height=5,
            relief="sunken",
            font=("Arial", 15)
        )
        self.text.grid(row=1, column=0, padx=20, pady=20)

        btn = tk.Button(
            mainFrame,
            bg="light gray",
            command=self.speech,
            width=20,
            text="Speech",
            font=("Arial", 20, "bold")
        )
        btn.grid(row=2, column=0, padx=20, pady=20)

    def speech(self):
        value = self.text.get('1.0', tk.END).strip()

        cmd = (
            f'PowerShell -Command '
            f'"Add-Type -AssemblyName System.Speech; '
            f'(New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak(\'{value}\');"'
        )

        subprocess.run(cmd, shell=True)

        query = "INSERT INTO speech_history(text_content) VALUES(%s)"
        self.cursor.execute(query, (value,))
        self.conn.commit()

        self.clear()

    def clear(self):
        self.text.delete('1.0', tk.END)


root = tk.Tk()
obj = Speech(root)
root.mainloop()