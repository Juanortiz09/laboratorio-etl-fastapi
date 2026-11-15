# Laboratorio ETL — Pipeline Híbrido (MongoDB + MySQL) con FastAPI

API REST desarrollada con **FastAPI** bajo el patrón arquitectónico **MVC (Model-View-Controller)**. Implementa un flujo completo de Extracción, Transformación y Carga (ETL), además de funcionalidades de analítica estadística.

El proyecto consume datos de la API externa **DummyJSON**, almacena los datos originales en **MongoDB (Staging)** y carga los datos transformados en **MySQL (Analítica)**.

## 1. Arquitectura del proyecto

El proyecto está organizado siguiendo el patrón MVC:

```text
laboratorio-etl-fastapi/
├── app/
│   ├── controllers/      # Rutas HTTP y controladores REST
│   ├── models/           # Modelos relacionales de SQLAlchemy
│   ├── services/         # Lógica de negocio, ETL y analítica
│   ├── views/            # Esquemas de validación y respuesta
│   ├── config.py         # Configuración y variables de entorno
│   ├── database.py       # Conexiones a MongoDB y MySQL
│   └── main.py           # Punto de entrada de FastAPI
├── tests/                # Pruebas automatizadas con Pytest
├── .env                  # Variables de entorno locales
├── .gitignore            # Archivos excluidos de Git
├── requirements.txt      # Dependencias del proyecto
└── README.md             # Documentación del proyecto
```

## 2. Tecnologías utilizadas

- **Python:** lenguaje de programación.
- **FastAPI:** desarrollo de la API REST.
- **MongoDB:** almacenamiento de datos crudos (Staging).
- **MySQL:** almacenamiento de datos transformados (Analítica).
- **SQLAlchemy:** conexión y gestión de la base de datos relacional.
- **Pandas:** transformación y procesamiento de datos.
- **PyMongo:** interacción con MongoDB.
- **Requests:** consumo de la API externa.
- **Pydantic:** validación de datos.
- **Pytest:** pruebas automatizadas.

## 3. Fuente de datos

Se utiliza la API pública DummyJSON:

https://dummyjson.com/products

Los productos obtenidos se almacenan inicialmente en MongoDB para conservar los datos originales antes de su transformación.

## 4. Bases de datos

### MongoDB — Staging

- Base de datos: `laboratorio_etl_db`
- Colección: `productos_raw`

Almacena los documentos originales obtenidos desde DummyJSON.

### MySQL — Analítica

- Base de datos: `laboratorio_etl_sql`
- Tabla: `productos_master`

Almacena los productos después del proceso de transformación y carga.

## 5. Configuración del entorno

### Requisitos previos

Antes de ejecutar el proyecto se necesita:

- Python 3.12 o compatible.
- MongoDB instalado y en ejecución.
- MySQL instalado y en ejecución.
- Git.

### Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
cd laboratorio-etl-fastapi
```

### Crear el entorno virtual

En Windows PowerShell:

```powershell
python -m venv .venv
```

Activar el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Instalar dependencias

```powershell
python -m pip install -r requirements.txt
```

### Configurar variables de entorno

Crear un archivo llamado `.env` en la raíz del proyecto:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB=laboratorio_etl_db
MONGO_COLLECTION=productos_raw

MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=TU_CONTRASEÑA
MYSQL_DB=laboratorio_etl_sql

DUMMYJSON_URL=https://dummyjson.com/products
```

Reemplazar `TU_CONTRASEÑA` por la contraseña correspondiente al usuario de MySQL.

**Importante:** el archivo `.env` contiene información de configuración privada y no debe subirse al repositorio. Está excluido mediante `.gitignore`.

## 6. Ejecución de la aplicación

Con el entorno virtual activado, ejecutar:

```powershell
python -m uvicorn app.main:app --reload
```

La API estará disponible en:

- API: http://127.0.0.1:8000
- Documentación interactiva Swagger: http://127.0.0.1:8000/docs
- Documentación alternativa: http://127.0.0.1:8000/redoc

El endpoint raíz `/` permite comprobar que la aplicación está funcionando.

## 7. Endpoints del proyecto

La API cuenta con cinco endpoints principales:

| Método | Endpoint | Funcionalidad |
|---|---|---|
| POST | `/api/v1/etl/extraer` | Extrae productos desde DummyJSON y los almacena en MongoDB. |
| POST | `/api/v1/etl/transformar` | Transforma los documentos de MongoDB y los carga en MySQL. |
| DELETE | `/api/v1/etl/reset` | Elimina los datos almacenados en MongoDB y MySQL. |
| GET | `/api/v1/analitica/columna/{nombre}` | Realiza análisis estadístico dinámico de una columna. |
| GET | `/api/v1/etl/perfil/{id}` | Compara un producto entre MongoDB y MySQL. |

### 7.1. Extracción de datos

**POST `/api/v1/etl/extraer`**

Consume DummyJSON y almacena los productos originales en la colección `productos_raw` de MongoDB.

Permite solicitar una cantidad de productos mediante el parámetro `cantidad`.

La extracción evita duplicar documentos que ya existen.

### 7.2. Transformación y carga

**POST `/api/v1/etl/transformar`**

Obtiene los documentos almacenados en MongoDB y utiliza Pandas para:

- Normalizar los datos.
- Renombrar columnas.
- Convertir los tipos de datos.
- Procesar fechas.
- Crear el indicador `es_stock_alto`.
- Cargar los registros transformados en MySQL.

La carga utiliza una operación de actualización o inserción para manejar registros existentes.

### 7.3. Reinicio de datos

**DELETE `/api/v1/etl/reset`**

Elimina los documentos de la colección de MongoDB y los registros de la tabla `productos_master` de MySQL.

Este endpoint permite reiniciar el entorno de datos para ejecutar nuevamente el proceso ETL.

**Advertencia:** esta operación elimina los datos almacenados en ambas bases de datos.

### 7.4. Análisis estadístico por columna

**GET `/api/v1/analitica/columna/{nombre}`**

Realiza un análisis dinámico según el tipo de dato de la columna solicitada.

Puede identificar y calcular:

- Columnas numéricas: mínimo, máximo, promedio, mediana y desviación estándar.
- Columnas booleanas: cantidad de valores verdaderos y falsos.
- Columnas categóricas: distribución y frecuencia de valores.
- Columnas de fecha: fechas mínima y máxima y rango de días.
- Valores nulos y cantidad de registros.

También valida que la columna solicitada exista en el modelo relacional.

### 7.5. Perfil dual

**GET `/api/v1/etl/perfil/{id}`**

Consulta un producto en MongoDB y MySQL para comparar la información almacenada en ambas bases de datos.

Identifica tres posibles estados:

- `SINCRONIZADO`: el producto existe en ambas bases de datos.
- `SOLO_STAGING`: el producto existe únicamente en MongoDB.
- `SOLO_ANALITICA`: el producto existe únicamente en MySQL.

La respuesta incluye los datos encontrados en cada sistema y el estado de sincronización.

## 8. Pruebas automatizadas

El proyecto utiliza Pytest para verificar el funcionamiento de los servicios y la lógica de negocio.

Ejecutar todas las pruebas con:

```powershell
python -m pytest -v
```

Las pruebas cubren:

- Extracción de productos.
- Validación de cantidades.
- Manejo de productos existentes.
- Transformación y carga de datos.
- Manejo de errores y rollback.
- Análisis estadístico por columna.
- Comparación del perfil dual entre MongoDB y MySQL.

## 9. Flujo general del proceso ETL

```text
             DummyJSON API
                   |
                   v
          1. EXTRACCIÓN
                   |
                   v
             MongoDB
              STAGING
                   |
                   v
        2. TRANSFORMACIÓN
              Pandas
                   |
                   v
           3. CARGA
                   |
                   v
              MySQL
             ANALÍTICA
                   |
          +--------+--------+
          |                 |
          v                 v
   Análisis por       Perfil dual
     columna          MongoDB/MySQL
```

## 10. Objetivo del laboratorio

Implementar un pipeline ETL híbrido que integre tecnologías SQL y NoSQL mediante una API REST, aplicando principios de arquitectura MVC, procesamiento de datos con Pandas, persistencia en bases de datos y análisis estadístico.

El proyecto permite comprender las etapas de extracción, transformación, carga y explotación analítica de datos dentro de una arquitectura backend.