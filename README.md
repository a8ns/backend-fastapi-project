# E-commerce API with Shop and Product Management

A FastAPI-based API for managing shops, products, inventory, and product variants. This API provides a complete solution for e-commerce applications with geographic features.

## Features

- **Shop Management**: CRUD operations for shops with location data
- **Product Management**: CRUD operations for products with categorization
- **Inventory Management**: Track product variants with color and size options
- **Category System**: Organize products with categories
- **Spatial Queries**: Find shops within a radius of a point (yet to be done)
- **Type-Safe Development**: Using SQLAlchemy 2.0 with type annotations

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy 2.0**: SQL toolkit and ORM with enhanced type safety
- **PostgreSQL**: Database with JSONB and UUID support
- **Pydantic**: Data validation and settings management
- **Asyncio**: Asynchronous I/O for high performance
- **Docker**: Containerization for easy deployment

## Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL (test database in container)
- Docker and Docker Compose (optional, for containerized setup)

### Environment Setup (for development without containers)

1. Clone the repository
2. Set up a virtual environment and install dependencies:
   ```bash
   poetry install --no-root
   ```
3. Activate environment
   ```bash
   poetry shell
   ```
4. Copy `.env.example` to `.env` and fill in your configuration values

### Running the API

The API will be available at [http://localhost:8000](http://localhost:8000)

## API Documentation

Interactive API docs are automatically generated using FastAPI:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## API Endpoints

### Shops

- `GET /api/shops/` - List all shops
- `POST /api/shops/` - Create a new shop
- `GET /api/shops/{shop_id}` - Get shop details
- `PUT /api/shops/{shop_id}` - Update a shop
- `DELETE /api/shops/{shop_id}` - Delete a shop

### Products

- `GET /api/products/` - List all products
- `POST /api/products/` - Create a new product
- `GET /api/products/{product_id}` - Get product details
- `PUT /api/products/{product_id}` - Update a product
- `DELETE /api/products/{product_id}` - Delete a product

### Inventory

- `GET /api/inventory/` - List all inventory items
- `POST /api/inventory/` - Create a new inventory item
- `GET /api/inventory/{inventory_id}` - Get inventory details
- `PUT /api/inventory/{inventory_id}` - Update an inventory item
- `DELETE /api/inventory/{inventory_id}` - Delete an inventory item

### Categories

- `GET /api/categories/` - List all categories
- `POST /api/categories/` - Create a new category
- `GET /api/categories/{category_id}` - Get category details
- `PUT /api/categories/{category_id}` - Update a category
- `DELETE /api/categories/{category_id}` - Delete a category

### Colors

- `GET /api/colors/` - List all colors
- `POST /api/colors/` - Create a new color
- `GET /api/colors/{color_id}` - Get color details
- `PUT /api/colors/{color_id}` - Update a color
- `DELETE /api/colors/{color_id}` - Delete a color

### Sizes

- `GET /api/sizes/` - List all sizes
- `POST /api/sizes/` - Create a new size
- `GET /api/sizes/{size_id}` - Get size details
- `PUT /api/sizes/{size_id}` - Update a size
- `DELETE /api/sizes/{size_id}` - Delete a size


## Database Models

The API uses SQLAlchemy 2.0 with the following models:

- **Shop**: Stores shop information including location data
- **Product**: Stores product information linked to shops
- **Category**: Provides categorization for products
- **Inventory**: Manages product variants with different colors and sizes
- **Color**: Contains color options for product variants
- **Size**: Contains size options for product variants

## Development

### Adding New Features

To extend the API:

1. Define new models in the models directory
2. Create corresponding schemas
3. Implement CRUD operations
4. Create API routes

### Database Migrations

The application automatically creates database tables on startup
