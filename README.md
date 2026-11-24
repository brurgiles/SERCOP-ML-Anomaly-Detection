# Detección de anomalías en las compras públicas del Ecuador con datos abiertos del SERCOP

Código del trabajo de titulación de la Maestría en Ciencia de Datos e Inteligencia Artificial de la Universidad Internacional del Ecuador (UIDE), tema 42 del catálogo.

- **Autores:** Bayron Rafael Urgiles Andrade (parte técnica: descarga, limpieza, modelos y análisis), Santiago Calle y Andrés Canchigña.
- **Tutora:** Mgtr. María del Carmen Salazar Torres.
- **Unidad de análisis:** el proceso de contratación individual. No se estudian redes ni colusión entre empresas.

## Qué contiene y qué no

**Contiene** los cuadernos de Jupyter y los scripts que produjeron los resultados, el preregistro firmado, las cuatro enmiendas registradas (A, B, C y D), la documentación de los indicadores y los registros agregados de cada corrida (huellas SHA-256, cifras y tablas del capítulo de resultados, y los resultados de los análisis exploratorios y de la explicación de la lista).

**No contiene:**

- **Datos.** Los archivos Parquet pesan varios gigabytes y llevan RUC de proveedores y entidades. Se reconstruyen desde la fuente con los cuadernos 1 y 2 (ver "Datos").
- **Salidas guardadas de los cuadernos.** Se quitaron todas antes de publicar, porque algunas mostraban RUC o razones sociales.
- **RUC y nombres de personas naturales, ni de los contribuyentes del catastro del SRI.** En siete archivos se reemplazaron por marcadores (`RUC_OCULTO_01`, `CONTRIBUYENTE_01`, etc.). Las celdas que los usan no corren tal cual: los valores reales están en los archivos de datos, que no se publican (los 15 contribuyentes del catastro, en `plan_A/planA_validacion_sri.parquet`). Archivos afectados: `02_codigo/planA.ipynb` (celda 9), `02_codigo/06_base_v3_y_modelo_final.ipynb` (dos representantes legales, `PERSONA_OCULTA_01` y `_02`), `02_codigo/03_cruce_ruc_sri.ipynb`, `02_codigo/03_sri_validacion_modelo (2).ipynb`, `02_codigo/04_continue.ipynb`, `plan_A/planb.ipynb` (constante `RUC_SIN_MARCA_VIGENTE`) y `plan_A/documentacion/especificacion_indicadores.json`. Se conservan los RUC de entidades públicas, que son información institucional.
- **Tablas proceso por proceso de las corridas** (`explicacion_por_proceso.csv` y los `*_inyecciones.csv` de las inyecciones sintéticas). Quedan en la computadora de trabajo; aquí solo van los registros y las tablas agregadas.
- **La lista de procesos priorizados, la clave de la muestra de H3 y las hojas de los revisores.** Un proceso priorizado es un candidato a revisión, no una irregularidad comprobada; publicar la lista proceso por proceso podría leerse como una acusación. Están a disposición del tribunal.

Fuera de esos cambios, el código es el que se ejecutó. Los registros, el preregistro y las enmiendas son copias exactas, byte por byte, y sus huellas coinciden con las de la tabla de abajo; la única excepción es `especificacion_indicadores.json`, por el marcador que reemplaza un RUC. Las rutas apuntan a `C:\SERCOP_FINAL\`, la carpeta de trabajo original, y la estructura de este repositorio la reproduce.

## Datos

- **Fuente principal:** portal de datos abiertos del SERCOP, <https://datosabiertos.compraspublicas.gob.ec>, estándar Open Contracting Data Standard (OCDS), años 2015 a 2026, descargados el 5 de septiembre de 2026 (12 archivos JSON, unos 19 GB, 2.785.355 procesos).
- **Fuentes de apoyo:** catastro de RUC del SRI, directorio de compañías de la Superintendencia de Compañías y catastro del SRI de contribuyentes por transacciones inexistentes (este último solo para validación externa, nunca como variable).
- **Base de modelado:** 446.677 procesos sin catálogo electrónico, con RUC del proveedor y monto positivo (54.012,3 millones de USD). Se puntúan 395.760 procesos iniciados desde 2016. La partición del universo y las huellas de cada archivo están en `plan_A/documentacion/manifiesto_2026-10-25.csv`.

## Orden de ejecución

El trabajo tuvo dos etapas. La etapa 1 (cuadernos 3 a 13) analizaba proveedores por año y quedó como antecedente; sus lecciones de calidad de datos están en el cuaderno 10. La tesis es la etapa 2, el Plan A (cuadernos 14 a 23).

| N.º | Archivo | Qué hace |
| --- | --- | --- |
| 1 | `02_codigo/01_transformar_json_a_parquet.ipynb` | JSON del OCDS a Parquet |
| 2 | `02_codigo/02_limpieza_etl_explicativo.ipynb` (`02_limpieza_etl.ipynb` es la misma versión sin texto) | Limpieza y ETL: tipo de contratación, monto canónico (`monto_final`) y variables base |
| 3 a 13 | `02_codigo/03_*` a `13_*` | Etapa 1, antecedente: cruce con el SRI, modelos por proveedor y año, auditoría y trazabilidad (9), circularidad (11), base final (12) y pruebas (13) |
| 10 | `02_codigo/10_fallas_y_decisiones.ipynb` | Registro de fallas F01 a F18 y las decisiones que tomó cada una |
| 14 | `02_codigo/opcionb.ipynb` | Factibilidad del diseño por proceso y verificación de los releases |
| 15 | `02_codigo/planA.ipynb` y `plan_A/pruebas.ipynb`, con `02_codigo/p2_complemento.py` | Universo segmentado, recuperación del RUC, esquema en estrella, indicadores (versión 6.2 final) y tipología de entidades |
| 16 y 17 | `plan_A/16_modelos_v3.ipynb` | Isolation Forest, LOF, autoencoder, ensamble e índice simple; lista congelada; reproducción de indicadores, firma del preregistro y H1 |
| 18 | `plan_A/planb.ipynb` | Muestra ciega de H3 (antes de abrir el SRI) y H2 |
| 19 | `plan_A/cuaderno19.ipynb` | H3: lectura ciega de las hojas, kappa y consenso, verificación de la huella del código y apertura de la clave |
| 20 | `plan_A/cuaderno20_motor.ipynb` (17 celdas, M1 a M17) y `plan_A/cuaderno20_exploratorios.ipynb` (E3a y E4) | Análisis exploratorios de la enmienda D: motor de inyección con control contra H1 (M1 a M8), E0 (métodos en 2022 y 2019), E3b (grupos de precio finos), E1 (representación `magnitud_sup`) y E2 (nivel de rareza y número de variables); E3a (dispersión del precio) y E4 (amontonamiento bajo los techos oficiales) |
| 21 | `plan_A/cuaderno21_objetivo6.ipynb` | Lista del objetivo 6 y comparación con las listas secundarias |
| 22 | `plan_A/cuaderno22_resultados.ipynb` | Tablas y figuras del capítulo de resultados; H3 con un solo revisor (exploratorio) |
| 23 | `plan_A/cuaderno23_explicacion.ipynb` | Explicación de la lista: Shapley de Isolation Forest y error por variable del autoencoder. Antes de explicar reajusta los 13 grupos con la semilla congelada y se detiene si no reproduce la lista |
| Aux. | `02_codigo/aux_capitulo1_e_inventario.ipynb` | Tablas del capítulo 1, manifiesto e inventario |
| Aux. | `plan_A/celda_E4.py` y `plan_A/celda_mediana.py` | Celdas de solo lectura que se pegan en un cuaderno: E4 (amontonamiento bajo los techos oficiales; es la celda de `cuaderno20_exploratorios.ipynb`) y la mediana de licitación frente a cotización (capítulo 1) |

No se usa "Ejecutar todo": cada cuaderno se corre celda por celda, en el orden de la tabla. En el cuaderno 20, M8 reproduce la semilla 1 de H1 y solo si coincide se sigue con el resto; en el 23, la celda E7 hace lo mismo con la lista congelada.

Tiempos de referencia en la computadora de trabajo (16 núcleos, 32 GB): H1 completo, 347 minutos; control del motor, unos 2 minutos por semilla; E1, unas 2 h 45 min; E2, unas 3,5 horas; cuaderno 23, 59 minutos. Las corridas largas guardan tras cada semilla y se reanudan. No hay que dejar que el equipo se suspenda.

## Dónde está cada parte del método

| Parte del método | Dónde |
| --- | --- |
| Fuente, descarga y conversión del OCDS | cuadernos 1 y 2 |
| Calidad de la fuente: fallas F01 a F18 y las decisiones que tomó cada una | `02_codigo/10_fallas_y_decisiones.ipynb` |
| Universo, base de modelado y cadena de filtros | `02_codigo/planA.ipynb`, `plan_A/documentacion/manifiesto_2026-10-25.csv` |
| Indicadores de riesgo (11 variables, versión 6.2) | `02_codigo/planA.ipynb`, `plan_A/pruebas.ipynb`, `plan_A/documentacion/especificacion_indicadores.json` y `nota_2026-10-25_especificacion_v6_2.md` |
| Grupos comparables, representación de entrada, modelos, ensamble, índice simple y lista congelada | `plan_A/16_modelos_v3.ipynb` |
| Evaluación con anomalías inyectadas (H1) | `plan_A/16_modelos_v3.ipynb` (celdas de H1) |
| Contribuyentes del catastro del SRI (H2) y muestra ciega de H3 | `plan_A/planb.ipynb` |
| Revisión documental (H3) | `plan_A/cuaderno19.ipynb` y el texto entregado el 16 de octubre en `plan_A/documentacion/19_analisis_H3_entregado_2026-10-16.md` |
| Lista del objetivo 6 | `plan_A/cuaderno21_objetivo6.ipynb` |
| Análisis exploratorios posteriores al preregistro | `plan_A/cuaderno20_motor.ipynb`, `plan_A/cuaderno20_exploratorios.ipynb` y la enmienda D |
| Explicación de la lista | `plan_A/cuaderno23_explicacion.ipynb` |
| Tablas y figuras del capítulo de resultados | `plan_A/cuaderno22_resultados.ipynb` |
| Estabilidad de la lista con 20 semillas | `modelos/20261016_1207_h1final/estabilidad_20_semillas.csv` (celda 9 de `plan_A/16_modelos_v3.ipynb`) |
| Concordancia entre detectores, controles de cobertura y de monto, estabilidad con dos semillas | `modelos/20261016_1017_completo_normal_sup/` (`6a_concordancia.csv`, `7_estabilidad.csv`, `9_tablero.csv` y `registro_corrida.json`, celdas 6 y 7 de `plan_A/16_modelos_v3.ipynb`) |
| Tablas del capítulo 1 y mediana por familia, período y objeto | `capitulo1/` (tablas A y B) y `capitulo1/mediana_20261123_160851/` (código en `plan_A/celda_mediana.py`) |

## Preregistro y enmiendas

La evaluación se preregistró antes de calcular cualquier resultado de validación. Toda modificación posterior se registró como enmienda numerada, con fecha y huellas.

| Documento | Fecha | SHA-256 (primeros 16 caracteres) |
| --- | --- | --- |
| `preregistro/preregistro_v1.md` (firma en `preregistro_firma.json`) | 16-oct-2026, 12:06:47 | `2edaf4047e19e7f5` |
| `enmiendas/enmienda_2026-10-16.json` (A) | 16-oct-2026 | `677cfacdb72d7040` |
| `enmiendas/enmienda_2026-10-16_b.json` (B) | 16-oct-2026 | `b173395502fd4bfa` |
| `enmiendas/enmienda_2026-10-16_c.json` (C) | 16-oct-2026 | `b26e9fd95e490f23` |
| `enmiendas/enmienda_2026-11-10_d.json` (D, posterior a H1 y H2) | 10-nov-2026, 10:53:57 | `55b01c16035d3b2b` |
| Código de las celdas 1 a 3 del cuaderno 19, registrado antes de recibir las hojas | 25-oct-2026, 19:08:27 | `44a43f6f17244567` |
| Código de las 11 primeras celdas de `cuaderno20_motor.ipynb` (control, E0 y E3b) | 22-nov-2026 | `5cc9a98d5525d282` |
| Código de las 14 primeras celdas (E1) | 22-nov-2026 | `b11503832e952417` |
| Código de las 17 celdas (E2; versión publicada) | 22 y 23-nov-2026 | `a20984a601b93dbe` |
| Código de las 10 celdas de `cuaderno23_explicacion.ipynb` (versión publicada, con la celda E8 corregida) | 23-nov-2026 | `95c2b34a2a4256c5` |

La huella del cuaderno 19 se toma sobre el código de las celdas cuyo título empieza con `# CELDA 1.`, `# CELDA 2.` y `# CELDA 3.`, unidas con `"\n# ----- fin de celda -----\n"` y codificadas en UTF-8. Las huellas de los cuadernos 20 y 23 se toman igual, sobre todas sus celdas de código (en el 20, sobre las primeras 11, 14 o 17 según la corrida). Las dos celdas de `cuaderno20_exploratorios.ipynb` se registran por separado, sin el salto de línea final: E3a `9c91b2c5e35a8181` y E4 `2390e31545982bb0`. Quitar las salidas no cambia ninguna: las versiones publicadas dan las mismas huellas.

## Resultados

| Hipótesis | Prueba | Resultado |
| --- | --- | --- |
| H1 (primaria): el ensamble recupera más anomalías inyectadas que el índice simple | Diferencia de recuperación en el 1 % superior, 7.600 inyecciones con 20 semillas | No se cumple: 0,0268 frente a 0,0330, D = −0,0062 (IC 95 %: −0,0116 a −0,0008), p = 0,9875 |
| H2 (secundaria): los procesos de contribuyentes del catastro del SRI puntúan más alto | Permutación por proveedor (9.999), Holm con H3 | No se rechaza la nula: T = 0,5301, p = 0,6058 |
| H3 (secundaria): los procesos priorizados tienen más hallazgos en la revisión documental | Exacta de Fisher unilateral, Holm con H2 | No se cumple: 4/60 frente a 3/60, p = 0,50. No concluyente: uno de los dos revisores informó que no revisó con exactitud (kappa 0,000). Con solo el otro revisor (exploratorio): 5/32 frente a 4/40, p = 0,36 |

Por la regla preregistrada (sección 10 del preregistro), la hipótesis general no queda respaldada y el resultado favorece al índice simple. Las tablas completas están en `capitulo_resultados/` y los registros de cada corrida en `modelos/`.

### Análisis posteriores al preregistro (22 y 23 de noviembre de 2026)

Se decidieron después de conocer los resultados de H1 y H2, y la enmienda D (10 de noviembre de 2026) los declara como exploratorios, fuera de la corrección de Holm y de la decisión general. Un hallazgo se confirma si el intervalo de confianza del 95 % del año 2022 queda del lado favorable de cero y la estimación de 2019 tiene el mismo signo; 2022 y 2019 no se usaron para inyectar anomalías en H1. No cambian H1, H2, H3 ni la lista congelada.

| Análisis | Resultado | Estatus |
| --- | --- | --- |
| E3a, dispersión del precio | Un precio normal varía en un factor de unas 2,7 veces dentro de su grupo de referencia; tres veces la mediana queda bajo 2 desviaciones robustas (z) en 96,6 % a 99,8 % de los procesos de cinco de los seis grupos. Explica por qué H1 casi no recuperó precios inflados | Diagnóstico |
| E0, métodos en 2022 y 2019 | Isolation Forest recupera 0,136 (2024), 0,151 (2022) y 0,145 (2019) de las anomalías inyectadas en el 1 % superior, frente a 0,024 a 0,033 del ensamble y del índice simple. La ventaja viene de los dos tipos de inyección con proveedor nuevo | Exploratorio, confirmado |
| E3b, grupos de precio más finos | No mejoran la recuperación de precios inflados (diferencias entre −0,0012 y +0,0007) | Exploratorio, no confirmado |
| E1, representación `magnitud_sup` | No mejora el ensamble y empeora Isolation Forest y LOF | Exploratorio, no confirmado |
| E2, nivel de rareza y número de variables | La recuperación del ensamble sube con el cuantil de la inyección (0,027; 0,188 y 0,417 con 0,95; 0,99 y 0,999 en 2024) y con el número de variables alteradas | Descriptivo, sin regla de confirmación |
| E4, amontonamiento bajo los techos oficiales | De 92.289 procesos de menor cuantía, cotización y lista corta, solo 2 superan su techo oficial; hay exceso de presupuestos pegados al techo en las cinco combinaciones de familia y objeto, concentrado en el último 0,2 %. Hay 1.413 procesos de procedimientos que la Ley Orgánica de Integridad Pública eliminó, iniciados entre el 26 de junio y el 6 de octubre de 2025 | Descriptivo |
| Explicación de la lista (cuaderno 23) | El reajuste reproduce la lista congelada sin diferencias. La variable principal más frecuente es la repetición de compras al mismo proveedor en 30 días (`recompra_30d`): 27,5 % como la variable más rara de cada proceso (`explica`), 35,0 % según los valores de Shapley de Isolation Forest y 39,3 % según el error del autoencoder. Las variables de competencia casi no explican | Descriptivo |

### Diagnósticos sin etiquetas y capítulo 1 (descriptivos)

| Análisis | Resultado |
| --- | --- |
| Estabilidad de la lista del 1 % con 20 semillas | Jaccard medio 0,585 frente a la lista congelada (0,503 a 0,709 según el grupo): con otra semilla cambia cerca de una cuarta parte de la lista. La semilla congelada la reproduce (Jaccard 1,000) |
| Concordancia entre detectores | W de Kendall ponderada 0,606; solo contratación directa anterior queda bajo 0,5 (0,487), por eso la lista pasa de 3.965 a 3.613. Núcleo de consenso: 665 de 3.965 procesos. Jaccard del 1 % superior: Isolation Forest y LOF 0,005, Isolation Forest y autoencoder 0,155, LOF y autoencoder 0,008 |
| Mediana de licitación frente a cotización | La mediana de la licitación (93.208,7 USD) es menor que la de la cotización (271.879,4 USD) por la composición por objeto: antes de la reforma, el 71,3 % de las licitaciones son servicios, con mediana de 41.856,4 USD |

Estas cifras describen una lista de procesos elegidos por ser extremos y anomalías inyectadas de manera sintética: no prueban irregularidades. Las tablas están en `modelos/`, en las carpetas `*_expD_*` y `20261123_0751_explicacion`.

## Entorno

Python 3.14.7, numpy 2.5.2, pandas 3.0.5, scikit-learn 1.9.0, DuckDB 1.5.5 y matplotlib 3.11.1, en Visual Studio Code sobre Windows (16 núcleos, 32 GB de RAM). Semilla global: 20261001. La lista de paquetes está en `requirements.txt`.

## Carpeta `antecedentes/`

`sercop_documentado_2026-09-05.ipynb` es el primer cuaderno exploratorio que se subió a este repositorio el 5 de septiembre de 2026 (antes había tres copias idénticas). No forma parte de la cadena de resultados.

Última actualización: 23 de noviembre de 2026 (cuadernos 20 y 23, registros de los análisis exploratorios y de la explicación de la lista, estabilidad, concordancia, tablas del capítulo 1 y mediana de licitación).
