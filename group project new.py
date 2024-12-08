import sqlite3
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime


# Database setup and helper functions
def initialize_database():
    conn = sqlite3.connect("diary.db")
    cursor = conn.cursor()
    # Create user_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY,
            name TEXT,
            password TEXT,
            security_question TEXT,
            security_answer TEXT
        )
    ''')
    # Create notes table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY,
            title TEXT,
            category TEXT,
            content TEXT,
            date TEXT
        )
    ''')
    conn.commit()
    conn.close()


def load_user_data():
    conn = sqlite3.connect("diary.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_data LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"name": row[1], "password": row[2], "security_question": row[3], "security_answer": row[4]}
    return {}


def save_user_data(user_data):
    conn = sqlite3.connect("diary.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_data")  # Clear existing user data
    cursor.execute(
        "INSERT INTO user_data (name, password, security_question, security_answer) VALUES (?, ?, ?, ?)",
        (user_data["name"], user_data["password"], user_data["security_question"], user_data["security_answer"])
    )
    conn.commit()
    conn.close()


def load_notes():
    conn = sqlite3.connect("diary.db")
    cursor = conn.cursor()
    cursor.execute("SELECT title, category, content, date FROM notes")
    notes = [{"title": row[0], "category": row[1], "content": row[2], "date": row[3]} for row in cursor.fetchall()]
    conn.close()
    return notes


def save_notes(notes):
    conn = sqlite3.connect("diary.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM notes")  # Clear existing notes
    for note in notes:
        cursor.execute(
            "INSERT INTO notes (title, category, content, date) VALUES (?, ?, ?, ?)",
            (note["title"], note["category"], note["content"], note["date"])
        )
    conn.commit()
    conn.close()


# Application logic
def authenticate(root, user_data, notes):
    if "name" in user_data and "password" in user_data:
        # Existing user - ask for password
        password_label = tk.Label(root, text="Enter your password:")
        password_entry = tk.Entry(root, show="*")
        password_button = tk.Button(root, text="Enter Password",
                                    command=lambda: check_password(root, password_entry.get(), user_data, notes))

        password_label.pack()
        password_entry.pack()
        password_button.pack()
    else:
        register_user(root, user_data, notes)


def check_password(root, password, user_data, notes):
    if password == user_data["password"]:
        clear_frame(root)
        show_main_menu(root, user_data, notes)
    else:
        messagebox.showerror("Error", "Incorrect password. Try again.")


def register_user(root, user_data, notes):
    name = simpledialog.askstring("Registration", "Enter your name:")
    password = simpledialog.askstring("Registration", "Enter a password:", show="*")
    re_password = simpledialog.askstring("Registration", "Confirm your password:", show="*")

    if password == re_password:
        security_question = simpledialog.askstring("Security", "Set a security question:")
        security_answer = simpledialog.askstring("Security", "Answer to security question:")

        user_data.update({
            "name": name.lower(),
            "password": password,
            "security_question": security_question,
            "security_answer": security_answer.lower()
        })
        save_user_data(user_data)
        clear_frame(root)
        show_main_menu(root, user_data, notes)
    else:
        messagebox.showerror("Error", "Passwords do not match.")


def show_main_menu(root, user_data, notes):
    welcome_label = tk.Label(root, text=f"Hello {user_data['name']}, how is your day?")
    welcome_label.pack(pady=10)

    tk.Button(root, text="Add Note", command=lambda: add_note(notes)).pack(pady=5)
    tk.Button(root, text="Search Note", command=lambda: search_note(notes)).pack(pady=5)
    tk.Button(root, text="Edit Note", command=lambda: edit_note(notes)).pack(pady=5)
    tk.Button(root, text="Delete Note", command=lambda: delete_note(notes)).pack(pady=5)
    tk.Button(root, text="Reset Password", command=lambda: reset_password(user_data)).pack(pady=5)
    tk.Button(root, text="Exit", command=root.quit).pack(pady=5)


def add_note(notes):
    title = simpledialog.askstring("Add Note", "Enter the title:")
    category = simpledialog.askstring("Add Note", "Enter the category:")
    content = simpledialog.askstring("Add Note", "Enter your thoughts:")
    date = datetime.now().strftime("%Y-%m-%d")

    if title and category and content:
        notes.append({"title": title.lower(), "category": category.lower(), "content": content, "date": date})
        save_notes(notes)
        messagebox.showinfo("Success", "Note added successfully!")


def search_note(notes):
    search_term = simpledialog.askstring("Search Note", "Enter title, category, or date (YYYY-MM-DD):")
    if search_term:
        found_notes = [note for note in notes if
                       search_term.lower() in [note["title"], note["category"], note["date"]]]

        if found_notes:
            results = "\n\n".join([
                f"Title: {note['title']}\nCategory: {note['category']}\nDate: {note['date']}\nContent: {note['content']}"
                for note in found_notes])
            messagebox.showinfo("Search Results", results)
        else:
            messagebox.showinfo("Search Results", "No notes found.")


def edit_note(notes):
    title = simpledialog.askstring("Edit Note", "Enter the title of the note to edit:")
    if title:
        for note in notes:
            if note["title"] == title.lower():
                new_content = simpledialog.askstring("Edit Note", "Edit your thoughts:", initialvalue=note["content"])
                if new_content:
                    note["content"] = new_content
                    save_notes(notes)
                    messagebox.showinfo("Success", "Note updated successfully!")
                    return
        messagebox.showerror("Error", "Note not found.")


def delete_note(notes):
    title = simpledialog.askstring("Delete Note", "Enter the title of the note to delete:")
    if title:
        for note in notes:
            if note["title"] == title.lower():
                notes.remove(note)
                save_notes(notes)
                messagebox.showinfo("Success", "Note deleted successfully!")
                return
        messagebox.showerror("Error", "Note not found.")


def reset_password(user_data):
    answer = simpledialog.askstring("Reset Password", user_data["security_question"])
    if answer and answer.lower() == user_data["security_answer"]:
        new_password = simpledialog.askstring("Reset Password", "Enter a new password:", show="*")
        if new_password:
            user_data["password"] = new_password
            save_user_data(user_data)
            messagebox.showinfo("Success", "Password reset successfully!")
    else:
        messagebox.showerror("Error", "Incorrect answer. Password reset failed.")


def clear_frame(root):
    for widget in root.winfo_children():
        widget.destroy()


# Run the application
def main():
    initialize_database()
    root = tk.Tk()
    root.title("DONA - Personal Diary")
    root.geometry("400x300")

    user_data = load_user_data()
    notes = load_notes()

    authenticate(root, user_data, notes)

    root.mainloop()


if __name__ == "__main__":
    main()
