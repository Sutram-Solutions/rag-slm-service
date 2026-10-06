# ============================================================
# PYTHON OOP & APPLICATION SYNTAX
# For Java / JavaScript Developers
# ============================================================


# ============================================================
print("\n===== 1. BASIC CLASS =====")
# ============================================================


class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def display(self):
        print(f"Name: {self.name}")
        print(f"Age : {self.age}")


# Create object
student1 = Student("Rahul", 25)

student1.display()


# ============================================================
print("\n===== 2. OBJECT PROPERTIES =====")
# ============================================================

student2 = Student("Priya", 22)

print(student2.name)
print(student2.age)

# Properties can be changed
student2.age = 23

print(student2.age)


# ============================================================
print("\n===== 3. METHODS WITH PARAMETERS =====")
# ============================================================


class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b


calculator = Calculator()

print(calculator.add(10, 20))
print(calculator.multiply(10, 20))


# ============================================================
print("\n===== 4. SELF =====")
# ============================================================


class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def display(self):
        print(f"{self.name} earns {self.salary}")


employee = Employee("Amit", 50000)

employee.display()


# ============================================================
print("\n===== 5. ONE CLASS USING ANOTHER CLASS =====")
# ============================================================


class Address:
    def __init__(self, city, state):
        self.city = city
        self.state = state

    def display(self):
        print(f"City : {self.city}")
        print(f"State: {self.state}")


class Student:
    def __init__(self, name, age, city, state):
        self.name = name
        self.age = age

        # Student HAS an Address
        self.address = Address(city, state)

    def display(self):
        print(f"Name: {self.name}")
        print(f"Age : {self.age}")

        self.address.display()


student = Student("Rahul", 25, "Hyderabad", "Telangana")

student.display()


# ============================================================
print("\n===== 6. INHERITANCE =====")
# ============================================================


class Person:
    def __init__(self, name):
        self.name = name

    def display(self):
        print(f"Name: {self.name}")


class Teacher(Person):
    def teach(self):
        print(f"{self.name} is teaching")


teacher = Teacher("Mr. Sharma")

teacher.display()
teacher.teach()


# ============================================================
print("\n===== 7. INHERITANCE WITH SUPER =====")
# ============================================================


class Person:
    def __init__(self, name):
        self.name = name

    def display(self):
        print(f"Name: {self.name}")


class Teacher(Person):
    def __init__(self, name, subject):
        # Call parent constructor
        super().__init__(name)

        self.subject = subject

    def teach(self):
        print(f"{self.name} teaches {self.subject}")


teacher = Teacher("Mr. Sharma", "Mathematics")

teacher.display()
teacher.teach()


# ============================================================
print("\n===== 8. METHOD OVERRIDING =====")
# ============================================================


class Animal:
    def speak(self):
        print("Animal makes a sound")


class Dog(Animal):
    def speak(self):
        print("Dog says Woof")


class Cat(Animal):
    def speak(self):
        print("Cat says Meow")


dog = Dog()
cat = Cat()

dog.speak()
cat.speak()


# ============================================================
print("\n===== 9. POLYMORPHISM =====")
# ============================================================

animals = [Dog(), Cat()]

for animal in animals:
    animal.speak()


# ============================================================
print("\n===== 10. CLASS VARIABLE =====")
# ============================================================


class Employee:
    company = "Sutram Solutions"

    def __init__(self, name):
        self.name = name


employee1 = Employee("Rahul")
employee2 = Employee("Priya")

print(employee1.name)
print(employee1.company)

print(employee2.name)
print(employee2.company)


# ============================================================
print("\n===== 11. CLASS METHOD =====")
# ============================================================


class Employee:
    company = "Sutram Solutions"

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_company(cls):
        return cls.company


print(Employee.get_company())


# ============================================================
print("\n===== 12. STATIC METHOD =====")
# ============================================================


class Calculator:
    @staticmethod
    def add(a, b):
        return a + b


print(Calculator.add(10, 20))


# ============================================================
print("\n===== 13. EXCEPTION HANDLING =====")
# ============================================================

try:
    number = int("ABC")

except ValueError:
    print("Invalid number")


# ============================================================
print("\n===== 14. TRY / EXCEPT / FINALLY =====")
# ============================================================

try:
    result = 10 / 0
    print(result)

except ZeroDivisionError:
    print("Cannot divide by zero")

finally:
    print("Execution completed")


# ============================================================
print("\n===== 15. EXCEPTION OBJECT =====")
# ============================================================

try:
    number = int("ABC")

except Exception as e:
    print(f"Error occurred: {e}")


# ============================================================
print("\n===== 16. WORKING WITH DICTIONARY / JSON-LIKE DATA =====")
# ============================================================

student = {"id": 101, "name": "Rahul", "age": 25, "subjects": ["Math", "Science", "English"]}

print(student["name"])

for subject in student["subjects"]:
    print(subject)


# ============================================================
print("\n===== 17. LIST OF OBJECTS =====")
# ============================================================


class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def display(self):
        print(f"{self.name} - {self.salary}")


employees = [Employee("Rahul", 50000), Employee("Amit", 60000), Employee("Priya", 70000)]

for employee in employees:
    employee.display()


# ============================================================
print("\n===== 18. LIST COMPREHENSION =====")
# ============================================================

salaries = [50000, 60000, 70000, 80000]

high_salaries = [salary for salary in salaries if salary >= 70000]

print(high_salaries)


# ============================================================
print("\n===== 19. LAMBDA =====")
# ============================================================

numbers = [1, 2, 3, 4, 5]

squared = list(map(lambda x: x * x, numbers))

print(squared)


# ============================================================
print("\n===== 20. COMPLETE EXAMPLE =====")
# ============================================================


class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def get_salary(self):
        return self.salary

    def display(self):
        print(f"Employee: {self.name}, " f"Salary: {self.salary}")


class Manager(Employee):
    def __init__(self, name, salary, team):
        super().__init__(name, salary)

        self.team = team

    def display_team(self):
        print(f"\nManager: {self.name}")

        print("Team:")

        for employee in self.team:
            print(f"- {employee.name}")


employee1 = Employee("Rahul", 50000)
employee2 = Employee("Amit", 60000)
employee3 = Employee("Priya", 70000)

team = [employee1, employee2, employee3]

manager = Manager("Rajesh", 100000, team)

manager.display()

manager.display_team()


# ============================================================
print("\n===== END =====")
# ============================================================
