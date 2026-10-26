# Análisis Batch de producción agrícola del Valle del Cauca con Apache Spark

## Descripción del proyecto

Este proyecto implementa un análisis exploratorio por lotes (*Batch*) con **Apache Spark y PySpark**, utilizando como fuente un archivo CSV con registros de producción agrícola del Valle del Cauca.

El script `batch_eda.py` procesa los datos y presenta los resultados directamente en la consola. No genera gráficos ni archivos de reportes.

### Funcionalidades

- Lee el archivo `datos.csv` e infiere el esquema de las columnas.
- Excluye, si están presentes, las columnas de metadatos `:id`, `:version`, `:created_at` y `:updated_at`.
- Muestra el esquema, una muestra de hasta 10 filas y el número de registros y columnas.
- Normaliza los nombres de las columnas para facilitar su procesamiento.
- Elimina espacios innecesarios en campos de texto y convierte marcadores comunes (`null`, `none`, `n/a`, `na`, `nan` y cadenas vacías) en valores nulos.
- Identifica y elimina registros duplicados.
- Cuenta los valores nulos por columna.
- Muestra estadísticas descriptivas.
- Presenta los 10 municipios y cultivos con más registros y, si existe esa columna, los registros por subregión.
- Si están disponibles las columnas `anio` y `produccion_toneladas`, calcula la producción total por año y la cantidad de registros.

## Requisitos

- Python 3.
- Java compatible con la versión de Apache Spark instalada.
- Apache Spark instalado y disponible mediante el comando `spark-submit`.
- PySpark instalado en el entorno de Spark.
- El archivo de datos en formato CSV.

Este script no necesita `matplotlib` ni otras librerías para visualización.

## Preparación de los archivos

Organiza los archivos de esta forma:

```text
analisis-produccion-frutales/
├── batch_eda.py
└── datos.csv
```

El archivo de entrada debe llamarse exactamente `datos.csv` y ubicarse en el mismo directorio desde el que se ejecutará el comando. El CSV debe incluir encabezados en la primera fila.

Para el resumen de producción anual, los nombres de las columnas deben quedar normalizados a `anio` y `produccion_toneladas`. Para los análisis por categoría, el script busca las columnas `municipio`, `cultivo` y `subregion`; si alguna no existe, omite ese análisis.

> Nota: el conjunto de datos se debe obtener de su fuente autorizada y comprobar que su licencia permita compartirlo. Si el repositorio solo necesita publicar el código, no es necesario incluir `datos.csv`.

## Instrucciones de ejecución

1. Clona el repositorio o descarga los archivos.
2. Copia el archivo de datos y nómbralo `datos.csv`, si todavía no tiene ese nombre.
3. Abre una terminal en el directorio que contiene `batch_eda.py` y `datos.csv`.
4. Verifica que Spark esté disponible:

   ```bash
   spark-submit --version
   ```

5. Ejecuta el análisis:

   ```bash
   spark-submit batch_eda.py
   ```

6. Revisa los resultados impresos en la consola: limpieza, valores nulos, estadísticas descriptivas, categorías con más registros y producción anual.

## Interpretación de los resultados

Los resultados permiten examinar la estructura y calidad de los datos, identificar registros duplicados y valores faltantes, consultar estadísticas descriptivas y comparar la cantidad de registros por municipio, cultivo o subregión. La producción total por año se calcula únicamente si están presentes las columnas requeridas.

El análisis es de tipo **Batch**: procesa el contenido del CSV durante una ejecución del programa. No es un flujo en tiempo real.

## Limitaciones y consideraciones

- El programa espera un archivo local llamado `datos.csv`; no descarga automáticamente los datos desde Internet.
- El esquema se infiere a partir del contenido del CSV. Conviene verificar que las columnas numéricas se interpreten correctamente.
- El conteo de registros por municipio o cultivo representa la cantidad de filas, no necesariamente el volumen producido.
- La producción anual solo se calcula cuando existen las columnas `anio` y `produccion_toneladas` con esos nombres después de la normalización.
- El script imprime los resultados en consola y no guarda reportes ni visualizaciones.
- La aplicación detiene la sesión de Spark al terminar, incluso si ocurre un error.

## Publicación en GitHub

Para compartir el proyecto, se recomienda incluir como mínimo:

```text
analisis-produccion-frutales/
├── batch_eda.py
├── README.md
└── .gitignore
```

Antes de publicar, confirma que el archivo CSV se puede redistribuir. Si no es necesario compartir los datos, publica únicamente el código y explica en el README cómo obtener y ubicar el archivo de entrada.
