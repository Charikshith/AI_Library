
# Structural Typing (Duck Typing) vs ABC (Nominal Typing) in Python

## Structural Typing (Duck Typing)

- **Definition:**  
  Structural typing means an object is considered suitable if it has the required methods and properties, regardless of its actual class or inheritance.
- **Famous saying:**  
  “If it looks like a duck and quacks like a duck, it’s a duck.”

### Example

```python
class Duck:
    def quack(self):
        print("Quack!")

class Person:
    def quack(self):
        print("I'm pretending to be a duck!")

def make_it_quack(thing):
    thing.quack()  # Works as long as 'thing' has a 'quack' method

make_it_quack(Duck())    # Output: Quack!
make_it_quack(Person())  # Output: I'm pretending to be a duck!
```

- **Key Point:**  
  No inheritance is required. Any object with a `quack` method will work.

---

## ABC (Abstract Base Class) - Nominal Typing

- **Definition:**  
  Nominal typing means an object is considered suitable only if it explicitly inherits from a specific base class (the "name" of the type matters).
- **Enforced by:**  
  Using `abc.ABC` and `@abstractmethod` decorators.

### Example

```python
from abc import ABC, abstractmethod

class Quacker(ABC):
    @abstractmethod
    def quack(self):
        pass

class Duck(Quacker):
    def quack(self):
        print("Quack!")

class Person:
    def quack(self):
        print("I'm pretending to be a duck!")

def make_it_quack(thing: Quacker):
    thing.quack()

make_it_quack(Duck())    # Output: Quack!
make_it_quack(Person())  # Type checker will warn/error; not a Quacker
```

- **Key Point:**  
  Only objects that inherit from `Quacker` are accepted, even if others have the right method.

---

## Summary Table

| Feature                | Structural Typing (Duck Typing) | ABC (Nominal Typing)      |
|------------------------|----------------------------------|---------------------------|
| Inheritance required?  | No                               | Yes                       |
| Type checked by        | Methods/attributes present       | Explicit base class       |
| Flexibility            | High                             | Lower                     |
| Example use            | Protocols, dynamic code          | Strict interfaces, APIs   |

---

## When to Use Each

- **Structural Typing:**  
  Use when you want flexibility and care only about whether the object has the right methods.

- **ABC (Nominal Typing):**  
  Use when you want strict type hierarchies and runtime enforcement of interfaces.

# Understanding `@staticmethod` and `@classmethod` in Python

Both `@staticmethod` and `@classmethod` are decorators in Python. Decorators modify the behavior of a function or method. In this case, they change how methods within a class relate to the class itself and its instances.

**1. `@staticmethod`**

*   **How:** Place `@staticmethod` directly above a method definition within a class.

    ```python
    class MyClass:
        @staticmethod
        def my_static_method(arg1, arg2):
            # Method body
            return result
    ```

*   **What it Does:**

    *   Turns a method into a static method. A static method is bound to the class but does *not* receive the class instance (`self`) or the class itself (`cls`) as an implicit first argument.
    *   It behaves like a regular function that happens to be defined within the class's namespace.

*   **When to Use:**

    *   When you have a method that logically belongs to the class (it's conceptually related to the class), but it doesn't need to access or modify any instance-specific data (attributes).
    *   When the method doesn't depend on the state of the class or its instances. It's just a utility function that's grouped with the class for organization.

*   **Where to Use:** Inside a class definition.

*   **Why Use:**

    *   **Organization/Namespace:** Keeps related functionality grouped together within the class, improving code readability.
    *   **Encapsulation:** The method is logically part of the class's interface, even if it doesn't operate on instance data.
    *   **Avoid Unnecessary `self` or `cls`:** Prevents the method from receiving the implicit `self` or `cls` argument, which would be unused and potentially confusing.

**Example:**

```python
class MathUtils:
    @staticmethod
    def add(x, y):
        return x + y

    @staticmethod
    def multiply(x, y):
        return x * y

# Calling the static methods:
result1 = MathUtils.add(5, 3)  # No instance required
result2 = MathUtils.multiply(2, 4)
print(result1, result2)  # Output: 8 8
```

In this example, `add` and `multiply` are utility functions that perform mathematical operations. They don't need to know anything about an instance of `MathUtils`. Therefore, they are perfect candidates for static methods.

**2. `@classmethod`**

*   **How:** Place `@classmethod` directly above a method definition within a class.

    ```python
    class MyClass:
        @classmethod
        def my_class_method(cls, arg1, arg2):
            # Method body
            return result
    ```

*   **What it Does:**

    *   Transforms a method into a class method. A class method *does* receive the class itself (`cls`) as the implicit first argument. This allows the method to access and modify class-level attributes, create instances of the class, or call other class methods.
    *   `cls` is conventionally used as the name for the class object, similar to how `self` is used for the instance object.

*   **When to Use:**

    *   When you want a method to operate on the class itself (e.g., to create new instances of the class, modify class-level variables, or provide alternative constructors).
    *   When the method needs to access or modify class attributes.
    *   When you need a method that can be inherited and behave differently in subclasses (polymorphism).

*   **Where to Use:** Inside a class definition.

*   **Why Use:**

    *   **Alternative Constructors:** Provides a way to create instances of the class with different initialization logic than the standard `__init__` method. This is often done using factory methods.
    *   **Access Class-Level Data:** Allows the method to interact with and modify class attributes (variables that belong to the class itself, not to individual instances).
    *   **Polymorphism/Inheritance:** Class methods can be overridden in subclasses, and they will automatically receive the subclass as the `cls` argument. This is useful for creating flexible and extensible class hierarchies.

**Example:**

```python
class Employee:
    num_employees = 0

    def __init__(self, name, salary):
        self.name = name
        self.salary = salary
        Employee.num_employees += 1  # Update class variable

    @classmethod
    def from_string(cls, employee_string):
        name, salary = employee_string.split('-')
        return cls(name, float(salary))  # Create a new instance of the class

    @classmethod
    def get_employee_count(cls):
        return cls.num_employees

# Using the class methods:
emp1 = Employee("Alice", 50000)
emp2 = Employee.from_string("Bob-60000")  # Alternative constructor
print(emp2.name, emp2.salary) #Output: Bob 60000.0

print(Employee.get_employee_count())  # Accessing class-level data, Output: 2
```

In this example:

*   `from_string` is a class method that acts as an alternative constructor. It creates a new `Employee` object from a string format. It uses `cls` to call the class's constructor (`cls(name, float(salary))`).
*   `get_employee_count` is a class method that returns the total number of employees. It accesses the class variable `num_employees` using `cls.num_employees`.

**Key Differences Summarized:**

| Feature          | `@staticmethod`                           | `@classmethod`                            |
| ---------------- | ----------------------------------------- | ------------------------------------------ |
| Implicit Argument | None                                      | Class (`cls`)                             |
| Purpose          | Utility function related to the class       | Operations on the class itself            |
| Access           | No access to class or instance attributes | Access to class attributes, can create instances|
| Use Cases        | Helper functions, logical grouping        | Alternative constructors, factory methods, class-level data |

**When to Choose Which:**

*   **Does the method need to know anything about the class or its instances?** If no, use `@staticmethod`.
*   **Does the method need to create instances of the class, modify class attributes, or be polymorphic in subclasses?** If yes, use `@classmethod`.
*   **Does the method need to access instance-specific data (attributes of `self`)?** If yes, use a regular instance method (no decorator).

In the original `ScheduleContextGenerator` example, both methods `get_current_activity` and `get_schedule_for_day` are decorated as class methods because they access the `SCHEDULES` dictionary, which is a class-level attribute. They don't need to operate on specific instances of the class, but they do need to access the class's schedule data. `_parse_time_range` is decorated as static method because it doesnt operate on any class or instance attributes.

By understanding these distinctions, you can effectively use `@staticmethod` and `@classmethod` to create well-organized, maintainable, and flexible code in your Python classes.

