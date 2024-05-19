from collections import UserDict
from datetime import datetime, timedelta
from typing import List, Dict
import re
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
class Birthday(Field):
    def __init__(self, value):
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(value)  

class Name(Field):
    def __init__(self, value):
         super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not re.match(r'^\d{10}$', value):
            raise ValueError("Phone number must be 10 digits")
        super().__init__(value)

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        if not re.match(r'^\d{10}$', phone):
            raise ValueError("Invalid phone number format. Use 10 digits.")
        self.phones.append(Phone(phone))
        
    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if str(p) != phone]
    
    def edit_phone(self, old_phone, new_phone):
        self.remove_phone(old_phone)
        self.add_phone(new_phone)
        
    def find_phone(self, phone):
        for p in self.phones:
            if str(p) == phone:
                return p
        return None
    
    def add_birthday(self, birthday):
        try:
            datetime.strptime(birthday, "%d.%m.%Y")
            self.birthday = Birthday(birthday)
        except ValueError:
            raise ValueError("Invalid birthday format. Use DD.MM.YYYY.")

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record
        
    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name] 
        
    def get_upcoming_birthdays(self) -> List[Dict[str, str]]:
        today = datetime.today().date()
        upcoming_birthdays=[]
        for record in self.data.values():
            if not record.birthday:
                continue
            birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            birthday_this_year = birthday_date.replace(year=today.year)
            
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year+1)
                   
            if birthday_this_year.weekday() == 5:
                birthday_this_year += timedelta(days = 2)
            if birthday_this_year.weekday() == 6:
                birthday_this_year += timedelta(days = 1)
                
            days_to_birthday = (birthday_this_year - today).days
            
            if days_to_birthday <=7:
                upcoming_birthdays.append({
                    "name" : record.name.value,
                    "congratulation_date" : birthday_this_year.strftime("%d.%m.%Y") 
                })
        return upcoming_birthdays	
    
def input_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "KeyError. No such name."
        except ValueError:
            return "ValueError. Enter the argument for the command."
        except IndexError:
            return "IndexError. Not enough arguments."

    return wrapper

@input_error
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

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
    name, old_phone, new_phone = args
    record = book.find(name)
    if record is None:
        return "Contact not found."
    try:
        record.edit_phone(old_phone, new_phone)
        return "Contact changed."
    except ValueError as e:
        return str(e)

@input_error
def print_contact(args, book):
    name, *_ = args
    record = book.find(name)
    if record is not None:
        phones = '; '.join([str(phone) for phone in record.phones])
        print(f'Contact name: {record.name.value}, phones: {phones}')
        return "Contact printed."
    else:
        return "Contact not found."

@input_error
def print_contacts(book):
    for record in book.data.values():
        phones = '; '.join([str(phone) for phone in record.phones])
        print(f'Contact name: {record.name.value}, phones: {phones}')
    return "All contacts printed."

def print_contacts(contacts):
    for key, value in contacts.items():
        print(f'{key}: {value}')
    return "All contacts printed."
    
@input_error
def add_birthday(args, book):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for {name}"
    return f"Contact {name} not found"

@input_error
def show_birthday(args, book):
    name, *_ = args
    record = book.find(name)
    if record and record.birthday:
        return f"{name}'s birthday is {record.birthday.value}"
    return f"No birthday found for {name}"

@input_error
def birthdays(book):
    return book.get_upcoming_birthdays()

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Повернення нової адресної книги, якщо файл не знайдено

def main():
    book = load_data()
    print("Welcome to the assistant bot!\nBook loaded!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Book saved. Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(print_contact(args, book)) 

        elif command == "all":
            print(print_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args,book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        else:
            print("Invalid command.")

if __name__ == "__main__":
    main()