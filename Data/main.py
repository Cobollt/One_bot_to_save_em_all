from pathlib import Path
import pickle
from .models import Record, AddressBook


DATA_DIR = Path("SaveData")
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "addressbook.pkl"


def save_data(book, filename=DATA_FILE):
    with open(filename, "wb") as file:
        pickle.dump(book, file)


def load_data(filename=DATA_FILE):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)
    except FileNotFoundError:
        return AddressBook()


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


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
            return "No contact."
        except IndexError:
            return "Enter a name."
    return inner


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
def change_contact(args, book):
    name, old_number, new_numbers = args
    record = book.find(name)
    if record is None:
        return "No contact."
    record.edit_phone(old_number, new_numbers)
    return "Contact changed."


@input_error
def show_phones(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "No contact."
    return "; ".join(phone.value for phone in record.phones)


@input_error
def show_all(book):
    if not book.data:
        return "Address book is empty."
    result = []
    for record in book.data.values():
        result.append(str(record))
    return "\n".join(result)


@input_error
def add_birthday(args, book):
    name, birthday, *_ = args
    record = book.find(name)
    record.add_birthday(birthday)
    return "Birthday added."


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    if record is None:
        return "No contact."
    if record.birthday is None:
        return "Birthday not found."
    return record.birthday.value


@input_error
def birthdays(book):
    result = []
    for record in book.upcoming_birthdays():
        result.append(str(record))
    return "\n".join(result)

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
def search_contact(args, book):
    if not args:
        return "Please provide a search query. "
    query = args[0]
    results = book.search(query)
    if not results:
        return "No matches found."
    return "\n---\n".join(str(record) for record in results)

@input_error
def delete_contact(args, book):
    name = args [0]
    if book.find(name):
        book.delete(name)
        return f"Contact {name} deleted."
    return "No contact found."


def main():
    book = load_data()
    commands = {
        "hello": lambda command_args: "How can I help you?",
        "add": lambda command_args: add_contact(command_args, book),
        "change": lambda command_args: change_contact(command_args, book),
        "phone": lambda command_args: show_phones(command_args, book),
        "all": lambda command_args: show_all(book),
        "add-birthday": lambda command_args: add_birthday(command_args, book),
        "show-birthday": lambda command_args: show_birthday(command_args, book),
        "birthdays": lambda command_args: birthdays(book),
        "add-email": lambda command_args: add_email(command_args, book),
        "change-email": lambda command_args: add_email(command_args, book),
        "change-address": lambda command_args: add_address(command_args, book),
        "add-address": lambda command_args: add_address(command_args, book),
        "search": lambda command_args: search_contact(command_args, book),
        "delete": lambda command_args: delete_contact(command_args, book),
    }
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        if not user_input.strip():
            print("Please enter a command.")
            continue
        command, *args = parse_input(user_input)
        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break
        handler = commands.get(command)
        if handler:
            print(handler(args))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()