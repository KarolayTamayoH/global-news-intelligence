                                         FACULTAD DE COMPUTACIÓN
                                         CIENCIAS DE LA COMPUTACIÓN




       Big Data

1. Fuente de Datos

El conjunto de datos deberá cumplir los siguientes requisitos:

   •     Ser de naturaleza no estructurada o semiestructurada (JSON, logs, redes sociales,
         sensores, APIs, etc.).

   •     Contener al menos 50,000 registros.

   •     Poder ser actualizado periódicamente o simular actualizaciones incrementales.

   •     Documentar claramente el origen, estructura y características del dataset.

Ejemplos:

   •     Twitter/X

   •     Reddit

   •     GitHub Events

   •     APIs públicas

   •     MovieLens

   •     Datos IoT

   •     Noticias en formato JSON

2. Arquitectura Multimodelo

El proyecto deberá utilizar obligatoriamente las siguientes tecnologías:

MongoDB

Será utilizada para almacenar los documentos originales o información semiestructurada.

Ejemplos:
   •    Publicaciones.

   •    Eventos.

   •    Registros JSON.

   •    Logs.

Cassandra

Será utilizada para almacenar información optimizada para consultas masivas y series
temporales.

Ejemplos:

   •    Históricos diarios.

   •    Métricas agregadas.

   •    Contadores.

   •    KPIs por fecha.

Neo4j

Será utilizada para modelar relaciones entre entidades.

Ejemplos:

   •    Usuario → Publica → Post.

   •    Usuario → Sigue → Usuario.

   •    Actor → Participa → Película.

   •    Cliente → Compra → Producto.

Cada grupo deberá justificar técnicamente por qué cada tipo de dato fue almacenado en
una determinada base de datos.

3. Automatización con Apache Airflow

Se deberá implementar un DAG que incluya como mínimo las siguientes etapas:

   1. Extracción de datos.

   2. Validación y limpieza.
   3. Carga en MongoDB.

   4. Transformación y carga en Cassandra.

   5. Construcción de relaciones y carga en Neo4j.

   6. Generación automática de indicadores.

El flujo deberá ejecutarse de forma programada.

4. Operaciones CRUD

Se deberán implementar las operaciones básicas sobre cada una de las bases de datos.

MongoDB

   •    Crear documento.

   •    Consultar documento.

   •    Actualizar documento.

   •    Eliminar documento.

Cassandra

   •    Inserción.

   •    Consulta.

   •    Actualización.

   •    Eliminación.

Neo4j

   •    Crear nodo.

   •    Crear relación.

   •    Actualizar propiedades.

   •    Eliminar nodos o relaciones.

Las operaciones deberán demostrarse durante la exposición

5. Dashboard Analítico
Conectar las 3 bases de datos a un dashboard utilizando Streamlit o Dash (Python) u otro
que crea conveniente.

Mostrar indicadores relevantes y visualizaciones que permitan analizar los datos de
manera intuitiva.

Se valorará la creatividad y la claridad en la presentación de los indicadores.

6. Indicadores (KPIs)

Definir como mínimo cinco indicadores relevantes para el problema planteado.

Ejemplos:

   •   Número de registros procesados por día.

   •   Crecimiento diario de eventos.

   •   Entidad con mayor número de conexiones.

   •   Promedio de actividad por usuario.

   •   Tendencia temporal de publicaciones.

Cada KPI deberá incluir:

   •   Definición.

   •   Fórmula de cálculo.

   •   Interpretación.

Entregables

   1. Informe técnico (en formato PDF) que incluya:
   •   Introducción.
   •   Descripción del problema.
   •   Arquitectura propuesta.
   •   Descripción del dataset.
   •   Modelo de datos de MongoDB.
   •   Modelo de datos de Cassandra.
   •   Modelo de grafo en Neo4j.
   •   Explicación del DAG de Airflow.
   •   KPIs implementados.
•   Capturas del dashboard.
•   Conclusiones.


2. Entregable

    Cada grupo deberá presentar:

•   Código fuente completo.

•   Scripts de creación de las bases de datos.

•   DAG de Airflow.

•   Dashboard funcional.

•   Informe técnico en PDF.

•   Video demostrativo de máximo 20-25 minutos.

    En el video, todos los integrantes deberán participar y explicar claramente su aporte
    al proyecto, incluyendo la demostración de los componentes que desarrollaron.

•   Evaluación de pares

    Cada estudiante deberá evaluar las presentaciones de los demás grupos utilizando
    los criterios que indique el docente. La evaluación deberá ser individual, objetiva y
    respetuosa, considerando aspectos como la solución propuesta, la arquitectura
    multimodelo, la automatización con Airflow, el dashboard y la claridad de la
    demostración.

Fecha de entrega

    17 Noviembre del 2026
