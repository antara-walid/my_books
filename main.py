import uvicorn

from fastapi import FastAPI, Query, Path, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import List, Dict, Annotated, Optional
from database import books


class Book(BaseModel):
    name: Optional[str] = None
    author: Optional[str] = None
    rating: Optional[float] = Field(default=None, ge=0, le=10)
    read: Optional[bool] = None
    tags: Optional[List[str]] = None


app = FastAPI()


@app.get("/")
def root():
    return {
        "root": "this is root"
    }


@app.get("/books", response_model=List[Dict[str, Book]])
def get_books(limit: Annotated[str | None, Query(max_length=1)] = "3"):
    response = []
    for book_id, book in list(books.items())[:int(limit)]:
        to_add = {str(book_id): book}
        response.append(to_add)

    return response


@app.get("/books/{book_id}", response_model=Book)
def get_book_by_id(book_id: Annotated[int, Path(..., gt=0, le=1000)]):
    book = books.get(book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Can not find book by id")
    return book


@app.post("/books",
          status_code=status.HTTP_201_CREATED)
def add_book(book_list: Annotated[List[Book], Body(...)]):
    last_item = len(books) + 1
    if len(book_list) < 1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="book list should not be empty")
    for book in book_list:
        books[last_item] = jsonable_encoder(book)
        last_item += 1


@app.put("/book/{book_id}", response_model=Dict[str, Book])
def update_book(book_id: Annotated[int, Path(..., gt=0, le=1000)], updated_book: Book):
    db_book = books.get(book_id)
    if db_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Could not find Book with the given id")

    db_book = Book(**db_book)
    updated_book = updated_book.model_dump(exclude_unset=True)
    new_book = db_book.model_copy(update=updated_book)
    books[book_id] = jsonable_encoder(new_book)
    response = {str(book_id): books[book_id]}

    return response


@app.delete("/books/{book_id}")
def delete_book(book_id: Annotated[int, Path(..., gt=0, le=1000)]):
    db_book = books.get(book_id)
    if db_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Could not find Book with the given id")

    del books[book_id]


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
