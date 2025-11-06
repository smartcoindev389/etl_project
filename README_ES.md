# Proyecto ETL - Historización MySQL en la Nube

Sistema ETL completo para procesar archivos CSV mensuales y almacenarlos en base de datos MySQL con soporte completo de historización.

## Características

- ✅ **Soporte para carpetas anidadas** - Descubre y procesa automáticamente archivos CSV de múltiples carpetas por mes
- ✅ Procesamiento mensual de CSV con historización
- ✅ Filtrado automático de columnas (maneja diferentes estructuras de CSV)
- ✅ **Carga masiva de datos históricos** - Carga TODOS los archivos CSV de estructuras de carpetas anidadas automáticamente
- ✅ Detección y prevención de archivos duplicados (hashing SHA256)
- ✅ Registro de auditoría completo para todas las cargas
- ✅ Soporte para MySQL local y en la nube
- ✅ Extracción automática de mes desde rutas de archivos (YYYY-MM, YYYYMM, nombres de mes)
- ✅ Procesos scripteados y repetibles (sin trabajo manual requerido)
- ✅ Procesamiento por lotes para archivos grandes
- ✅ Manejo de errores y lógica de reintento

## Estructura del Proyecto

```
etl_project/
├── config.py                          # Gestión de configuración
├── etl_monthly_processor.py          # Procesador ETL básico (filtra columnas automáticamente)
├── etl_merge_processor.py            # Procesador de merge (replica lógica del notebook)
├── bulk_historical_loader.py         # Cargador masivo de datos históricos
├── bulk_load_all_script.py          # Script completo de carga masiva (recomendado)
├── test_mysql_connection.py          # Utilidad para probar conexión
├── requirements.txt                   # Dependencias de Python
├── .env.example                      # Plantilla de variables de entorno
│
├── database/
│   ├── schema.sql                    # Plantilla de esquema base
│   ├── schema_resultados.sql         # Esquema completo (111 columnas de datos + metadata)
│   └── init_database.py              # Inicialización de base de datos
│
├── utils/
│   ├── db_utils.py                   # Utilidades de base de datos
│   └── schema_generator.py           # Generador de esquema desde CSV
│
└── fending data/                     # Archivos CSV del cliente (ignorados en git)
    ├── Mes1/                         # Ejemplo: Carpetas mensuales
    │   ├── Carpeta1/                 # Múltiples carpetas por mes
    │   │   ├── resultados_analisis_completo.csv
    │   │   └── grabaciones_multimedia.csv
    │   └── Carpeta2/
    │       └── todas_conversaciones.csv
    └── Mes2/
        └── ...
```

## Configuración

### 1. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno

Copiar `.env.example` a `.env` y actualizar con tus credenciales de base de datos:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# O crear manualmente el archivo .env
```

Editar `.env` con tus credenciales de MySQL:

```env
# MySQL Local (para XAMPP)
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=
DB_NAME=etl_project

# MySQL en la Nube (cuando esté listo)
CLOUD_DB_HOST=
CLOUD_DB_PORT=3306
CLOUD_DB_USER=
CLOUD_DB_PASSWORD=
CLOUD_DB_NAME=etl_project

# Configuración ETL
CSV_BASE_PATH=./data
BATCH_SIZE=10000
```

### 3. Inicializar Base de Datos

```bash
# Base de datos local
python database/init_database.py

# Base de datos en la nube
python database/init_database.py --cloud
```

### 4. Probar Conexión

```bash
# Local
python test_mysql_connection.py

# Nube
python test_mysql_connection.py --cloud
```

## Configuración de MySQL en XAMPP

Si estás usando XAMPP y obtienes errores "MySQL server has gone away" con archivos grandes:

### Solución: Configurar MySQL

1. Editar `C:\xampp\mysql\bin\my.ini` (como Administrador)

2. Buscar sección `[mysqld]` y agregar:

```ini
[mysqld]
max_allowed_packet = 256M
wait_timeout = 600
interactive_timeout = 600
net_read_timeout = 600
net_write_timeout = 600
```

3. Reiniciar MySQL en XAMPP Control Panel:
   - Clic en **Stop** en MySQL
   - Esperar unos segundos
   - Clic en **Start** en MySQL

### Alternativa: Solución SQL Rápida (Temporal)

Si no puedes editar el archivo ahora:

1. Abrir **phpMyAdmin**: http://localhost/phpmyadmin
2. Ir a pestaña **SQL**
3. Ejecutar:

```sql
SET GLOBAL max_allowed_packet = 268435456;
SET GLOBAL wait_timeout = 600;
SET GLOBAL interactive_timeout = 600;
SET GLOBAL net_read_timeout = 600;
SET GLOBAL net_write_timeout = 600;
```

**Nota**: Estos ajustes se resetean cuando MySQL se reinicia, así que edita `my.ini` para una solución permanente.

## Uso

### Cuatro tablas desde fending_data (1 tabla por CSV)

Este proyecto crea exactamente 4 tablas en la base de datos, una por cada CSV en `fending_data`, con nombres de tabla iguales al nombre del archivo (sin `.csv`):

- resultados_analisis_completo_metadata_final_nps
- flags_resumen_total_con_pagos_atc
- flags_resumen_total_con_pagos_galicia
- flags_resumen_total_con_morosidad

Pasos para crearlas y cargar datos:

```bash
# 1) Generar archivos SQL (CREATE TABLE) a partir de los CSVs
python tools/generate_sql_from_csvs.py

# 2) Aplicar todos los SQLs a la base (crea las 4 tablas)
python database/init_database.py           # local
python database/init_database.py --cloud   # nube

# 3) Cargar datos en esas 4 tablas
python create_tables_from_csvs.py --path "fending_data"
python create_tables_from_csvs.py --path "fending_data" --cloud

# 4) Verificar
# En MySQL:
#   SHOW TABLES;
#   SELECT COUNT(*) FROM resultados_analisis_completo_metadata_final_nps;
```

### Crear 4 tablas con el mismo nombre que los archivos CSV (importación única)

Si necesitas crear una tabla por CSV con el nombre de la tabla igual al nombre del archivo CSV (sin la extensión .csv, preservando espacios y paréntesis), usa el script auxiliar:

```bash
# Base de datos local
python create_tables_from_csvs.py --path "fending_data"

# Base de datos en la nube
python create_tables_from_csvs.py --path "fending_data" --cloud

# Ajustes opcionales
python create_tables_from_csvs.py --path "fending_data" --sample 1000 --chunksize 5000
```

Notas:
- El script infiere tipos de MySQL por columna a partir de una muestra del CSV y crea tablas con identificadores entre comillas para permitir espacios/paréntesis en los nombres.
- Luego carga los datos completos de cada CSV en lotes dentro de la tabla creada correspondiente.

### Procesar un Archivo CSV Individual

```bash
# Procesar cualquier archivo CSV (filtra columnas automáticamente)
python etl_monthly_processor.py --file "fending data\resultados_analisis_completo.csv"

# Procesar archivo final mergeado
python etl_monthly_processor.py --file "fending data\resultados_analisis_completo_metadata_final_nps2.csv"
```

### Procesar Todos los Archivos de un Mes

```bash
python etl_monthly_processor.py --month 2025-08 --path "fending data"
```

### Merge y Procesar (Recomendado)

Encuentra y mergea automáticamente archivos fuente (replica lógica del notebook):

```bash
# Procesar Agosto 2025
python etl_merge_processor.py --month 2025-08 --path "fending data"
```

Esto hará:
1. Encontrar `resultados_analisis_completo*.csv` del mes
2. Encontrar `grabaciones_multimedia_*.csv` del mes
3. Encontrar `todas_conversaciones_*.csv` del mes
4. Mergearlos juntos
5. Cargar a la base de datos

### Carga Masiva de Datos Históricos

**Carga TODOS los archivos CSV de estructuras de carpetas anidadas automáticamente**

El sistema automáticamente:
- Descubre todos los archivos CSV recursivamente (incluyendo carpetas anidadas)
- Agrupa archivos por mes (incluso si están en diferentes carpetas)
- Procesa todos los archivos de todas las carpetas
- Maneja múltiples carpetas por mes
- Maneja múltiples archivos por carpeta

```bash
# Previsualizar qué se cargará (modo dry-run)
python bulk_load_all_script.py --path "fending data" --dry-run

# Cargar todos los datos históricos (de todas las carpetas)
python bulk_load_all_script.py --path "fending data"

# Cargar rango de fechas específico
python bulk_load_all_script.py \
  --path "fending data" \
  --start-month 2024-08 \
  --end-month 2024-12

# Cargar con base de datos en la nube
python bulk_load_all_script.py --path "fending data" --cloud
```

**Alternativa (cargador masivo original):**
```bash
python bulk_historical_loader.py --path "fending data" --dry-run
python bulk_historical_loader.py --path "fending data"
```

## Esquema de Base de Datos

### Tablas Principales

- **fact_records**: Tabla principal de datos (111 columnas de datos + 7 columnas de metadata)
  - Columnas de datos: Todos motivo_*_flg, flag_agrupacion_*, metadata de archivos mergeados
  - Metadata: source_file, data_month, load_ts, load_id
  - Total: 118 columnas

- **audit_loads**: Registro de auditoría completo de ETL
  - Rastrea todos los intentos de procesamiento de archivos
  - Estado, conteo de filas, tiempo, errores

- **processed_files**: Seguimiento de archivos y prevención de duplicados
  - Hashing SHA256 de archivos
  - Previene re-procesamiento de mismos archivos

- **monthly_summary**: Estadísticas agregadas mensuales

### Detalles del Esquema

El esquema de base de datos (`database/schema_resultados.sql`) coincide con la estructura CSV final mergeada:
- 111 columnas de datos de `resultados_analisis_completo_metadata_final_nps2.csv`
- 7 columnas de metadata para historización
- Filtrado automático de columnas para archivos con diferentes estructuras

## Estructura de Archivos CSV

### Archivos Soportados

1. **resultados_analisis_completo.csv** (162 columnas)
   - Contiene: nombre_archivo, fecha_procesamiento, columnas motivo_* (con frase/fraser/simil/subfrases)
   - El sistema filtra automáticamente a solo columnas de flags

2. **grabaciones_multimedia_*.csv** (18 columnas)
   - Metadata de grabaciones multimedia
   - Columnas: conversation_id, archivo_multimedia, fechas, info de cola, etc.

3. **todas_conversaciones_*.csv** (19 columnas)
   - Metadata de todas las conversaciones
   - Columnas: conversation_id, info de participantes, detalles de sesión, etc.

4. **resultados_analisis_completo_metadata_final_nps2.csv** (111 columnas)
   - Tabla FINAL mergeada (lista para cargar directamente)
   - Contiene: solo flags + metadata mergeada + datos NPS

## Detalles de Características

### Filtrado Automático de Columnas

El procesador ETL automáticamente:
- Lee columnas del esquema de base de datos
- Filtra columnas CSV para coincidir con base de datos
- Solo carga columnas que existen en la base de datos
- Maneja archivos con diferentes estructuras elegantemente

### Soporte para Carpetas Anidadas

El cargador masivo maneja estructuras de carpetas complejas:
- **Múltiples carpetas por mes**: Encuentra automáticamente todos los archivos CSV en todas las subcarpetas
- **Estructuras anidadas**: Busca recursivamente en todos los subdirectorios
- **Múltiples archivos por carpeta**: Procesa todos los archivos CSV en cada carpeta
- **Organizado por mes**: Agrupa archivos por mes independientemente de la estructura de carpetas

Ejemplo de estructura soportada:
```
data/
├── 2024-08/
│   ├── Carpeta1/
│   │   ├── resultados_analisis_completo.csv
│   │   └── grabaciones_multimedia.csv
│   └── Carpeta2/
│       └── todas_conversaciones.csv
├── 2024-09/
│   └── ...
└── 2024-10/
    ├── Subcarpeta1/
    │   └── archivo1.csv
    └── Subcarpeta2/
        └── archivo2.csv
```

¡Todos los archivos se descubren y procesan automáticamente!

### Historización

- **Todos los registros preservados**: Nunca elimina datos
- **Seguimiento mensual**: Cada registro tiene `data_month` (YYYY-MM-01)
- **Seguimiento de fuente**: Columnas `source_file` y `source_type`
- **Seguimiento de carga**: Vinculado a `load_id` en tabla de auditoría
- **Seguimiento de timestamp**: `load_ts` registra cuándo se cargó
- **Prevención de duplicados**: Archivos rastreados por hash SHA256

### Manejo de Errores

- Lógica de reintento de conexión para timeouts
- Procesamiento por lotes para archivos grandes
- Registro de errores en tabla `audit_loads`
- Capacidad de reanudación (omite archivos ya procesados)

## Comandos Comunes

```bash
# Probar conexión
python test_mysql_connection.py

# Inicializar base de datos
python database/init_database.py

# Procesar archivo individual
python etl_monthly_processor.py --file "ruta/a/archivo.csv"

# Procesar mes
python etl_monthly_processor.py --month 2025-08 --path "fending data"

# Merge y procesar (recomendado para procesamiento mensual)
python etl_merge_processor.py --month 2025-08 --path "fending data"

# Cargar TODOS los archivos de carpetas anidadas (recomendado para carga histórica)
python bulk_load_all_script.py --path "fending data" --dry-run
python bulk_load_all_script.py --path "fending data"
```

## Solución de Problemas

### "Table doesn't exist"
```bash
# Reinicializar base de datos
python database/init_database.py
```

### "MySQL server has gone away"
- **XAMPP**: Actualizar `C:\xampp\mysql\bin\my.ini` (ver Configuración de MySQL en XAMPP arriba)
- **Otro MySQL**: Actualizar `max_allowed_packet` en configuración de MySQL
- **Solución rápida**: Reducir `BATCH_SIZE` en `.env` a 1000

### "Connection failed"
- Verificar archivo `.env` con credenciales
- Verificar que MySQL esté corriendo (XAMPP Control Panel)
- Probar conexión: `python test_mysql_connection.py`

### "Column mismatch"
- El sistema filtra columnas automáticamente
- Si el problema persiste, verificar que el esquema de base de datos coincida con la estructura CSV

### Archivos Grandes Fallando
1. Actualizar configuración de MySQL `max_allowed_packet` (ver Configuración de MySQL en XAMPP)
2. Reducir `BATCH_SIZE` en `.env`
3. Procesar en lotes más pequeños manualmente

## Pruebas

### Probar con Datos de Muestra

```bash
# Probar con muestra pequeña (100 filas)
python etl_monthly_processor.py --file test_sample.csv
```

### Verificar Datos Cargados

Verificar en base de datos:
```sql
-- Contar registros
SELECT COUNT(*) FROM fact_records;

-- Verificar por mes
SELECT data_month, COUNT(*) 
FROM fact_records 
GROUP BY data_month;

-- Verificar registros de auditoría
SELECT * FROM audit_loads ORDER BY start_ts DESC LIMIT 10;
```

## Utilidades de Base de Datos

```python
from utils.db_utils import get_database_stats, verify_data_integrity

# Obtener estadísticas
stats = get_database_stats(use_cloud=False)
print(f"Total de registros: {stats['total_records']}")
print(f"Registros por mes: {stats['records_by_month']}")

# Verificar integridad
checks = verify_data_integrity(use_cloud=False)
print(f"Todas las verificaciones pasaron: {checks['all_passed']}")
```

## Despliegue en la Nube

### Configurar MySQL en la Nube

1. Elegir proveedor (Railway, PlanetScale, AWS RDS, Aiven)
2. Crear instancia de base de datos MySQL
3. Obtener credenciales de conexión
4. Actualizar `.env` con variables `CLOUD_DB_*`
5. Probar: `python test_mysql_connection.py --cloud`
6. Inicializar: `python database/init_database.py --cloud`

### Listo para Automatización

Todos los scripts son basados en CLI y están listos para:
- Google Cloud Scheduler
- AWS Lambda / EventBridge
- GitHub Actions
- Cron jobs

Ejemplo:
```bash
# Automatización mensual
python etl_merge_processor.py --month $(date +%Y-%m) --path /cloud/storage/data --cloud
```

## Estado del Proyecto

✅ **Completo y Listo para Producción**

- Toda la funcionalidad core implementada
- Probado con MySQL local (XAMPP)
- Listo para despliegue en la nube
- Manejo de errores completo
- Documentación completa

## Próximos Pasos

1. ✅ Configurar MySQL local (XAMPP) - **HECHO**
2. ✅ Probar con archivos de muestra - **HECHO**
3. ⚠️ Actualizar configuración de MySQL para archivos grandes (si es necesario)
4. ⚠️ Configurar MySQL en la nube (cuando esté listo)
5. ⚠️ Cargar todos los datos históricos
6. ⚠️ Configurar automatización mensual

## Soporte

Para problemas:
1. Verificar tabla `audit_loads` para detalles de errores
2. Revisar logs de conexión
3. Verificar configuración de MySQL
4. Probar con archivos más pequeños primero

---

**Versión**: 1.0.0  
**Última Actualización**: 31 de Octubre, 2025  
**Estado**: Listo para Producción

