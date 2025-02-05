Blog Post Generation API
 This project implements an API for managing users, blog posts, and integrating an AI agent to generate blog content. The API is built using FastAPI for the backend, SQLite as the database, and utilizes SQLAlchemy for database interaction and Alembic for migrations. It also integrates an AI agent to generate blog posts based on user input.

Core Functionality
1. User Management
User Registration and Authentication:
  Users can register by providing a username and password.
  Authentication is handled using JSON Web Tokens (JWT).
SQLite Database:
  User information, including credentials and session tokens, are stored in an SQLite database.
User Sessions:
  Handles user sessions using JWT tokens for authentication and authorization.
2. Blog Post Management
Create Blog Posts:
  Users can create new blog posts using an integrated AI agent to generate content.
Database Storage:
  Blog posts are stored in the SQLite database.
CRUD Operations:
  Users can retrieve, update, or delete their blog posts.
Association:
  Blog posts are linked to the users who create them.
3. AI Agent Integration
  AI Agent Script Integration:
  The project integrates an AI agent for generating blog posts using an external Python script, based on a user-provided topic.
Asynchronous Handling:
  Blog post generation is processed asynchronously to handle long-running tasks efficiently.
Error Handling:
  The AI agent interactions are wrapped with error handling mechanisms to ensure smooth operation.

Technical Requirements
  1. Project Structure
      The project follows best practices inspired by the FastAPI Best Practices Repository, which promotes scalability, maintainability, and clean architecture.
  
  2. Database Design
      SQLAlchemy Models:
      Implemented models for users and blog posts.
  Alembic Migrations:
    Alembic is used to manage database migrations to handle schema changes.
    Relationships:
    The models are related such that blog posts are associated with users.
    
  3. API Endpoints
  The following API endpoints are available:
      POST /api/v1/users/register
          Register a new user.
          Request: username, password.
          Response: JWT token.
          POST /api/v1/users/login:
        Log in an existing user.
          Request: username, password.
          Response: JWT token.
      POST /api/v1/blogs:
          Create a new blog post.
          Request: topic (for AI agent to generate the blog post).
          Response: Blog post details.
      GET /api/v1/blogs:
          Get all blog posts.
          Response: List of blog posts.
      GET /api/v1/blogs/{id}:
          Get a single blog post by its ID.
          Response: Blog post details.
      PUT /api/v1/blogs/{id}:
          Update an existing blog post.
          Request: new content.
          Response: Updated blog post details.
      DELETE /api/v1/blogs/{id}:
          Delete a blog post by its ID.
          Response: Success message.
  4. Background Tasks
    AI Agent Background Processing:
        Blog post generation is offloaded to a background task to prevent blocking the main thread.
        Task Status Tracking:
  
  A status mechanism is implemented to track the progress of blog post generation, and users can check the status of their request.
Setup Instructions
  Prerequisites
  Python 3.8+
  SQLite database (default, can be modified in settings)

Installation
  Clone the repository:
    git clone https://github.com/blvckbill/blog-post-generation-api.git
    cd blog-post-generation-api
  
  Set up a virtual environment:
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
  Install dependencies:
    pip install -r requirements.txt
  Set up the database:
  run migrations:
    alembic upgrade head
  Start the FastAPI application:
    uvicorn src.main:app --reload
  The application should now be available at http://127.0.0.1:8000.

Design Decisions and Rationale
  SQLite was chosen for simplicity and portability as a lightweight database for this project.
  FastAPI was selected for its performance and easy integration of async features, perfect for handling long-running AI tasks.
  SQLAlchemy was used as the ORM to simplify database interactions and leverage migrations with Alembic.
  JWT Authentication was implemented for secure, stateless user authentication.
  AI Integration: The project integrates an external AI agent for content generation, making it easy to generate blog posts on-demand.
Assumptions
  Users are assumed to have a basic understanding of how to interact with API endpoints.
  The AI agent's script should be accessible and functional at the provided link.
  No external front-end is part of this application; it's strictly API-based.
  Blog post content is generated based on the user's provided topic but is entirely dependent on the AI agent's capabilities.
Future Improvements
  Frontend Interface: Adding a simple frontend to interact with the API and visualize blog posts.
  AI Model Customization: Integrating different AI models for content generation to allow more control over the content.
  Search Functionality: Allow users to search and filter blog posts by title, content, or keywords.
  User Roles: Implementing admin roles for managing users and blog posts.
  Pagination: Adding pagination for retrieving blog posts to improve performance with large datasets.
