import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, trim, lower, when, count, isnan, sum as spark_sum

INPUT = 'datos.csv'

spark = SparkSession.builder.appName('AnalisisBatchDatosAbiertosConsola').getOrCreate()
spark.sparkContext.setLogLevel('ERROR')

try:
    df = (spark.read.option('header', True)
          .option('inferSchema', True)
          .option('encoding', 'UTF-8')
          .csv(INPUT))

    metadata_cols = [':id', ':version', ':created_at', ':updated_at']
    existing_metadata = [name for name in metadata_cols if name in df.columns]
    if existing_metadata:
        df = df.drop(*existing_metadata)

    print('\n' + '=' * 72)
    print('ANÁLISIS BATCH: PRODUCCIÓN AGRÍCOLA DEL VALLE DEL CAUCA')
    print('=' * 72)
    print('\n--- ESQUEMA DEL ARCHIVO ---')
    df.printSchema()
    print('\n--- MUESTRA ORIGINAL (10 FILAS) ---')
    df.show(10, truncate=False)
    original_count = df.count()
    print(f'Registros originales: {original_count} | Columnas: {len(df.columns)}')

    # Normaliza nombres de columnas para trabajar con ellos con mayor facilidad.
    renamed = []
    for i, name in enumerate(df.columns):
        clean = re.sub(r'[^a-zA-Z0-9_]+', '_', name.strip().lower()).strip('_')
        renamed.append(clean or f'columna_{i+1}')
    for old, new in zip(df.columns, renamed):
        if old != new:
            df = df.withColumnRenamed(old, new)

    # Limpia espacios y convierte marcadores comunes de ausencia a NULL.
    for name, dtype in df.dtypes:
        if dtype == 'string':
            df = df.withColumn(name, trim(col(name)))
            df = df.withColumn(
                name,
                when((col(name) == '') | lower(col(name)).isin('null', 'none', 'n/a', 'na', 'nan'), None)
                .otherwise(col(name))
            )

    before_dedup = df.count()
    df = df.dropDuplicates()
    after_dedup = df.count()
    print('\n--- LIMPIEZA ---')
    print(f'Registros duplicados eliminados: {before_dedup - after_dedup}')
    print(f'Registros después de la limpieza: {after_dedup}')

    print('\n--- VALORES NULOS POR COLUMNA ---')
    null_exprs = []
    for name, dtype in df.dtypes:
        if dtype in ('float', 'double'):
            null_exprs.append(spark_sum(when(col(name).isNull() | isnan(col(name)), 1).otherwise(0)).alias(name))
        else:
            null_exprs.append(spark_sum(when(col(name).isNull(), 1).otherwise(0)).alias(name))
    df.select(*null_exprs).show(truncate=False, vertical=True)

    print('\n--- ESTADÍSTICAS DESCRIPTIVAS ---')
    df.describe().show(50, truncate=False)

    for category_col, title in [('municipio', 'MUNICIPIOS CON MÁS REGISTROS'), ('cultivo', 'CULTIVOS CON MÁS REGISTROS'), ('subregion', 'REGISTROS POR SUBREGIÓN')]:
        if category_col in df.columns:
            print(f'\n--- {title} (TOP 10) ---')
            (df.where(col(category_col).isNotNull())
             .groupBy(category_col).count()
             .orderBy(col('count').desc(), col(category_col).asc())
             .show(10, truncate=False))

    if {'anio', 'produccion_toneladas'}.issubset(set(df.columns)):
        print('\n--- PRODUCCIÓN TOTAL POR AÑO (TONELADAS) ---')
        (df.groupBy('anio')
         .agg(spark_sum(col('produccion_toneladas')).alias('produccion_total_toneladas'),
              count('*').alias('cantidad_registros'))
         .orderBy('anio')
         .show(100, truncate=False))

    print('\nProceso Batch terminado.')
finally:
    spark.stop()
