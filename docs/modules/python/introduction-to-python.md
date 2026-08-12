# Introduction to Python

This module introduces the Python vocabulary students need before writing games and robot-control code.

## Learning Goals

- Use variables to store values.
- Distinguish common data types such as integers, floats, booleans, strings, lists, tuples, and dictionaries.
- Run expressions in the Python interpreter.
- Understand that variables reference values in memory.
- Read simple `if`, `while`, and `for` structures.

## Suggested Flow

1. Open a terminal and run the Python interpreter with `python3`.
2. Try arithmetic and string expressions.
3. Assign values to variables and inspect them.
4. Use `type(...)` to compare values.
5. Move from the interpreter into a `.py` file in VS Code.

## Student Checks

Ask students to predict each result before running it:

```python
x = 10
y = 10.0
name = "robot"
ready = True

print(type(x))
print(type(y))
print(name + " arm")
print(not ready)
```

## Materials

- [Introduction to Python slides](../../assets/downloads/introduction-to-python.pptx)
- [Introduction to lab and course slides](../../assets/downloads/introduction-to-lab-and-course.pptx)

## Connection to Robotics

Robot programs use the same small building blocks as beginner games: values, choices, repetition, and named helper functions. The difference is that the output eventually becomes physical motion instead of text on the screen.
