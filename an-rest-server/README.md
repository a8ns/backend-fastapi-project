# Shop and Product API with Map Integration

A FastAPI-based API for managing shops and products with geographical features. This API allows you to:

- Create and manage shops with location data  
- Add products associated with shops  
- Find nearby shops using geographic queries  
- Use LLM integration for generating product descriptions and names  

## Features

- **Shop Management**: CRUD operations for shops with location data  
- **Product Management**: CRUD operations for products  
- **Spatial Queries**: Find shops within a radius of a point  
- **Metadata Support**: Add custom metadata to both shops and products  
- **LLM Integration**: Generate product descriptions and names using OpenAI  

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs  
- **SQLAlchemy**: SQL toolkit and ORM  
- **GeoAlchemy2**: Geospatial extension for SQLAlchemy  
- **PostgreSQL**: Database with PostGIS extensions  
- **OpenAI**: Integration for LLM features  
- **Docker**: Containerization for easy deployment  
- **Poetry**: Dependency and environment management  

## Getting Started

### Prerequisites

- Python 3.9+  
- PostgreSQL with PostGIS extension  
- Docker and Docker Compose (optional, for containerized setup)  
- Poetry (for Python dependency management)  

### Environment Setup

1. Clone the repository  
2. Create a virtual environment with Poetry and install dependencies:
   ```bash
   poetry install
   ```
3. Activate the environment:
   ```bash
   poetry shell
   ```
4. Copy `.env.example` to `.env` and fill in your configuration values

### Running the API

#### With Docker

```bash
docker-compose up -d
```

#### Without Docker

```bash
uvicorn main:app --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000)

---

## 📘 API Documentation

Interactive API docs are automatically generated using FastAPI:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)  
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)  
- **OpenAPI schema**: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)  

Use these to explore, test, and debug the API with ease.

---

## API Endpoints

### Shops

- `GET /api/v1/shops/` - List all shops  
- `POST /api/v1/shops/` - Create a new shop  
- `GET /api/v1/shops/{shop_id}` - Get shop details with its products  
- `PUT /api/v1/shops/{shop_id}` - Update a shop  
- `DELETE /api/v1/shops/{shop_id}` - Delete a shop (soft delete)  
- `GET /api/v1/shops/nearby` - Find shops within radius of a point  

### Products

- `GET /api/v1/products/` - List all products  
- `POST /api/v1/products/` - Create a new product  
- `GET /api/v1/products/{product_id}` - Get product details  
- `PUT /api/v1/products/{product_id}` - Update a product  
- `DELETE /api/v1/products/{product_id}` - Delete a product (soft delete)  
- `GET /api/v1/products/with-shop` - Get products with shop information  

### LLM Integration

- `POST /api/v1/llm/generate` - Generate text using a custom prompt  
- `POST /api/v1/llm/product-description` - Generate a product description  
- `POST /api/v1/llm/product-name` - Generate product name suggestions  

## Development

### Database Migrations

This project uses SQLAlchemy's declarative models. When making changes to models:

1. Run database initialization during app startup or manually:
   ```python
   from db.db_utils import init_db
   await init_db()
   ```

### Adding New Routes

To add new functionality:

1. Create route handlers in appropriate files in the `api/routes/` directory  
2. Update imports and route includes in `api/routers.py` if needed  

## Project Structure

```
project_root/
├── api/
│   ├── __init__.py
│   ├── routers.py            # Central router configuration
│   ├── dependencies.py       # Shared dependencies
│   └── routes/
│       ├── __init__.py
│       ├── shops.py          # Shop endpoints only
│       ├── products.py       # Product endpoints only
│       └── llm.py            # LLM endpoints only
├── core/
│   ├── __init__.py
│   └── config.py
├── db/
│   ├── __init__.py
│   ├── base_model.py
│   ├── db_utils.py
│   └── session.py
├── models/
│   ├── __init__.py
│   ├── shop.py
│   └── product.py
├── schemas/
│   ├── __init__.py
│   ├── shop.py
│   ├── product.py
│   └── llm.py
├── services/
│   ├── __init__.py
│   ├── claude_service.py
│   └── openai_service.py
├── main.py
├── .env
├── pyproject.toml
└── Dockerfile 
```