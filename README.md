# Detección de anomalías en las compras públicas del Ecuador con datos abiertos del SERCOP

Código del trabajo de titulación de la Maestría en Ciencia de Datos e Inteligencia Artificial de la Universidad Internacional del Ecuador (UIDE), tema 42 del catálogo.

- **Autores:** Bayron Rafael Urgiles Andrade (parte técnica: descarga, limpieza, modelos y análisis), Santiago Calle y Andrés Canchigña.
- **Tutora:** Mgtr. María del Carmen Salazar Torres.
- **Unidad de análisis:** el proceso de contratación individual. No se estudian redes ni colusión entre empresas.

## Qué contiene y qué no

**Contiene** los cuadernos de Jupyter y los scripts que produjeron los resultados, el preregistro firmado, las cuatro enmiendas registradas (A, B, C y D), la documentación de los indicadores y los registros agregados de cada corrida (huellas SHA-256, cifras y tablas del capítulo de resultados).

**No contiene:**

- **Datos.** Los archivos Parquet pesan varios gigabytes y llevan RUC de proveedores y entidades. Se reconstruyen desde la fuente con los cuadernos 1 y 2 (ver "Datos").
- **Salidas guardadas de los cuadernos.** Se quitaron todas antes de publicar, porque algunas mostraban RUC o razones sociales.
- **RUC y nombres de personas naturales, ni de los contribuyentes del catastro del SRI.** En siete archivos se reemplazaron por marcadores (`RUC_OCULTO_01`, `CONTRIBUYENTE_01`, etc.). Las celdas que los usan no corren tal cual: los valores reales están en los archivos de datos, que no se publican (los 15 contribuyentes del catastro, en `plan_A/planA_validacion_sri.parquet`). Archivos afectados: `02_codigo/planA.ipynb` (celda 9), `02_codigo/06_base_v3_y_modelo_final.ipynb` (dos representantes legales, `PERSONA_OCULTA_01` y `_02`), `02_codigo/03_cruce_ruc_sri.ipynb`, `02_codigo/03_sri_validacion_modelo (2).ipynb`, `02_codigo/04_continue.ipynb`, `plan_A/planb.ipynb` (constante `RUC_SIN_MARCA_VIGENTE`) y `plan_A/documentacion/especificacion_indicadores.json`. Se conservan los RUC de entidades públicas, que son información institucional.
- **La lista de procesos priorizados, la clave de la muestra de H3 y las hojas de los revisores.** Un proceso priorizado es un candidato a revisión, no una irregularidad comprobada; publicar la lista proceso por proceso podría leerse como una acusación. Están a disposición del tribunal.

Fuera de esos cambios, el código es el que se ejecutó. Los registros, el preregistro y las enmiendas son copias exactas, byte por byte, y sus huellas coinciden con las de la tabla de abajo; la única excepción es `especificacion_indicadores.json`, por el marcador que reemplaza un RUC. Las rutas apuntan a `C:\SERCOP_FINAL\`, la carpeta de trabajo original, y la estructura de este repositorio la reproduce.

## Datos

- **Fuente principal:** portal de datos abiertos del SERCOP, <https://datosabiertos.compraspublicas.gob.ec>, estándar Open Contracting Data Standard (OCDS), años 2015 a 2026, descargados el 5 de septiembre de 2026 (12 archivos JSON, unos 19 GB, 2.785.355 procesos).
- **Fuentes de apoyo:** catastro de RUC del SRI, directorio de compañías de la Superintendencia de Compañías y catastro del SRI de contribuyentes por transacciones inexistentes (este último solo para validación externa, nunca como variable).
- **Base de modelado:** 446.677 procesos sin catálogo electrónico, con RUC del proveedor y monto positivo (54.012,3 millones de USD). Se puntúan 395.760 procesos iniciados desde 2016. La partición del universo y las huellas de cada archivo están en `plan_A/documentacion/manifiesto_2026-10-25.csv`.

## Orden de ejecución

El trabajo tuvo dos etapas. La etapa 1 (cuadernos 3 a 13) analizaba proveedores por año y quedó como antecedente; sus lecciones de calidad de datos están en el cuaderno 10. La tesis es la etapa 2, el Plan A (cuadernos 14 a 22).

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
| 21 | `plan_A/cuaderno21_objetivo6.ipynb` | Lista del objetivo 6 y comparación con las listas secundarias |
| 22 | `plan_A/cuaderno22_resultados.ipynb` | Tablas y figuras del capítulo de resultados; H3 con un solo revisor (exploratorio) |
| Aux. | `02_codigo/aux_capitulo1_e_inventario.ipynb` | Tablas del capítulo 1, manifiesto e inventario |

No se usa "Ejecutar todo": cada cuaderno se corre celda por celda, en el orden de la tabla.

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

La huella del cuaderno 19 se toma sobre el código de las celdas cuyo título empieza con `# CELDA 1.`, `# CELDA 2.` y `# CELDA 3.`, unidas con `"\n# ----- fin de celda -----\n"` y codificadas en UTF-8. Quitar las salidas no la cambia: la versión publicada da la misma huella.

## Resultados

| Hipótesis | Prueba | Resultado |
| --- | --- | --- |
| H1 (primaria): el ensamble recupera más anomalías inyectadas que el índice simple | Diferencia de recuperación en el 1 % superior, 7.600 inyecciones con 20 semillas | No se cumple: 0,0268 frente a 0,0330, D = −0,0062 (IC 95 %: −0,0116 a −0,0008), p = 0,9875 |
| H2 (secundaria): los procesos de contribuyentes del catastro del SRI puntúan más alto | Permutación por proveedor (9.999), Holm con H3 | No se rechaza la nula: T = 0,5301, p = 0,6058 |
| H3 (secundaria): los procesos priorizados tienen más hallazgos en la revisión documental | Exacta de Fisher unilateral, Holm con H2 | No se cumple: 4/60 frente a 3/60, p = 0,50. No concluyente: uno de los dos revisores informó que no revisó con exactitud (kappa 0,000). Con solo el otro revisor (exploratorio): 5/32 frente a 4/40, p = 0,36 |

Por la regla preregistrada (sección 10 del preregistro), la hipótesis general no queda respaldada y el resultado favorece al índice simple. Las tablas completas están en `capitulo_resultados/` y los registros de cada corrida en `modelos/`.

Los análisis exploratorios E0 a E4 de la enmienda D no se ejecutaron antes de la entrega y quedan como trabajo futuro.

## Entorno

Python 3.14.7, numpy 2.5.2, pandas 3.0.5, scikit-learn 1.9.0, DuckDB 1.5.5 y matplotlib 3.11.1, en Visual Studio Code sobre Windows (16 núcleos, 32 GB de RAM). Semilla global: 20261001. La lista de paquetes está en `requirements.txt`.

## Carpeta `antecedentes/`

`sercop_documentado_2026-09-05.ipynb` es el primer cuaderno exploratorio que se subió a este repositorio el 5 de septiembre de 2026 (antes había tres copias idénticas). No forma parte de la cadena de resultados.
