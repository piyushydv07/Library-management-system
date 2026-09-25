import streamlit as st
import json
import random
import string
from pathlib import Path
from datetime import datetime

DATABASE = "lib.json"

DEFAULT_DATA = {
    "books": [],
    "members": []
}


def load_data():
    if Path(DATABASE).exists():
        try:
            with open(DATABASE, "r") as f:
                content = f.read().strip()

            if content:
                return json.loads(content)

        except (json.JSONDecodeError, FileNotFoundError):
            pass

    with open(DATABASE, "w") as f:
        json.dump(DEFAULT_DATA, f, indent=4)

    return DEFAULT_DATA.copy()


def save_data():
    with open(DATABASE, "w") as f:
        json.dump(data, f, indent=4)


def gen_id(prefix="B"):
    random_id = ""

    for _ in range(5):
        random_id += random.choice(
            string.ascii_uppercase + string.digits
        )

    return prefix + "-" + random_id


data = load_data()


def add_book():
    st.subheader("Add New Book")

    title = st.text_input("Book Title")
    author = st.text_input("Book Author")
    copies = st.number_input(
        "Number of Copies",
        min_value=1,
        step=1
    )

    if st.button("Add Book"):
        if not title or not author:
            st.error("Please enter book title and author.")
            return

        book = {
            "id": gen_id("B"),
            "title": title,
            "author": author,
            "total_copies": copies,
            "available_copies": copies,
            "added_on": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        data["books"].append(book)
        save_data()

        st.success("Book added successfully!")


def list_books():
    st.subheader("All Books")

    if not data["books"]:
        st.info("No books available in the library.")
        return

    for book in data["books"]:
        with st.container(border=True):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Book ID**")
                st.write(book["id"])

            with col2:
                st.write("**Title**")
                st.write(book["title"])

            with col3:
                st.write("**Author**")
                st.write(book["author"])

            st.write(
                f"Copies: {book['available_copies']} / "
                f"{book['total_copies']} available"
            )

            st.caption(f"Added on: {book['added_on']}")


def add_member():
    st.subheader("Add New Member")

    name = st.text_input("Member Name")
    email = st.text_input("Member Email")

    if st.button("Add Member"):
        if not name or not email:
            st.error("Please enter name and email.")
            return

        member = {
            "id": gen_id("M"),
            "name": name,
            "email": email,
            "borrowed": []
        }

        data["members"].append(member)
        save_data()

        st.success("Member added successfully!")


def list_members():
    st.subheader("All Members")

    if not data["members"]:
        st.info("There are no members.")
        return

    for member in data["members"]:
        with st.container(border=True):
            st.write(f"### {member['name']}")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Member ID:** {member['id']}")

            with col2:
                st.write(f"**Email:** {member['email']}")

            if member["borrowed"]:
                st.write("**Currently Borrowed Books:**")

                for book in member["borrowed"]:
                    st.write(
                        f"- {book['title']} "
                        f"({book['book_id']})"
                    )
            else:
                st.write("No books currently borrowed.")


def borrow_book():
    st.subheader("Borrow Book")

    if not data["members"]:
        st.warning("No members available.")
        return

    if not data["books"]:
        st.warning("No books available.")
        return

    member_options = {
        f"{m['name']} ({m['id']})": m["id"]
        for m in data["members"]
    }

    book_options = {
        f"{b['title']} ({b['id']})": b["id"]
        for b in data["books"]
        if b["available_copies"] > 0
    }

    if not book_options:
        st.warning("No books are currently available.")
        return

    selected_member = st.selectbox(
        "Select Member",
        list(member_options.keys())
    )

    selected_book = st.selectbox(
        "Select Book",
        list(book_options.keys())
    )

    if st.button("Borrow Book"):
        member_id = member_options[selected_member]
        book_id = book_options[selected_book]

        member = next(
            m for m in data["members"]
            if m["id"] == member_id
        )

        book = next(
            b for b in data["books"]
            if b["id"] == book_id
        )

        borrow_entry = {
            "book_id": book["id"],
            "title": book["title"],
            "borrow_on": datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }

        member["borrowed"].append(borrow_entry)
        book["available_copies"] -= 1

        save_data()

        st.success(
            f"{book['title']} borrowed by {member['name']}!"
        )


def return_book():
    st.subheader("Return Book")

    if not data["members"]:
        st.warning("No members available.")
        return

    member_options = {
        f"{m['name']} ({m['id']})": m["id"]
        for m in data["members"]
        if m["borrowed"]
    }

    if not member_options:
        st.info("No member currently has a borrowed book.")
        return

    selected_member = st.selectbox(
        "Select Member",
        list(member_options.keys())
    )

    member_id = member_options[selected_member]

    member = next(
        m for m in data["members"]
        if m["id"] == member_id
    )

    book_options = {
        f"{b['title']} ({b['book_id']})": i
        for i, b in enumerate(member["borrowed"])
    }

    selected_book = st.selectbox(
        "Select Book to Return",
        list(book_options.keys())
    )

    if st.button("Return Book"):
        index = book_options[selected_book]

        returned_book = member["borrowed"].pop(index)

        for book in data["books"]:
            if book["id"] == returned_book["book_id"]:
                book["available_copies"] += 1
                break

        save_data()

        st.success(
            f"{returned_book['title']} returned successfully!"
        )


def dashboard():
    st.subheader("Library Dashboard")

    total_books = len(data["books"])
    total_members = len(data["members"])
    total_copies = sum(
        book["total_copies"]
        for book in data["books"]
    )
    available_copies = sum(
        book["available_copies"]
        for book in data["books"]
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Books", total_books)

    with col2:
        st.metric("Members", total_members)

    with col3:
        st.metric("Total Copies", total_copies)

    with col4:
        st.metric("Available Copies", available_copies)


st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Library Management System")
st.write("Manage books, members, borrowing and returns.")

st.sidebar.title("Navigation")

menu = st.sidebar.radio(
    "Select an option",
    [
        "Dashboard",
        "Add Book",
        "List Books",
        "Add Member",
        "List Members",
        "Borrow Book",
        "Return Book"
    ]
)

if menu == "Dashboard":
    dashboard()

elif menu == "Add Book":
    add_book()

elif menu == "List Books":
    list_books()

elif menu == "Add Member":
    add_member()

elif menu == "List Members":
    list_members()

elif menu == "Borrow Book":
    borrow_book()

elif menu == "Return Book":
    return_book()