import tkinter as tk
from tkinter import scrolledtext
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key="use your own api key")

# Create a model
model = genai.GenerativeModel("gemini-2.5-flash")

class SmartChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Chatbot")

        # Chat display
        self.chat_window = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, width=55, height=20, state='disabled'
        )
        self.chat_window.pack(padx=10, pady=10)

        # Entry + button frame
        bottom = tk.Frame(root)
        bottom.pack(fill=tk.X, padx=10, pady=5)

        self.entry = tk.Entry(bottom, font=("Arial", 12))
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.entry.bind("<Return>", self.send_message)

        tk.Button(bottom, text="Send", command=self.send_message).pack(side=tk.LEFT)

        # Keep conversation history
        self.chat_history = []

    def send_message(self, event=None):
        user_text = self.entry.get().strip()
        if not user_text:
            return

        self.display(f"You: {user_text}")
        self.entry.delete(0, tk.END)

        # Get AI response
        reply = self.ask_gemini(user_text)
        self.display(f"Bot: {reply}")

    def ask_gemini(self, user_input):
        try:
            # Add to conversation
            self.chat_history.append({"role": "user", "parts": user_input})

            # Send to Gemini
            response = model.generate_content(self.chat_history)
            bot_reply = response.text

            # Save bot reply to history
            self.chat_history.append({"role": "model", "parts": bot_reply})

            return bot_reply

        except Exception as e:
            return f"Error: {e}"

    def display(self, text):
        self.chat_window.config(state='normal')
        self.chat_window.insert(tk.END, text + "\n")
        self.chat_window.config(state='disabled')
        self.chat_window.see(tk.END)

# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    SmartChatApp(root)
    root.mainloop()
