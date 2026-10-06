# ============================================================
# PYTHON BASICS — For Java / JavaScript Developers
# ============================================================

print("===== 1. VARIABLES & DATA TYPES =====")

name = "Rahul"  # String
age = 25  # Integer
salary = 50000.50  # Float
is_active = True  # Boolean
address = None  # None

print(name)
print(age)
print(salary)
print(is_active)
print(type(name))
print(type(age))


# ============================================================
print("\n===== 2. TYPE CONVERSION =====")
# ============================================================

age_text = "30"

age = int(age_text)
print(age)
print(type(age))

salary_text = "45000.50"
salary = float(salary_text)

print(salary)


# ============================================================
print("\n===== 3. F-STRING =====")
# ============================================================

name = "Rahul"
age = 25

print(f"My name is {name} and I am {age} years old.")


# ============================================================
print("\n===== 4. LIST =====")
# ============================================================

students = ["Rahul", "Amit", "Priya"]

print(students)
print(students[0])

students.append("Neha")

print(students)

students.remove("Amit")

print(students)

print(f"Number of students: {len(students)}")


# ============================================================
print("\n===== 5. TUPLE =====")
# ============================================================

coordinates = (10, 20)

print(coordinates)
print(coordinates[0])

# Tuple is immutable
# coordinates[0] = 100   # This would give an error


# ============================================================
print("\n===== 6. SET =====")
# ============================================================

numbers = {10, 20, 30}

print(numbers)

numbers.add(40)

print(numbers)


# ============================================================
print("\n===== 7. DICTIONARY / MAP =====")
# ============================================================

student = {"name": "Rahul", "age": 25, "city": "Hyderabad"}

print(student)

print(student["name"])
print(student["age"])

student["course"] = "Python"

print(student)


# ============================================================
print("\n===== 8. IF / ELIF / ELSE =====")
# ============================================================

age = 25

if age >= 18:
    print("Adult")
elif age >= 13:
    print("Teenager")
else:
    print("Child")


# ============================================================
print("\n===== 9. FOR LOOP =====")
# ============================================================

students = ["Rahul", "Amit", "Priya"]

for student in students:
    print(student)


# ============================================================
print("\n===== 10. RANGE =====")
# ============================================================

for number in range(5):
    print(number)


# ============================================================
print("\n===== 11. WHILE LOOP =====")
# ============================================================

count = 1

while count <= 5:
    print(count)
    count += 1


# ============================================================
print("\n===== 12. FUNCTION =====")
# ============================================================


def add(a, b):
    return a + b


result = add(10, 20)

print(f"Result = {result}")


# ============================================================
print("\n===== 13. FUNCTION WITH MULTIPLE PARAMETERS =====")
# ============================================================


def calculate_salary(basic, bonus):
    total = basic + bonus
    return total


salary = calculate_salary(50000, 10000)

print(f"Total salary = {salary}")


# ============================================================
print("\n===== 14. DEFAULT PARAMETER =====")
# ============================================================


def greet(name="Guest"):
    print(f"Hello {name}")


greet("Rahul")
greet()


# ============================================================
print("\n===== 15. MULTIPLE RETURN VALUES =====")
# ============================================================


def get_student():
    name = "Rahul"
    age = 25
    city = "Hyderabad"

    return name, age, city


name, age, city = get_student()

print(f"Name : {name}")
print(f"Age  : {age}")
print(f"City : {city}")


# ============================================================
print("\n===== 16. MULTIPLE RETURN WITH CALCULATION =====")
# ============================================================


def calculate(a, b):
    addition = a + b
    subtraction = a - b
    multiplication = a * b

    return addition, subtraction, multiplication


add_result, sub_result, multiply_result = calculate(10, 5)

print(f"Addition       : {add_result}")
print(f"Subtraction    : {sub_result}")
print(f"Multiplication : {multiply_result}")


# ============================================================
print("\n===== END =====")
# ============================================================
