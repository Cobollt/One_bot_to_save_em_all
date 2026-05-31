from pathlib import Path
from difflib import get_close_matches
import pickle
from models import Record, AddressBook, NoteBook


# Colors
RED = "\033[91m"
GREEN = "\033[92m"
GRAY = "\033[90m"
BLUE = "\033[94m"
RESET = "\033[0m"


DATA_DIR = Path("SaveData")
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "addressbook.pkl"
NOTES_FILE = DATA_DIR / "notebook.pkl"


def save_data(book, filename=DATA_FILE):
    with open(filename, "wb") as file:
        pickle.dump(book, file)


def save_notes(notes, filename=NOTES_FILE):
    with open(filename, "wb") as file:
        pickle.dump(notes, file)


def load_data(filename=DATA_FILE):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return AddressBook()


def load_notes(filename=NOTES_FILE):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return NoteBook()


# ── Parser ───────────────────────────────────────────────────────────────────

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


# ── Help ─────────────────────────────────────────────────────────────────────

def show_help():
    return f"""
{GRAY}----------
Available commands:

add contact [name] [phone]                    - add contact or add phone to existing contact
add birthday [name] [DD.MM.YYYY]              - add birthday to contact
add email [name] [email]                      - add or update email
add address [name] [address]                  - add or update address
add note [title] [text] #tag                  - add general note
add contact-note [name] [title] [text] #tag   - add note to contact

change contact [name] [old_phone] [new_phone] - change contact phone
change email [name] [email]                   - change email
change address [name] [address]               - change address
change note [title] [new text]                - edit note

find contact [query]                          - search contacts
find note [query]                             - search notes
find tag [tag]                                - search general notes by tag
find contact-tag [tag]                        - search contact notes by tag

show all                                      - show all contacts
show phone [query]                            - show phones by search
show birthday [query]                         - show birthday by search
show birthdays [days]                         - upcoming birthdays
show notes                                    - show all general notes
show contact-notes [query]                    - show contact notes by search

delete contact [name]                         - delete contact
delete note [title]                           - delete note

close / exit                                  - save and exit
----------{RESET}
"""


def suggest_command(user_input, commands):
    parts = user_input.split()
    available = []
    for command, value in commands.items():
        if isinstance(value, dict):
            for keyword in value:
                available.append(f"{command} {keyword}")
        else:
            available.append(command)
    matches = get_close_matches(
        " ".join(parts[:2]).lower(),
        available,
        n=1,
        cutoff=0.4
    )
    if not matches:
        return None
    if len(parts) > 2:
        return f"{matches[0]} {' '.join(parts[2:])}"
    return matches[0]


def normalize_command(command, args):
    if command == "add":
        if len(args) >= 2 and args[1].isdigit():
            return command, ["contact"] + args
    if command in ("find", "search"):
        if len(args) >= 1:
            return "find", ["contact"] + args
    return command, args


# ── Decorator ────────────────────────────────────────────────────────────────

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            if "not enough values to unpack" in str(e):
                if func.__name__ == "add_contact":
                    return "Give me name and phone please."
                if func.__name__ == "change_contact":
                    return "Invalid Name."
                if func.__name__ == "add_birthday":
                    return "Give me name and birthday please."
                if func.__name__ == "add_email":
                    return "Give me name and email please."
                if func.__name__ == "add_address":
                    return "Give me name and address please."
            return str(e)
        except KeyError:
            if "note" in func.__name__:
                return "Note not found."
            return "No contact."
        except IndexError:
            return "Enter a name."
    return inner


# ── Command handlers ──────────────────────────────────────────────────────────

@input_error
def add_contact(args, book):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message


@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def add_email(args, book):
    name, email = args
    record = book.find(name)
    if record is None:
        return "No contact found."
    record.add_email(email)
    return "Email added/updated."


@input_error
def add_address(args, book):
    name, *address_parts = args
    address = " ".join(address_parts)
    record = book.find(name)
    if record is None:
        return "No contact found."
    record.add_address(address)
    return "Address added/updated"


@input_error
def add_note(args, notebook):
    title, *parts = args
    text, tags = split_text_and_tags(parts)
    notebook.add_note(title, text, tags)
    return "Note added."


@input_error
def add_contact_note(args, book):
    name, title, *parts = args
    record = book.find(name)
    if record is None:
        return "No contact."
    text, tags = split_text_and_tags(parts)
    record.add_note(title, text, tags)
    return "Contact note added."


@input_error
def change_contact(args, book):
    name, old_number, new_numbers = args
    record = book.find(name)
    if record is None:
        return "No contact."
    record.edit_phone(old_number, new_numbers)
    return "Contact changed."


@input_error
def edit_note(args, notebook):
    title, *text_parts = args
    new_text = " ".join(text_parts)
    notebook.edit_note(title, new_text)
    return "Note edited."


@input_error
def find_note(args, notebook):
    query = " ".join(args)
    notes = notebook.find_note(query)
    if not notes:
        return "No note found."
    return "\n".join(str(note) for note in notes)


@input_error
def find_note_tag(args, notebook):
    tag = args[0].lstrip("#")
    notes = notebook.find_by_tag(tag)
    if not notes:
        return "No notes found."
    return "\n".join(str(note) for note in notes)


@input_error
def search_contact_note_tag(args, book):
    tag = args[0].lstrip("#").lower()
    results = []
    for record in book.search(tag):
        for note in record.notes:
            if any(t.lower() == tag for t in note.tags):
                results.append(
                    f"{record.name.value} -> {note}"
                )
    if not results:
        return "No contact notes found."
    return "\n".join(results)


@input_error
def search_contact(args, book):
    query = " ".join(args)
    results = book.search(query)
    if not results:
        return "No matches found."
    return "\n".join(str(record) for record in results)


@input_error
def show_phones(args, book):
    query = " ".join(args)
    results = book.search(query)
    if not results:
        return "No contact."
    return "\n".join(
        f"{record.name.value}: {'; '.join(phone.value for phone in record.phones)}"
        for record in results
    )


@input_error
def show_all(book):
    if not book.data:
        return "Address book is empty."
    result = []
    for record in book.data.values():
        result.append(str(record))
    return "\n".join(result)


@input_error
def show_birthday(args, book):
    query = " ".join(args)
    results = book.search(query)
    if not results:
        return "No contact."
    output = []
    for record in results:
        birthday = (
            record.birthday.value
            if record.birthday
            else "Birthday not found."
        )
        output.append(f"{record.name.value}: {birthday}")
    return "\n".join(output)


@input_error
def show_contact_notes(args, book):
    query = " ".join(args)
    results = book.search(query)
    if not results:
        return "No contact."
    output = []
    for record in results:
        if record.notes:
            output.append(f"\n{record.name.value}:")
            output.extend(str(note) for note in record.notes)
    if not output:
        return "No notes found."
    return "\n".join(output)


@input_error
def show_all_notes(notebook):
    notes = notebook.all_notes()
    if not notes:
        return "Notebook is empty."
    return "\n".join(str(note) for note in notes)


@input_error
def birthdays(args, book):
    if args:
        try:
            days = int(args[0])
            if days < 1:
                return "Please enter a positive number of days."
        except ValueError:
            return "Invalid number of days. Usage: birthdays [days]"
    else:
        days = 7
    result = []
    for record in book.upcoming_birthdays(days=days):
        result.append(str(record))
    if not result:
        return f"No birthdays in the next {days} day(s)."
    return "\n".join(result)


@input_error
def delete_contact(args, book):
    name = args [0]
    if book.find(name):
        book.delete(name)
        return f"Contact {name} deleted."
    return "No contact found."


@input_error
def delete_note(args, notebook):
    title = args[0]
    notebook.delete_note(title)
    return "Note deleted."


def split_text_and_tags(parts):
    text_parts = []
    tags = []
    for part in parts:
        if part.startswith("#"):
            tags.append(part[1:])
        else:
            text_parts.append(part)
    return " ".join(text_parts), tags


def main():
    book = load_data()
    notebook = load_notes()
    commands = {
        "add": {
            "contact": lambda command_args: add_contact(command_args, book),
            "note": lambda command_args: add_note(command_args, notebook),
            "contact-note": lambda command_args: add_contact_note(command_args, book),
            "birthday": lambda command_args: add_birthday(command_args, book),
            "email": lambda command_args: add_email(command_args, book),
            "address": lambda command_args: add_address(command_args, book),
        },
        "change": {
            "contact": lambda command_args: change_contact(command_args, book),
            "email": lambda command_args: add_email(command_args, book),
            "address": lambda command_args: add_address(command_args, book),
            "note": lambda command_args: edit_note(command_args, notebook),
        },
        "find": {
            "contact": lambda command_args: search_contact(command_args, book),
            "note": lambda command_args: find_note(command_args, notebook),
            "tag": lambda command_args: find_note_tag(command_args, notebook),
            "contact-tag": lambda command_args: search_contact_note_tag(command_args, book),
        },
        "show": {
            "all": lambda command_args: show_all(book),
            "notes": lambda command_args: show_all_notes(notebook),
            "contact-notes": lambda command_args: show_contact_notes(command_args, book),
            "phone": lambda command_args: show_phones(command_args, book),
            "birthday": lambda command_args: show_birthday(command_args, book),
            "birthdays": lambda command_args: birthdays(command_args, book),
        },
        "delete": {
            "contact": lambda command_args: delete_contact(command_args, book),
            "note": lambda command_args: delete_note(command_args, notebook),
        },
    }
    print(f"\n{BLUE}Welcome to the assistant bot!{RESET}")
    while True:
        print(show_help())

        user_input = input("Enter a command: ")
        if not user_input.strip():
            print("Please enter a command.")
            continue
        command, *args = parse_input(user_input)
        command, args = normalize_command(command, args)
        if command in ["close", "exit"]:
            save_data(book)
            save_notes(notebook)
            print("Good bye!")
            break
        if command in commands:
            if isinstance(commands[command], dict):
                if not args:
                    print("Enter keyword.")
                    continue
                keyword, *data = args
                handler = commands[command].get(keyword)
                if handler:
                    print(handler(data))
                else:
                    suggestion = suggest_command(user_input, commands)
                    if suggestion:
                        print(f"Did you mean: {suggestion}?")
                    else:
                        print("Invalid command.")
        else:
            suggestion = suggest_command(user_input, commands)
            if suggestion:
                print(f"Did you mean: {suggestion}?")
            else:
                print("Invalid command.")

if __name__ == "__main__":
    main()