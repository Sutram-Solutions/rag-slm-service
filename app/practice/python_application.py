# ============================================================
# PYTHON APPLICATION DEVELOPMENT
# For Java / Spring / React / Angular Developers
# ============================================================


# ============================================================
print("\n===== 1. IMPORTING A BUILT-IN MODULE =====")
# ============================================================

import math

number = 25

print(math.sqrt(number))
print(math.pi)


# ============================================================
print("\n===== 2. IMPORTING SPECIFIC FUNCTIONS =====")
# ============================================================

from datetime import datetime

current_time = datetime.now()

print(current_time)
print(current_time.year)
print(current_time.month)
print(current_time.day)


# ============================================================
print("\n===== 3. ALIAS =====")
# ============================================================

import datetime as dt

now = dt.datetime.now()

print(now)


# ============================================================
print("\n===== 4. WORKING WITH JSON =====")
# ============================================================

import json

student = {"id": 101, "name": "Rahul", "age": 25, "subjects": ["Math", "Science", "English"]}


# Python Dictionary -> JSON String

json_data = json.dumps(student)

print(json_data)


# JSON String -> Python Dictionary

python_object = json.loads(json_data)

print(python_object)
print(python_object["name"])


# ============================================================
print("\n===== 5. JSON FORMATTING =====")
# ============================================================

json_data = json.dumps(student, indent=4)

print(json_data)


# ============================================================
print("\n===== 6. WRITING TO A FILE =====")
# ============================================================

student_data = {"id": 101, "name": "Rahul", "age": 25}

with open("student.json", "w") as file:
    json.dump(student_data, file, indent=4)

print("File created successfully")


# ============================================================
print("\n===== 7. READING FROM A FILE =====")
# ============================================================

with open("student.json") as file:
    data = json.load(file)

print(data)
print(data["name"])


# ============================================================
print("\n===== 8. EXCEPTION HANDLING =====")
# ============================================================

try:
    with open("unknown.txt") as file:
        data = file.read()

except FileNotFoundError:
    print("File does not exist")


# ============================================================
print("\n===== 9. MULTIPLE EXCEPTIONS =====")
# ============================================================

try:
    number = int("ABC")

    result = 100 / number

except ValueError:
    print("Invalid number")

except ZeroDivisionError:
    print("Cannot divide by zero")

except Exception as e:
    print(f"Unexpected error: {e}")


# ============================================================
print("\n===== 10. CUSTOM EXCEPTION =====")
# ============================================================


class InvalidAgeExceptionError(Exception):
    pass


def validate_age(age):
    if age < 18:
        raise InvalidAgeExceptionError("Age must be 18 or above")

    return True


try:
    validate_age(15)

except InvalidAgeExceptionError as e:
    print(e)


# ============================================================
print("\n===== 11. FUNCTION RETURNING DICTIONARY =====")
# ============================================================


def get_student():
    return {"id": 101, "name": "Rahul", "age": 25}


student = get_student()

print(student)


# ============================================================
print("\n===== 12. FUNCTION ACCEPTING DICTIONARY =====")
# ============================================================


def display_student(student: dict[str, object]) -> None:
    print(f"ID   : {student['id']}")
    print(f"Name : {student['name']}")
    print(f"Age  : {student['age']}")


display_student(student)


# ============================================================
print("\n===== 13. *ARGS =====")
# ============================================================


def calculate_total(*numbers):
    total = 0

    for number in numbers:
        total += number

    return total


print(calculate_total(10, 20))
print(calculate_total(10, 20, 30))
print(calculate_total(10, 20, 30, 40))


# ============================================================
print("\n===== 14. **KWARGS =====")
# ============================================================


def create_student(**details):
    print(details)


create_student(name="Rahul", age=25, city="Hyderabad")


# ============================================================
print("\n===== 15. *ARGS + **KWARGS =====")
# ============================================================


def print_data(*args, **kwargs):
    print("Arguments:")
    print(args)

    print("Keyword Arguments:")
    print(kwargs)


print_data(10, 20, name="Rahul", city="Hyderabad")


# ============================================================
print("\n===== 16. TYPE HINTING =====")
# ============================================================


def add(a: int, b: int) -> int:
    return a + b


result = add(10, 20)

print(result)


# ============================================================
print("\n===== 17. TYPE HINTING WITH OBJECTS =====")
# ============================================================


class Student:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age


def display_student(student: Student) -> None:
    print(student.name)
    print(student.age)


student = Student("Rahul", 25)

display_student(student)


# ============================================================
print("\n===== 18. SIMPLE SERVICE CLASS =====")
# ============================================================


class StudentService:
    def get_student(self, student_id: int):
        return {"id": student_id, "name": "Rahul", "age": 25}

    def create_student(self, name: str, age: int):
        return {"name": name, "age": age}


service = StudentService()

student = service.get_student(101)

print(student)

new_student = service.create_student("Amit", 22)

print(new_student)


# ============================================================
print("\n===== 19. SIMPLE API CALL =====")
# ============================================================

import urllib.request

url = "https://jsonplaceholder.typicode.com/users/1"

try:
    response = urllib.request.urlopen(url)

    data = response.read()

    user = json.loads(data)

    print(user)

except Exception as e:
    print(f"API Error: {e}")


# ============================================================
print("\n===== 20. API RESPONSE AS PYTHON OBJECT =====")
# ============================================================

try:
    response = urllib.request.urlopen(url)

    data = response.read()

    user = json.loads(data)

    print(f"ID    : {user['id']}")
    print(f"Name  : {user['name']}")
    print(f"Email : {user['email']}")

except Exception as e:
    print(f"Error: {e}")


# ============================================================
print("\n===== END =====")
# ============================================================


import json
import urllib.request

url = "https://jsonplaceholder.typicode.com/users"

try:
    response = urllib.request.urlopen(url)

    data = response.read()

    users = json.loads(data)

    print(f"Total users: {len(users)}")

    for user in users:
        print(f"ID: {user['id']}, " f"Name: {user['name']}, " f"Email: {user['email']}")

except Exception as e:
    print(f"API Error: {e}")
