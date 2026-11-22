# Nota fechada sobre la especificación de los indicadores (registro tardío)

**Fecha de esta nota:** 25 de octubre de 2026.
**Grupo 1, paralelo A:** Bayron Rafael Urgiles Andrade, Santiago Calle y Andrés Canchigña. **Redacta:** Bayron Rafael Urgiles Andrade.

Esta nota se escribe después de los hechos que describe y lleva su fecha real. No reemplaza ni modifica `plan_A/documentacion/especificacion_indicadores.json` (guardada el 10 de octubre de 2026 a las 16:25), ni `plan_A/documentacion/enmiendas.md` (10 de octubre, 17:07), ni el preregistro firmado (`preregistro/preregistro_v1.md`, firma del 16 de octubre de 2026 a las 12:06:47). Su único fin es dejar escrito cuál es el archivo de indicadores vigente y conectar lo que dicen esos documentos.

## 1. Por qué hace falta

La especificación en JSON del 10 de octubre no recoge el estado final de la tabla de indicadores:

- Lista `pct_concurrencia_pos` entre las variables de rango. Esa columna no existe en el archivo vigente.
- Su campo `sha256_del_parquet_indicadores` (`499158a3c2804d30…`) y la huella anotada en su enmienda v6 (`6729e3b048617581`) no corresponden a ninguna versión conservada de la tabla. Las versiones conservadas de ese día son `_versiones/planA_indicadores_v6_1.parquet` (16:35, huella `65741da3b170aaae…`) y `_versiones/planA_indicadores_v6_2.parquet` (16:40, la vigente). Las dos se guardaron después de la especificación.

Las dos versiones sí quedaron registradas el mismo día en `plan_A/documentacion/enmiendas.md` (17:07), como **enmienda v6.1** (firma `65741da3b170aaae`) y **enmienda v6.2** (firma `dc87f4b8e1282d7f`). Esta nota no agrega decisiones nuevas: deja constancia de que el JSON quedó atrás y de que el estado vigente es el que describen `enmiendas.md` y el preregistro.

## 2. El archivo vigente

| Dato | Valor |
| --- | --- |
| Archivo | `plan_A/planA_indicadores.parquet` (copia exacta de `_versiones/planA_indicadores_v6_2.parquet`) |
| Versión | v6_2 |
| Guardado | 10 de octubre de 2026, 16:40:20 |
| Filas y columnas | 446.677 filas (una por `ocid`), 66 columnas |
| SHA-256 | `dc87f4b8e1282d7f7ea814a465b43ce4269eefeb3cfce84f6e4786c18a956f5c` |

Se guardó antes de la primera corrida de modelos (11 de octubre de 2026, 17:33, corrida `20261011_1733_rapido_percentil`). Es el archivo que usaron todas las corridas, el que cita con esta misma huella `preregistro_firma.json` y el que vuelve a verificar `plan_A/documentacion/manifiesto_2026-10-25.csv`. No se ha modificado desde entonces.

## 3. Concurrencia: `pct_concurrencia_pos` se sustituyó por `dif_concurrencia_grupo` y `ref_concurrencia_grupo`

- **Lo que dice la especificación.** Su enmienda v6 del 10 de octubre recalcula el rango de concurrencia solo entre los procesos con dos o más oferentes, con el nombre `pct_concurrencia_pos`.
- **Lo que tiene el archivo.** En lugar de esa columna hay dos: `dif_concurrencia_grupo` y `ref_concurrencia_grupo`. La versión v6_1, guardada a las 16:35, ya las tiene, así que el cambio se hizo el 10 de octubre entre las 16:25 y las 16:35.
- **Dónde quedó escrito.** En `enmiendas.md`, enmienda v6.1: "las variables con más del 5 % del dominio en el valor extremo de su grupo dejan de representarse como rango y pasan a diferencia contra la mediana del grupo comparable: dif_concurrencia_grupo", y "se retiran definitivamente: pct_poca_concurrencia, pct_fraccionamiento, pct_cuota_12m, pct_recurrencia_par, pct_concurrencia_pos". La enmienda v6.2 lo mantiene. El JSON no se actualizó.
- **La definición que rige es la del preregistro** (sección 4, variable `poca_concurrencia`): mediana de oferentes del grupo menos oferentes del proceso, llevada a 0-1 dentro del grupo con cortes en los percentiles 1 y 99, donde 1 corresponde a un solo oferente. Los modelos toman `poca_concurrencia` de `dif_concurrencia_grupo`. `ref_concurrencia_grupo` guarda la referencia del grupo.
- **Valores observados en las 446.677 filas.** `dif_concurrencia_grupo`: 209.665 nulos, mínimo −636, máximo 4, 473 valores distintos. `ref_concurrencia_grupo`: 209.665 nulos, valores entre 2 y 6 (cuatro distintos). Como referencia, `ind_n_oferentes` tiene 16 nulos y un máximo de 642.
- **Dónde se calculan.** Las crean las celdas 45 (v6.1) y 46 (v6.2) de `plan_A/pruebas.ipynb`, con el nombre armado como `dif_{alias}_grupo` y `ref_{alias}_grupo`. La regla: dominio = procesos con dos o más oferentes; grupo = familia × período si tiene 30 o más procesos en el dominio, si no la familia, si no un grupo global; `ref` = mediana de oferentes del grupo; `dif` = `ref` menos los oferentes del proceso. Fuera del dominio quedan vacías. Los modelos las leen del archivo.
- **Reproducción.** Se rehicieron el 25 de octubre con esa regla y coinciden con el archivo en las 446.677 filas (sección 7).

## 4. Las columnas con sufijo `_1`

El archivo vigente tiene cinco columnas con sufijo `_1`: `pct_precio_alto_1`, `pct_monto_capital_1`, `pct_proveedor_nuevo_1`, `pct_plazo_corto_1` y `pct_firma_rapida_1`.

- Tienen exactamente los mismos nulos que su par sin sufijo.
- En las filas con dato, la diferencia media absoluta con su par es de 0,0001 o menos en precio, monto sobre capital y proveedor nuevo, de 0,0472 en plazo corto y de 0,0230 en firma rápida. Las correlaciones con su par van de 0,9966 a 1,0000.
- Las diferencias mayores están en las variables con muchos empates, que es justo lo que cambió entre las enmiendas v6, v6.1 y v6.2 (de `percent_rank` a `cume_dist` y luego al percentil a mitad de salto; celdas 45 y 46 de `plan_A/pruebas.ipynb`).
- **Origen, comprobado el 25 de octubre (sección 7):** son los percentiles de la enmienda v6 (`percent_rank`), calculados en la celda 44 de `plan_A/pruebas.ipynb`. Esa celda unió las columnas anteriores del archivo con las recalculadas, que tenían el mismo nombre, y DuckDB agregó `_1` al nombre repetido. Las celdas 45 y 46 reemplazaron después las columnas sin sufijo y dejaron las `_1`. Por eso solo las tienen las cinco columnas de rango que conservaron su nombre; las tres con `_pos` y `dif_concurrencia_grupo` son nombres nuevos.
- **Ningún modelo las usa.** El mapa de variables del cuaderno 16 toma las columnas sin sufijo. Se conservan en el archivo, que no se modifica.

## 5. Columnas que usan los modelos (las 11 variables del preregistro)

| Variable del preregistro | Columna del archivo |
| --- | --- |
| precio_alto | `pct_precio_alto` |
| monto_capital | `pct_monto_capital` |
| proveedor_nuevo | `pct_proveedor_nuevo` |
| plazo_corto | `pct_plazo_corto` |
| firma_rapida | `pct_firma_rapida` |
| recompra_30d | `pct_fraccionamiento_pos` |
| cuota_entidad | `pct_cuota_pos` |
| recurrencia_par | `pct_recurrencia_pos` |
| oferente_unico | `ind_oferente_unico` |
| poca_concurrencia | `dif_concurrencia_grupo` |
| debutante | `ind_proveedor_debutante_365` |

La ventana de 365 días del debutante y la salida de "primera vez con la entidad" no son parte de esta nota: las decidió la enmienda A del 16 de octubre de 2026, antes de los resultados que afectan.

## 6. Lo que esta nota no cambia

No cambia ningún archivo de datos, ni la especificación del 10 de octubre, ni el preregistro, ni las enmiendas. No cambia ningún resultado: el preregistro cita la huella correcta del archivo vigente y describe las 11 variables tal como se implementaron.

## 7. Comprobación del 25 de octubre de 2026

Celda de solo lectura corrida por Bayron en `plan_A/aux_capitulo1_e_inventario.ipynb`. Compara, en las 446.677 filas, nulo contra nulo y valor contra valor (tolerancia 1e-9).

| Qué se reconstruyó | Resultado |
| --- | --- |
| `ind_n_oferentes` de los indicadores contra `n_oferentes` de `planA_procesos_modelo` | Idénticas (16 nulos en los dos) |
| `dif_concurrencia_grupo`, desde los indicadores y desde la base | Idéntica en los dos casos (209.665 nulos en los dos lados, 237.012 valores iguales) |
| `ref_concurrencia_grupo`, desde los indicadores y desde la base | Idéntica en los dos casos |
| `pct_precio_alto`, `pct_monto_capital`, `pct_proveedor_nuevo`, `pct_plazo_corto`, `pct_firma_rapida` | Idénticas al percentil a mitad de salto (v6.2); media 0,5000 en cada grupo |
| Las cinco columnas `_1` | Idénticas a `percent_rank` (v6); no cumplen la regla de conservación de la v6.2 (la media de un grupo llega a alejarse 0,5 en plazo corto) |

El dominio de la concurrencia son 237.012 procesos con dos o más oferentes; los 209.665 vacíos son 209.649 procesos con uno o ningún oferente y 16 sin dato. La mediana de oferentes por grupo va de 2 a 6 (régimen especial y lista corta, 2; menor cuantía, 6; el resto, 3 o 4); un grupo global reúne 2 procesos de familias con menos de 30 casos en el dominio.

Con esto la tabla vigente queda reproducible desde sus columnas de origen en las variables de concurrencia y en los cinco percentiles de rango.
