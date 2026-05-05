from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

app = FastAPI()

# ---------------- DATABASE ----------------
books = []
history = []

# ---------------- MODEL ----------------
class Book(BaseModel):
    id: int
    title: str
    author: str
    category: str
    price: float
    available: bool

# ---------------- HELPER ----------------
def find_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            return book
    return None


# ================= HOME =================
@app.get("/")
def home():
    return {"message": "Library API Running Successfully"}


# ================= CREATE =================
@app.post("/books", status_code=201)
def create_book(book: Book):
    if find_book(book.id):
        raise HTTPException(status_code=400, detail="Book already exists")
    books.append(book.dict())
    return book


# ================= GET ALL =================
@app.get("/books")
def get_books():
    return books


# ================= SEARCH =================
@app.get("/books/search")
def search(q: str = Query(None)):
    return [b for b in books if q and q.lower() in b["title"].lower()]


# ================= SORT =================
@app.get("/books/sort")
def sort_books(order: str = "asc"):
    return sorted(books, key=lambda x: x["title"], reverse=(order == "desc"))


# ================= PAGINATION =================
@app.get("/books/pagination")
def pagination(skip: int = 0, limit: int = 2):
    return books[skip: skip + limit]


# ================= CATEGORY =================
@app.get("/books/category")
def category_filter(category: str):
    return [b for b in books if b["category"].lower() == category.lower()]


# ================= PRICE =================
@app.get("/books/price")
def price_filter(min_price: float = 0, max_price: float = 1000):
    return [b for b in books if min_price <= b["price"] <= max_price]


# ================= AVAILABLE (Q15) =================
@app.get("/books/status/available")
def available_books():
    return [b for b in books if b["available"]]


# ================= UNAVAILABLE (Q16) =================
@app.get("/books/status/unavailable")
def unavailable_books():
    return [b for b in books if not b["available"]]


# ================= COUNT (Q17) =================
@app.get("/books/total")
def count():
    return {"total_books": len(books)}


# ================= SUMMARY =================
@app.get("/summary")
def summary():
    return {
        "total_books": len(books),
        "available_books": len([b for b in books if b["available"]])
    }


# ================= BROWSE (Q20) =================
@app.get("/books/browse")
def browse(skip: int = 0, limit: int = 2, order: str = "asc"):
    data = sorted(books, key=lambda x: x["title"], reverse=(order == "desc"))
    return data[skip: skip + limit]


# ================= HISTORY =================
@app.get("/history")
def get_history():
    return history


# ================= BORROW =================
@app.post("/borrow/{book_id}")
def borrow(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if not book["available"]:
        raise HTTPException(status_code=400, detail="Already borrowed")

    book["available"] = False
    history.append({"book_id": book_id, "action": "borrow"})
    return {"message": "Book borrowed"}


# ================= RETURN =================
@app.post("/return/{book_id}")
def return_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    book["available"] = True
    history.append({"book_id": book_id, "action": "return"})
    return {"message": "Book returned"}


# ================= RESET =================
@app.delete("/reset")
def reset():
    books.clear()
    history.clear()
    return {"message": "Reset successful"}


# ================= VARIABLE ROUTES (LAST) =================
@app.put("/books/{book_id}")
def update_book(book_id: int, updated: Book):
    for i, b in enumerate(books):
        if b["id"] == book_id:
            books[i] = updated.dict()
            return updated
    raise HTTPException(status_code=404, detail="Book not found")


@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    books.remove(book)
    return {"message": "Deleted successfully"}


@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book