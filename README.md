
# Auth Server

Auth Server implements Json Web Token (JWT) based authentication using FastAPI as it's framework. 
The testing and Docker build process is built in, it's very easy to deploy it to any host that supports Docker.

### Build the Docker image

```bash
docker build -t auth_server:latest .
```
### Run this image in Docker
Replace *<your-secret-a/b>* with a your secret strings
#### Linux/Unix/MacOS etc.
```bash
docker run -d -p 3000:80 \
       -e ACCESS_TOKEN_SECRET=<your-secret-a> \
       -e REFRESH_TOKEN_SECRET=<your-secret-b> --restart always auth_server
```
#### Windows
```cmd
docker run -d -p 3000:80 ^
       -e ACCESS_TOKEN_SECRET=<your-secret-a> ^
       -e REFRESH_TOKEN_SECRET=<your-secret-b> --restart always auth_server
```
### Authorisation Flow
#### Authorisation Endpoints
Please refer to the documentation at /docs or /redoc for API endpoint details
- POST /admin_token/
Allow admin to login via webform and obtain an access token for this server
- POST /token/
Generate access_token and refresh_token for user
- POST /refresh/
Renew access_token using a valid refresh_token
#### User CRUD Endpoints
- GET /user/
Retrieve a user using email
- GET /users/
Retrieve all users
- POST /user/
Create a new user  (Authorisation as Admin required)
- PUT /user/
Update user attributes (Authorisation as Admin required)
- DELETE /user/
Delete a user (Authorisation as Admin required)

### Admin User
#### User Model
There is only one table in the database which is mapped to the User model below:
```python 
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: EmailStr = Field(sa_column=Column("email", String, unique=True))
    hashed_password: str
    refresh_token: str | None = Field(default=None)
    is_admin: bool = False
```
#### Default Admin User
A default admin user **admin@example.com** with password **admin** is built in. Please update it to something more secure immediately following the initialisation.
