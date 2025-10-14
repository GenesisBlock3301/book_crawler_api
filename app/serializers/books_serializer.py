from bson import ObjectId

def serialize_book(book):
    book["_id"] = str(book["_id"])
    return book