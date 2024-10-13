# ATLAS_IQ

ATLAS_IQ is a Python-based implementation of a dynamic, self-generating knowledge repository using graph automata and large language models (LLMs). This system is based on the concept described in the paper "Prompt Crawling: Using Graph Automata to Enable Autopoiesis and Self-Generation in Knowledge Repositories" by R.J. Cordes.

## Table of Contents

- [ATLAS\_IQ](#atlas_iq)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [System Architecture](#system-architecture)
  - [Installation](#installation)
  - [Usage](#usage)
  - [System Architecture](#system-architecture-1)
  - [Core Components](#core-components)
    - [ATLAS](#atlas)
    - [Entity](#entity)
    - [Pattern](#pattern)
    - [iQuery](#iquery)
  - [Data Management](#data-management)
    - [Repository](#repository)
    - [Models](#models)
  - [Resource Handling](#resource-handling)
    - [LLM Integration](#llm-integration)
    - [API and Database Handlers](#api-and-database-handlers)
    - [Human Interface](#human-interface)
  - [Utility Modules](#utility-modules)
  - [Asynchronous Operations](#asynchronous-operations)
  - [Error Handling and Resilience](#error-handling-and-resilience)
  - [Configuration Management](#configuration-management)
  - [Advanced Features](#advanced-features)
    - [Autopoiesis](#autopoiesis)
    - [Dynamic Refactoring](#dynamic-refactoring)
    - [Authority Smoothing](#authority-smoothing)
  - [System Workflow](#system-workflow)
  - [Scalability and Performance Considerations](#scalability-and-performance-considerations)
  - [Security Considerations](#security-considerations)
  - [Testing and Validation](#testing-and-validation)
  - [Future Enhancements](#future-enhancements)
  - [Contributing](#contributing)
  - [License](#license)

## Features

- Dynamic knowledge graph generation and management
- Integration with OpenAI's GPT models for natural language processing
- Asynchronous operations for improved performance
- Graph-based data model using Neo4j
- Autopoiesis and self-generation of new knowledge entities
- Dynamic refactoring of the knowledge structure
- Authority smoothing for balanced entity importance
- Flexible resource handling (LLMs, APIs, databases)
- Configurable system parameters

## System Architecture

The following diagram illustrates the high-level architecture of the ATLAS_IQ system:

```ascii
+------------------+                       +---------------------+
|      ATLAS       |<---manages/triggers---| Global Update Cycle |<--+
+------------------+                       +---------------------+   |
        |                                                            |
        | triggers Local Update Cycles                               |
        v                                                            |
+-------------------+                                                |
|     Entities      |<-----------------------------------------------+
| (e.g., Concepts,  |                                                |
|  Scenarios, etc.) |                                                |
+---------+---------+                                                |
          |                                                          |
          | perform Local Update Cycles                              |
          v                                                          |
+-------------------+            +------------------+                |
|     Patterns      |----use---->|      iQueries    |                |
| (with Conditional |            +------------------+                |
|  Type Assertions) |                                                |
+-------------------+                                                |
          |                                                          |
          | influence behavior via                                   |
          | Conditional Type Assertions                              |
          v                                                          |
+-------------------+                                                |
|  Resource Handlers|<---process iQueries---+                        |
+-------------------+                       |                        |
          |                                    \                     |
          | interact with                    +------------------+    |
          v                                  |  External Sources|    |
+-------------------+      (LLMs, APIs,      |  (LLMs, APIs,    |    |
| Responses from    |<-----Databases, etc.)--|  Databases, etc.)|    |
| External Sources  |                        +-----------------+|    |
+-------------------+                                                |
          |                                                          |
          | update Entities / create New Entities                    |
          v                                                          |
+-------------------+                                                |
|   Entities        |-----feedback loop to Local Update Cycles-------+
| (Newly Created)   |
+---------+---------+
          |
          | may execute Functions influencing behavior
          v
+-------------------+
|   Functions       |
| - Semantic Crawl  |
| - Dynamic Refactor|
| - Auth. Smoothing |
+-------------------+
```

## Installation

1. Clone the repository:

```

git clone https://github.com/BlockScience/atlas_iq.git
cd atlas_iq

```

2. Set up a Python virtual environment:

```

python -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`

```

3. Install dependencies:

```

pip install -r requirements.txt

```

4. Set up Neo4j using Docker Compose:

The project includes a `docker-compose.yml` file. To start Neo4j, run:

```

docker-compose up -d

```

This will start a Neo4j 5.11.0 instance with the following configuration:

- Web interface available at http://localhost:7474
- Bolt port: 7687
- Initial password: password (you should change this in production)
- Memory settings: 1G for page cache, 1G for heap (initial and max)

5. Obtain an OpenAI API key from [OpenAI's website](https://openai.com/).

6. Create a `.env` file in the project root and add your configuration:

```

NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_HOST=localhost
NEO4J_PORT=7687
OPENAI_API_KEY=<your_openai_api_key>
ATLAS_UPDATE_INTERVAL=60

```

7. You're now ready to run the ATLAS_IQ system!

## Usage

1. Initialize the ATLAS system:

```python
from atlas.core.atlas import ATLAS

atlas = ATLAS()
```

2. Create initial entities and patterns:

```python
from atlas.core.entity import Entity
from atlas.core.pattern import Pattern
from atlas.core.iquery import iQuery

# Create a pattern
pattern = Pattern("example_pattern")
iquery = iQuery("example_query", "example_attribute", [your_resource_handler])
pattern.add_iquery(iquery)

# Create an entity
entity = Entity("example_entity", patterns=[pattern])
```

3. Run the ATLAS system:

```python
atlas.run()
```

This will start the global update cycle, which will continually update entities, generate new knowledge, and refactor the knowledge structure as needed.

## System Architecture

The PromptCrawling implementation is built as a modular, asynchronous system with a focus on flexibility and extensibility. At its core, it uses a graph-based data model to represent knowledge entities and their relationships. The system is designed to continuously evolve and expand its knowledge base through interactions with various information sources, primarily Large Language Models (LLMs).

Key architectural features:

- Modular design with clear separation of concerns
- Asynchronous operations for improved performance
- Graph-based data model for complex relationships
- Integration with external resources (LLMs, APIs, databases)
- Configurable and extensible components

The system is primarily implemented in Python, leveraging asyncio for concurrent operations and Neo4j as the underlying graph database.

## Core Components

### ATLAS

The ATLAS class (atlas/core/atlas.py) serves as the central coordinator of the entire system. It manages the global state, orchestrates update cycles, and oversees the creation and management of entities.

Key features of ATLAS:

- Singleton pattern implementation ensures a single instance
- Manages global update cycles (global_update_cycle method)
- Handles entity registration and unregistration
- Coordinates dynamic refactoring and autopoiesis processes
- Performs graph analysis and authority smoothing

Notable methods:

- `global_update_cycle()`: The heart of the system, continuously updating entities
- `trigger_dynamic_refactor()`: Initiates the refactoring process for entities
- `manage_autopoiesis()`: Manages the self-generation of new entities
- `perform_graph_analysis()`: Analyzes the graph structure using NetworkX
- `smooth_authority()`: Implements the authority smoothing algorithm

### Entity

The Entity class (atlas/core/entity.py) represents individual nodes in the knowledge graph. Each entity has attributes, patterns, and associated iQueries.

Key features of Entity:

- Unique identifier (entity_id)
- Dictionary of attributes
- List of associated patterns
- List of iQueries derived from patterns
- Methods for local updates and attribute management

Notable methods:

- `local_update(global_state)`: Updates the entity based on its iQueries
- `add_pattern(pattern)`: Associates a new pattern with the entity
- `add_attribute(key, value)`: Adds or updates an entity attribute
- `check_and_generate_new_entities(global_state)`: Generates new entities based on iQuery responses

### Pattern

The Pattern class (atlas/core/pattern.py) defines a collection of iQueries that can be applied to entities. Patterns can inherit from other patterns, allowing for a hierarchical structure of knowledge representation.

Key features of Pattern:

- Unique name
- List of associated iQueries
- List of parent patterns for inheritance
- Methods for managing iQueries and inheritance

Notable methods:

- `get_iqueries()`: Returns all iQueries, including inherited ones
- `add_iquery(iquery)`: Adds a new iQuery to the pattern
- `inherit_from(parent_pattern)`: Establishes inheritance relationship
- `validate_consistency()`: Checks for circular inheritance

### iQuery

The iQuery class (atlas/core/iquery.py) represents individual information requests. It encapsulates the logic for querying information sources and updating entity attributes.

Key features of iQuery:

- Target attribute to update
- List of resource handlers to use
- Conditions for execution
- Retry mechanism with exponential backoff

Notable methods:

- `execute(entity)`: Executes the iQuery, updating the entity's attributes
- `check_conditions(entity, global_state)`: Checks if the iQuery should be executed
- `build_query(entity)`: Constructs the query based on the entity's state
- `process_response(response)`: Processes the response from resource handlers

## Data Management

### Repository

The Repository class (atlas/data/repository.py) serves as an abstraction layer between the application logic and the database. It handles all database operations, including CRUD operations for entities, patterns, and iQueries.

Key features of Repository:

- Caching mechanism using TTLCache for improved performance
- Methods for creating, retrieving, updating, and deleting entities, patterns, and iQueries
- Batch operations for efficient data management

Notable methods:

- `get_entity_by_id(entity_id)`: Retrieves an entity, using cache when possible
- `create_entity(entity_id, attributes)`: Creates a new entity in the database
- `update_entity_attributes(entity_id, new_attributes)`: Updates entity attributes
- `batch_create_entities(entities_data)`: Efficiently creates multiple entities

### Models

The data models (atlas/data/models.py) define the structure of the data stored in the Neo4j database. They use the neomodel library to define node types and relationships.

Key models:

- `EntityModel`: Represents entities in the database
- `PatternModel`: Represents patterns
- `IQueryModel`: Represents iQueries
- `ResourceHandlerModel`: Represents resource handlers

These models define the properties and relationships of each node type in the graph database, ensuring data integrity and enabling complex queries.

## Resource Handling

The system integrates with various external resources to gather information and update entities. This is primarily handled through different resource handler classes.

### LLM Integration

The OpenAIGPTHandler class (atlas/resources/openai_handler.py) manages interactions with OpenAI's GPT models. It handles API requests, response processing, and error handling.

Key features:

- Asynchronous API calls using aiohttp
- Retry mechanism with exponential backoff
- Response validation and processing
- Prompt construction based on entity attributes and iQuery parameters

### API and Database Handlers

The system includes handlers for external APIs (ExternalAPIHandler in atlas/resources/api_handler.py) and databases (AsyncPGDatabaseHandler in atlas/resources/database_handler.py). These handlers provide a consistent interface for different types of external resources.

### Human Interface

The AsyncHumanInterfaceHandler class (atlas/resources/human_interface.py) simulates interactions with human operators, allowing for manual input when needed.

## Utility Modules

The system includes several utility modules to support its operations:

- `CircuitBreaker` (atlas/utils/circuitbreaker.py): Implements the circuit breaker pattern for handling failures in external service calls
- `Settings` (atlas/utils/config.py): Manages configuration settings using Pydantic
- Logger (atlas/utils/logger.py): Configures logging for the system

## Asynchronous Operations

The system heavily utilizes Python's asyncio library for concurrent operations. This is evident in:

- ATLAS's global update cycle
- Entity's local update method
- iQuery execution
- Resource handler operations (especially API calls)

Asynchronous operations allow the system to handle multiple entities and queries efficiently, improving overall performance.

## Error Handling and Resilience

The system implements several strategies for error handling and resilience:

- Try-except blocks in critical sections
- Retry mechanism with exponential backoff in iQuery execution
- Circuit breaker pattern for handling external service failures
- Comprehensive logging throughout the system

## Configuration Management

The system uses Pydantic's BaseSettings for configuration management (atlas/utils/config.py). This allows for easy configuration through environment variables or .env files, with type checking and default values.

## Advanced Features

### Autopoiesis

The `manage_autopoiesis()` method in ATLAS implements the concept of autopoiesis, allowing the system to generate new entities based on existing knowledge. This process involves:

1. Checking each entity for self-generation capabilities
2. Executing self-generation methods on eligible entities
3. Registering newly generated entities with ATLAS

### Dynamic Refactoring

The `trigger_dynamic_refactor()` method in ATLAS enables the system to reorganize and update its knowledge structure. This process involves:

1. Evaluating each entity to determine if refactoring is needed
2. Executing refactoring operations on eligible entities
3. Updating the graph structure based on refactoring results

### Authority Smoothing

The authority smoothing feature (`smooth_authority()` method in ATLAS) implements a mechanism to balance the importance of entities in the graph. This process involves:

1. Performing graph analysis using NetworkX to calculate authority scores
2. Identifying entities with the lowest authority scores
3. Boosting the authority of these entities through targeted updates

## System Workflow

The general workflow of the system can be summarized as follows:

1. ATLAS initialization
2. Entity creation and registration
3. Continuous global update cycles:
   a. Entity local updates
   b. iQuery execution
   c. Dynamic refactoring (when triggered)
   d. Autopoiesis management
   e. Authority smoothing (when triggered)
4. Persistence of updated knowledge in the graph database

## Scalability and Performance Considerations

The system's design allows for scalability, but there are several considerations:

- The use of a graph database (Neo4j) allows for efficient querying of complex relationships
- Caching mechanisms (e.g., in the Repository class) help reduce database load
- Asynchronous operations allow for concurrent processing of multiple entities
- The singleton pattern for ATLAS could become a bottleneck in a distributed system

Future enhancements could include:

- Distributed processing of entities across multiple nodes
- Improved caching strategies
- Optimization of graph algorithms for large-scale knowledge bases

## Security Considerations

The current implementation includes basic security measures:

- Use of environment variables for sensitive information (e.g., API keys)
- Pydantic for type checking and validation of configuration settings

Additional security measures to consider:

- Encryption of sensitive data in the database
- Implementation of authentication and authorization for system access
- Regular security audits and vulnerability assessments

## Testing and Validation

The provided code does not include explicit test cases. Implementing a comprehensive testing strategy would be crucial for ensuring system reliability and correctness. This could include:

- Unit tests for individual components (Entity, Pattern, iQuery, etc.)
- Integration tests for database operations and external API interactions
- System tests to validate the overall behavior of the PromptCrawling system
- Performance tests to ensure scalability and efficiency

## Future Enhancements

Based on the paper's suggestions and the current implementation, potential future enhancements could include:

1. Implementation of more sophisticated graph analysis algorithms
2. Integration with a wider range of LLMs and external knowledge sources
3. Development of a user interface for system monitoring and manual interventions
4. Implementation of more advanced autopoiesis and self-organization strategies
5. Exploration of federated learning techniques for distributed knowledge acquisition
6. Integration of semantic reasoning capabilities to enhance knowledge inference
7. Development of domain-specific Pattern and iQuery libraries for specialized applications

## Contributing

Contributions to PromptCrawling are welcome! Please follow these steps to contribute:

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your fork
5. Submit a pull request

Please ensure your code adheres to the project's coding standards and include appropriate tests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

For more information on the theoretical background of this project, please refer to the original paper: "Prompt Crawling: Using Graph Automata to Enable Autopoiesis and Self-Generation in Knowledge Repositories" by R.J. Cordes.
