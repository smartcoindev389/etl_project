# CSV File Structure Documentation

## Files Analysis

### 1. `resultados_analisis_completo.csv` (162 columns)
**Purpose**: Main speech analytics results

**Structure**:
- `nombre_archivo`: File name (VARCHAR)
- `fecha_procesamiento`: Processing date (DATETIME)
- Multiple `motivo_*` columns (29 motives):
  - `motivo_*_flg`: Flag (0/1)
  - `motivo_*_frase`: Phrase found
  - `motivo_*_fraser`: Similar phrase
  - `motivo_*_simil`: Similarity
  - `motivo_*_subfrases`: Sub-phrases
- 15 `flag_agrupacion_*` columns: Grouping flags

**Total**: 2 base columns + (29 motives × 5 columns) + 15 grouping flags = 162 columns

### 2. `grabaciones_multimedia_202508_inbound_v3.csv` (18 columns)
**Purpose**: Multimedia recordings metadata

**Columns**:
- `conversation_id`: Conversation identifier
- `fecha_inicio`, `fecha_fin`: Start/end dates
- `fecha_inicio_sesion`, `fecha_fin_sesion`: Session dates
- `queue_id`, `queue_name`: Queue information
- `wrapup_code`, `conclusion_desc`: Conclusion data
- `agent_id`, `purpose`: Agent and purpose
- `cliente_ani`: Customer ANI
- `mediaType`, `recording_media`: Media type
- `participant_id`: Participant identifier
- `archivo_multimedia`: Multimedia file
- `tamano_archivo`: File size
- `url_grabacion`: Recording URL

### 3. `todas_conversaciones_mes_202508_v3.csv` (19 columns)
**Purpose**: All conversations metadata

**Columns**:
- `conversation_id`: Conversation identifier
- `fecha_inicio`, `fecha_fin`: Dates
- `participant_id`, `participant_name`: Participant info
- `purpose`, `agent_id`: Purpose and agent
- `session_cliente_ani`: Customer ANI
- `session_mediaType`: Media type
- `seg_fecha_inicio`, `seg_fecha_fin`: Segment dates
- `diferencia_minutos`: Time difference in minutes
- `queue_id`, `queue_name`: Queue info
- `wrapup_code`, `conclusion_desc`: Conclusion
- `seg_type`, `seg_disconnectType`, `seg_howEnded`: Segment details

### 4. `resultados_analisis_completo_metadata_final_nps2.csv` (111 columns)
**Purpose**: FINAL merged table - this is what gets stored in database

**Structure**:
- Columns 1-2: Base columns (nombre_archivo, fecha_procesamiento)
- Columns 3-29: motivo_*_flg columns (flags only, no frase/fraser/simil/subfrases)
- Columns 30-43: flag_agrupacion_* columns
- Columns 44-46: Additional motivo flags (Cliente_molesto, Cliente_satisfecho, Satisfacción)
- Columns 47-105: Metadata from grabaciones_multimedia and todas_conversaciones merged
- Columns 106-111: NPS columns (conclusion_consolidada, Grupo_Conclusion, codmes, PREGUNTA, RESPUESTA, FLG_BUENO)

**Merge Logic**:
1. Start with `resultados_analisis_completo.csv`
2. Keep only flag columns (remove frase, fraser, simil, subfrases)
3. Merge with `grabaciones_multimedia` on `nombre_archivo` or `archivo_multimedia`
4. Merge with `todas_conversaciones` on `conversation_id`
5. Add NPS data from BASE_NPS.xlsx

## Database Schema

The final database schema (`database/schema_resultados.sql`) matches the structure of `resultados_analisis_completo_metadata_final_nps2.csv`:

- **111 data columns** (matching final CSV)
- **7 metadata columns** (source_file, source_type, data_month, data_year, data_month_num, load_id, load_ts)
- **Total: 118 columns** in `fact_records` table

## Monthly Processing Flow

For each month:
1. Load `resultados_analisis_completo*.csv` (filter to flags only)
2. Load `grabaciones_multimedia_*YYYYMM*.csv` (if available)
3. Load `todas_conversaciones_mes_*YYYYMM*.csv` (if available)
4. Merge all tables following join logic
5. Add NPS data (if available)
6. Store final merged result in database

## File Naming Patterns

- `resultados_analisis_completo*.csv` - Main results
- `grabaciones_multimedia_*YYYYMM*_inbound_v3.csv` - Multimedia metadata
- `todas_conversaciones_mes_*YYYYMM*_v3.csv` - Conversation metadata
- `resultados_analisis_completo_metadata_final_nps2.csv` - Pre-merged final (optional, can regenerate)

## Data Types

- **Flags**: `TINYINT(1)` (0/1 values)
- **Dates**: `DATETIME`
- **Text**: `VARCHAR(255)` or `VARCHAR(500)`
- **Decimals**: `DECIMAL(15,2)` for time durations, NPS scores
- **Integers**: `INT` for counts, `TINYINT` for small integers

