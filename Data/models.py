import re
from collections import UserDict
from datetime import datetime


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)


class Birthday(Field):
    def __init__(self, value):
        try:
            value = datetime.strptime(value, '%d.%m.%Y').date()
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")


class Note:
    def __init__(self, title, text):
        self.title = title
        self.text = text

    def edit(self, new_text):
        self.text = new_text

    def __str__(self):
        return f"{self.title}: {self.text}"


class Email(Field):
    def __init__(self, value):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(pattern, value):
            raise ValueError("Invalid email format.")
        super().__init__(value)


class Address(Field):
    pass


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
        self.email = None
        self.address = None

    def add_phone(self, phone) -> None:
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phones):
        for p in self.phones:
            if p.value == old_phone:
                p.value = Phone(new_phones).value
                return
        raise ValueError("Phone not found")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def find_birthday(self):
        return self.birthday

    def add_email(self, email):
        self.email = Email(email)

    def add_address(self, address):
        self.address = Address(address)

    def __str__(self):
        birthday = self.birthday.value if self.birthday else "not added"
        email = self.email.value if self.email else "not added"
        address = self.address.value if self.address else "not added"
        phones = '; '.join(p.value for p in self.phones) if self.phones else "none"
        return (
            f"Contact name: {self.name.value}, "
            f"phones: {phones}, "
            f"birthday: {birthday}, "
            f"email: {email}, "
            f"address: {address}"
        )


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def upcoming_birthdays(self, days=7):
            """Return records with birthdays within the next `days` days (inclusive)."""
            today = datetime.today().date()
            birthdays = []
            for record in self.data.values():
                if record.birthday:
                    birthday = record.birthday.value
                    next_birthday = birthday.replace(
                        year=today.year
                        if birthday.replace(year=today.year) >= today
                        else today.year + 1
                    )
                    if (next_birthday - today).days <= days:
                        birthdays.append(record)
            return birthdays

    def search(self, query):
        query = query.lower()
        results = []
        for record in self.data.values():
            if query in record.name.value.lower():
                results.append(record)
                continue

            if any(query in p.value for p in record.phones):
                results.append(record)
                continue

            if record.email and query in record.email.value.lower():
                results.append(record)
                continue
            if record.address and query in record.address.value.lower():
                results.append(record)
                continue
        return results


class NoteBook(UserDict):
    def add_note(self, title, text):
        self.data[title] = Note(title, text)

    def find_note(self, query):
        query = query.lower()
        return [note for note in self.data.values()
                if query in note.title.lower() or query in note.text.lower()]

    def edit_note(self, title, new_text):
         if title not in self.data:
             raise KeyError
         self.data[title].edit(new_text)

    def delete_note(self, title):
        if title not in self.data:
            raise KeyError
        del self.data[title]

    def all_notes(self):
        return list(self.data.values())
