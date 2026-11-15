# Laboratorio ETL — Pipeline Híbrido (MongoDB + MySQL) con FastAPI

API REST desarrollada bajo el patrón **MVC (Model-View-Controller)** con FastAPI que implementa un flujo completo de Extracción, Transformación, Carga (ETL) y Analítica Estadística consumiendo datos desde **DummyJSON**, almacenando datos crudos en **MongoDB (Staging)** y cargando registros limpios en **MySQL (Analítica)**.

## Arquitectura del Proyecto (MVC)

```text
laboratorio_etl/
├── app/
│   ├── controllers/      # Rutas HTTP y controladores REST (FastAPI APIRouter)
│   ├── models/           # Modelos ORM relacionales (SQLAlchemy)
│   ├── services/         # Lógica de negocio (ETL, Pandas, SQL/NoSQL, Analítica)
│   ├── views/            # Esquemas de validación y respuesta (Pydantic)
│   ├── config.py         # Carga de variables de entorno (.env)
│   ├── database.py       # Conexiones a MongoDB y MySQL
│   └── main.py           # Punto de entrada de la aplicación FastAPI
├── .env                  # Variables de entorno locales (ignorado por Git)
├── .gitignore            # Exclusiones de repositorio
└── requirements.txt      # Dependencias del proyecto