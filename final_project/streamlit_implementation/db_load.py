##Quick script to populate and test database creation by hammering it with an array
import db_functions

PAGE = "http://127.0.0.1:5000"
import random
import string


def add_password(length=10):
    """Generates a simple pseudo-random password."""
    characters = string.ascii_letters + string.digits + string.punctuation
    # Ensure the character pool is not empty before sampling
    if not characters:
        return "defaultPass"  # Or raise an error
    # Ensure length is not greater than the population size
    k = min(length, len(characters))
    password = "".join(random.choice(characters) for i in range(k))
    return password


def create_element(element):
    # --- Lists of names for realistic generation ---
    first_names = [
        "Olivia",
        "Liam",
        "Emma",
        "Noah",
        "Amelia",
        "Oliver",
        "Ava",
        "Elijah",
        "Sophia",
        "Mateo",
        "Isabella",
        "Lucas",
        "Mia",
        "Levi",
        "Charlotte",
        "Asher",
        "Luna",
        "James",
        "Gianna",
        "Leo",
        "Aurora",
        "Grayson",
        "Harper",
        "Ezra",
        "Evelyn",
        "Luca",
        "Aria",
        "Ethan",
        "Ellie",
        "Aiden",
        "Mila",
    ]
    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
        "Hernandez",
        "Lopez",
        "Gonzalez",
        "Wilson",
        "Anderson",
        "Thomas",
        "Taylor",
        "Moore",
        "Martin",
        "Jackson",
        "Lee",
        "Perez",
        "Thompson",
        "White",
        "Harris",
        "Sanchez",
        "Clark",
        "Ramirez",
        "Lewis",
        "Robinson",
        "Walker",
        "Young",
        "Allen",
        "King",
    ]
    fname = random.choice(first_names)
    lname = random.choice(last_names)
    username = fname + "_" + lname
    email = username + "@copperonion.edu"
    element["name"] = fname + " " + lname
    element["uname"] = username
    element["email"] = email
    element["pass"] = add_password()


if __name__ == "__main__":
    NUM_STUDENTS = 21
    path = PAGE + "/create_user"
    for i in range(NUM_STUDENTS):
        element = {"obj_class": "student"}
        create_element(element)
        response = db_functions.create_user(element)
        print(response)