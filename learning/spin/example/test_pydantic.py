from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str

user = User(id=123, name='John Doe')
print(user)
