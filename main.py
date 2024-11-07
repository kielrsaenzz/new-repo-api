from typing import List
from fastapi import FastAPI, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId


app = FastAPI()

"""
def get_db():
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client["fastapi"]
        collection = db["post"]
        return collection
    finally:
        client.close()
"""

MONGODB_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGODB_URI)
db = client["fastapi"]
collection = db["post"]


class Post(BaseModel):
    id: str
    title: str
    content: str
    created: datetime


class PostCreate(BaseModel):
    title: str
    content: str


@app.get("/")
def read_root():
    return JSONResponse(content={"Hello": "World", "framework": "fastapi"})


@app.get("/api/v1/post", response_model=List[Post])
def read_all_post() -> List[Post]:
    posts = collection.find()
    # result = []
    # for post in posts:
    #    result.append(
    #        Post(
    #            id=str(post["_id"]),
    #            title=post["title"],
    #            content=post["content"],
    #            created=post["created"],
    #        )
    #    )
    # return result
    return [
        Post(
            id=str(post["_id"]),
            title=post["title"],
            content=post["content"],
            created=post["created"],
        )
        for post in posts
    ]


@app.get("/api/v1/post/{post_id}", response_model=Post)
def find_one_post(post_id: str) -> Post:
    try:
        post = collection.find_one({"_id": ObjectId(post_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid ID")

    if post is None:
        raise HTTPException(status_code=400, detail="Post Not found")

    return Post(
        id=str(post["_id"]),
        title=post["title"],
        content=post["content"],
        created=post["created"],
    )


@app.post("/api/v1/post/create", response_model=Post)
def create_one_post(post: PostCreate) -> Post:
    created_time = datetime.now()
    new_post = {"title": post.title, "content": post.content, "created": created_time}
    result = collection.insert_one(new_post)
    return find_one_post(str(result.inserted_id))
    # created_post = collection.find_one({"_id": result.inserted_id})
    # return Post(
    #    id=str(created_post["_id"]),
    #    title=created_post["title"],
    #    content=created_post["content"],
    #    created=created_post["created"],
    # )


@app.put("/api/v1/post/edit/{post_id}", response_model=Post)
def edit_one_post(post_id: str, post: PostCreate) -> Post:
    find_one_post(post_id)
    updated_post_data = {"title": post.title, "content": post.content}
    collection.update_one({"_id": ObjectId(post_id)}, {"$set": updated_post_data})
    return find_one_post(post_id)


@app.delete("/api/v1/post/delete/{post_id}", response_model=Post)
def delete_one_post(post_id: str) -> Post:
    find_one_post(post_id)
    delete_result = collection.delete_one({"_id": ObjectId(post_id)})
    if delete_result.deleted_count == 1:
        return Response(
            status_code=status.HTTP_200_OK, detail="El Post se eliminó correctamente"
        )
    raise HTTPException(status_code=404, detail=f"Post {id} not found")
