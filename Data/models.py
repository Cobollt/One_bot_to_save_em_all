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


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

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

    def __str__(self):
        birthday = self.birthday.value if self.birthday else "not added"
        return (
            f"Contact name: {self.name.value}, "
            f"phones: {'; '.join(p.value for p in self.phones)}, "
            f"birthday: {birthday}")


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def upcoming_birthdays(self):
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
                if (next_birthday - today).days <= 7:
                    birthdays.append(record)
        return birthdays