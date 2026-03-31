import json
import random

subjects = {
    "python": [
        ("What is Python used for?", "Python is used for web development, AI, automation, and data science."),
        ("Explain list in Python", "A list is a mutable collection that stores multiple items in order."),
        ("What is a dictionary in Python?", "A dictionary stores key-value pairs."),
        ("What is lambda function?", "A lambda is an anonymous function defined using lambda keyword."),
        ("What is PEP 8?", "PEP 8 is the style guide for writing Python code.")
    ],

    "java": [
        ("What is JVM?", "JVM is Java Virtual Machine that runs Java bytecode."),
        ("Explain OOP in Java", "OOP includes encapsulation, inheritance, polymorphism, abstraction."),
        ("What is method overloading?", "Multiple methods with same name but different parameters."),
        ("What is JDK?", "JDK is Java Development Kit used for developing Java applications."),
        ("Difference between JDK and JRE?", "JDK is for development, JRE is for running programs.")
    ],

    "data structures": [
        ("What is stack?", "Stack follows LIFO principle."),
        ("What is queue?", "Queue follows FIFO principle."),
        ("Difference between array and linked list?", "Array is fixed size, linked list is dynamic."),
        ("What is binary tree?", "Tree where each node has at most two children."),
        ("What is hash table?", "Structure that maps keys to values using hash function.")
    ],

    "placement": [
        ("What is campus placement?", "It is a hiring process conducted in colleges."),
        ("How to prepare for placement?", "Practice coding, aptitude, and communication skills."),
        ("What are aptitude tests?", "Tests that measure logical and numerical ability."),
        ("What is group discussion?", "Discussion to evaluate communication and leadership."),
        ("What is technical round?", "Interview focusing on technical knowledge.")
    ],

    "hr": [
        ("Tell me about yourself", "I am a motivated individual with strong technical skills."),
        ("Why should we hire you?", "I am hardworking and ready to learn."),
        ("What are your strengths?", "Problem-solving and quick learning."),
        ("What are your weaknesses?", "I focus too much on perfection sometimes."),
        ("Where do you see yourself in 5 years?", "In a challenging role growing professionally.")
    ],

    "coding": [
        ("What is recursion?", "Function calling itself to solve a problem."),
        ("What is time complexity?", "It measures algorithm efficiency."),
        ("What is space complexity?", "Memory used by an algorithm."),
        ("Explain binary search", "Search in sorted array with O(log n)."),
        ("What is sorting?", "Arranging elements in order.")
    ]
}

prefix_questions = [
    "Explain",
    "Define",
    "What is",
    "Can you describe",
    "Give details about",
    "Why is important",
    "How does work",
    "What are advantages of",
    "Write short note on",
    "Briefly explain"
]

data = []
used = set()

while len(data) < 1000:
    topic = random.choice(list(subjects.keys()))
    q, a = random.choice(subjects[topic])

    prefix = random.choice(prefix_questions)

    new_q = f"{prefix} {q}".lower()

    if new_q not in used:
        used.add(new_q)
        data.append({
            "question": new_q,
            "answer": a
        })

with open("chatbot_data.json", "w") as f:
    json.dump(data, f, indent=4)

print("✅ 1000 UNIQUE Q&A generated successfully!")