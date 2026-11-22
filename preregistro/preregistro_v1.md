# Preregistro de la evaluación · versión 1

**Trabajo:** Detección de anomalías en las compras públicas del Ecuador mediante datos abiertos SERCOP (catálogo UIDE, tema 42).
**Grupo 1, paralelo A:** Bayron Rafael Urgiles Andrade, Santiago Calle y Andrés Canchigña. **Tutora:** Mgtr. María del Carmen.
**Redactado:** 16 de octubre de 2026.

Este documento fija, antes de mirar cualquier resultado de validación, las poblaciones, las variables, los modelos, las pruebas y las reglas de decisión de las hipótesis H1, H2 y H3. Se firma con la huella SHA-256 de este mismo archivo, que queda en `preregistro_firma.json`. La firma se hace **antes** de: (a) cruzar las marcas del SRI con los puntajes; (b) inyectar anomalías en los procesos de 2024; (c) empezar la revisión documental. Cualquier cambio posterior se registra como enmienda numerada y fechada; ninguna enmienda reemplaza a esta versión.

## 1. Qué se ha visto y qué no

**Ya se vio** (y por eso se declara): los diagnósticos sin etiquetas de las corridas exploratorias del cuaderno 16; un piloto de H1 con anomalías inyectadas en procesos de **2023**; la reproducción de los indicadores desde sus columnas de origen (celda R).

| Piloto de H1 con 2023 (inyección en escala de percentil) | Recuperación en el 1 % superior |
|---|---|
| Corrida rápida, representación `percentil`: ensamble / índice simple | 0,020 / 0,027 |
| Corrida rápida, representación `normal_sup`: ensamble / índice simple | 0,085 / 0,027 |
| Corrida completa, `normal_sup` (1.086 inyecciones): ensamble / índice simple | 0,112 / 0,041 (diferencia +0,072; IC 95 % +0,052 a +0,093) |

**No se ha visto:** ningún puntaje de los procesos de los contribuyentes del catastro del SRI (el archivo `planA_validacion_sri` no se ha cargado en ningún cuaderno de modelos); ninguna anomalía inyectada en procesos de 2024; ningún proceso de la muestra de revisión documental, que todavía no se ha sorteado.

## 2. Datos y huellas

| Archivo | Huella SHA-256 (16 primeros caracteres) |
|---|---|
| `plan_A/planA_indicadores.parquet` | `dc87f4b8e1282d7f` |
| `plan_A/planA_procesos_modelo.parquet` | `adb1768ebd2dd83a` |
| `enmiendas/enmienda_2026-10-16.json` (enmienda A) | `677cfacdb72d7040` |
| `enmiendas/enmienda_2026-10-16_b.json` (enmienda B) | `b173395502fd4bfa` |
| `modelos/20261016_1017_completo_normal_sup/puntajes.parquet` (lista congelada) | `eed4fbceb2cc9f3c` |
| `modelos/20261016_1017_completo_normal_sup/registro_corrida.json` | `979ec56fe8f8935a` |
| `preregistro/reproduccion_indicadores.json` (celda R) | se registra completa en la firma |

**Universo.** Base de modelado de 446.677 procesos (54.012,3 millones USD): sin catálogo electrónico, con RUC de proveedor y monto positivo, con corte de descarga al 5 de septiembre de 2026. **Se puntúan los 395.760 procesos con inicio del período de ofertas desde el 1 de enero de 2016.** Los 50.917 procesos de 2015 solo sirven de historial, porque en ese año los indicadores con ventana de 12 meses no tienen pasado (enmienda A).

## 3. Grupos comparables

Familia de procedimiento × período normativo, con el corte del 7 de octubre de 2025 aplicado a `fecha_inicio_tender`: 13 grupos. Los grupos con menos de 100 procesos no se modelan. Los grupos del período reformado son piloto: se describen, pero no entran en H1, H2 ni H3. **Año** de un proceso = año de `fecha_inicio_tender`.

## 4. Variables de los modelos (11)

| Variable | Definición | Codificación |
|---|---|---|
| precio_alto | Percentil del z robusto del logaritmo del precio unitario frente a su grupo de referencia (CPC5 × unidad, con retroceso a CPC5, CPC3 y familia; mínimo 30) | Percentil en el grupo comparable |
| monto_capital | Percentil del monto adjudicado sobre el capital suscrito (solo sociedades) | Percentil; vacío si no hay capital |
| proveedor_nuevo | Percentil inverso de la antigüedad del proveedor en días | Percentil |
| plazo_corto | Percentil inverso del plazo de presentación de ofertas | Percentil; vacío donde la familia no tiene ese plazo |
| firma_rapida | Percentil inverso de los días entre adjudicación y firma | Percentil |
| recompra_30d | Monto del mismo par proveedor-entidad y misma CPC5 en los 30 días anteriores | 0 si no ocurre; percentil entre los que ocurre |
| cuota_entidad | Monto del par sobre el monto de la entidad en los 365 días anteriores | 0 si no hay historial; percentil entre los que tienen |
| recurrencia_par | Procesos previos del par en los 365 días anteriores | 0 si no hay; percentil entre los que tienen |
| oferente_unico | Un solo oferente | 0/1 |
| poca_concurrencia | Mediana de oferentes del grupo menos oferentes del proceso, llevada a 0-1 dentro del grupo (cortes en los percentiles 1 y 99) | 1 = un solo oferente |
| debutante | Sin procesos del proveedor en los 365 días anteriores (`ind_procesos_proveedor_12m` = 0) | 0/1 |

Todas las ventanas de historial cuentan solo días anteriores, sin el día del proceso. `primera_vez_con_la_entidad` queda fuera de los modelos: con la ventana de 12 meses coincide en el 100 % con "recurrencia = 0" (celda 0). Ninguna variable sale de la marca del SRI ni de estados administrativos actuales. Una variable se retira de un grupo si tiene dato en menos del 1 % o un mismo valor en el 99,5 % o más de sus procesos.

**Representación de entrada (enmienda A):** `normal_sup`. Cada valor se convierte en su rareza dentro del grupo (percentil a mitad de salto, también para banderas y variables en dos partes), se pasa a la escala normal y la mitad inferior se lleva a 0, de modo que solo cuenta la dirección de riesgo.

**Índice simple (línea base):** promedio, sin ponderaciones, de la rareza dentro del grupo de las variables de la tabla que el proceso tiene disponibles (las 11 están orientadas: valor alto = más riesgo).

## 5. Modelos e hiperparámetros (fijos)

- **Isolation Forest:** 100 árboles, submuestra de 256.
- **Local Outlier Factor:** 20 vecinos, en modo novedad, ajustado sobre las filas distintas de una muestra de referencia de hasta 50.000 procesos; un proceso idéntico a una fila de la referencia recibe el LOF de esa fila calculado sin contarse a sí misma.
- **Autoencoder:** red con una capa intermedia de la mitad de las variables (ReLU, Adam, alpha 0,0001, lotes de 256, tasa 0,001, hasta 200 épocas, parada temprana con 10 % de validación y paciencia de 10), entrenado con hasta 50.000 procesos.
- **Patrones de disponibilidad:** un patrón con 1.000 procesos o más tiene modelo propio; uno menor usa el modelo grande cuyas variables están todas en el suyo y, si no existe, recibe un modelo propio sin la variable que le falta (topes de cómputo de 10.000 procesos).
- Cada puntaje se convierte en percentil frente a la referencia del mismo modelo. **Ensamble** = promedio de los percentiles de los tres modelos (especificación primaria). Semilla global 20261001.
- Software de la corrida congelada: Python 3.14.7, numpy 2.5.2, pandas 3.0.5, scikit-learn 1.9.0, DuckDB 1.5.5. Código: cuaderno 16 versión 3.

## 6. Lista priorizada

La lista es la de la corrida congelada (sección 2): el 1 % de procesos con mayor puntaje del ensamble en cada grupo (3.965 procesos). Núcleo de consenso: procesos que al menos dos de los tres modelos ubican en su propio 1 % superior. Regla de coherencia: en un grupo con W de Kendall menor que 0,5, la lista se reduce a su núcleo de consenso; se aplicó a contratación directa anterior a la reforma (W = 0,487) y la lista final tiene **3.613 procesos** (columna `priorizado`). Cada proceso priorizado se acompaña de las tres variables con mayor rareza dentro de su grupo.

**Estabilidad (descriptiva):** se reajustan todos los grupos con las semillas 1 a 20 y se informa el índice de Jaccard de cada lista frente a la congelada. Como control, el reajuste con la semilla original (20261001) debe reproducir la lista congelada exactamente.

## 7. H1 (primaria): anomalías inyectadas en 2024

**Enunciado.** El ensamble recupera, dentro del 1 % de procesos con mayor puntaje de cada grupo, una proporción de anomalías inyectadas mayor que la del índice simple.

**Población.** Procesos con inicio en 2024 de los grupos anteriores a la reforma que tengan al menos 1.000 procesos de 2024.

**Réplicas.** 20 semillas de inyección (1 a 20). En cada semilla y grupo se altera el 1 % de los procesos de 2024 del grupo (redondeado), repartidos en partes iguales entre los tipos aplicables al grupo en un orden sorteado. Cada proceso recibe a lo sumo una inyección por semilla.

**Tipos y magnitudes (inyectados en las variables de origen).**

| Tipo | Cambio en el origen | Elegibles |
|---|---|---|
| precio_x1,5 / precio_x2 / precio_x3 | Precio unitario = 1,5, 2 o 3 veces la mediana de su grupo de referencia de precio | Procesos con precio reproducido y precio actual por debajo de ese valor |
| oferente_unico | Número de oferentes = 1 | Familias competitivas (subasta, menor cuantía, cotización, licitación, lista corta, concurso) con 2 o más oferentes |
| plazo_p5 | Plazo de ofertas = percentil 5 del grupo | Procesos con plazo mayor que ese percentil |
| nuevo_monto_alto | Antigüedad del proveedor = 30 días; monto sobre capital = percentil 99 del grupo; sin historial (debutante = 1, cuota, recurrencia y recompra = 0) | Sociedades con capital, antigüedad mayor de 30 días y monto sobre capital menor que el percentil 99 |
| combinado_precio_oferente | precio_x2 + oferente_unico | Intersección de elegibles |
| combinado_precio_plazo | precio_x2 + plazo_p5 | Intersección de elegibles |
| combinado_nuevo_precio | nuevo_monto_alto + precio_x1,5 | Intersección de elegibles |

Un tipo solo se aplica en un grupo si las variables que modifica se usan en ese grupo.

**Recálculo.** Los indicadores alterados se recalculan con la misma regla con que se construyó la base, verificada por reproducción en la celda R (columna de origen, orientación, agrupación y fórmula de empates), comparando el nuevo valor con la distribución original de su grupo. La mediana y la escala de cada grupo de referencia de precio, y los percentiles de los demás procesos, no se recalculan, porque cambian en menos de 1/n. La firma de este documento exige que la celda R reproduzca cada indicador en al menos el 99 % de los procesos.

**Ajuste.** En cada semilla y grupo se ajustan los modelos sobre el grupo completo (2016 a 2025, con las inyecciones), con la semilla de modelo 20261001 + semilla de inyección, y se puntúan los procesos de 2024.

**Métrica.** Para cada proceso inyectado y cada método (ensamble e índice simple), acierto = 1 si queda dentro del 1 % de procesos de 2024 de su grupo con mayor puntaje (k exacto, empates al azar con semilla fija).

**Prueba.** D = promedio de (acierto del ensamble − acierto del índice simple) sobre todas las inyecciones. Remuestreo por conglomerados de semillas: 2.000 réplicas que sortean con reposición las 20 semillas. Valor p unilateral = proporción de réplicas con D ≤ 0. **H1 se cumple si p < 0,05.** Se informan D, su intervalo de confianza al 95 % y la recuperación de cada método.

**Secundarios (descriptivos):** recuperación por tipo, magnitud y grupo; cortes de 2 % y 5 %; Isolation Forest, LOF y autoencoder por separado; percentil mediano de los inyectados; remuestreo por inyección como sensibilidad.

**Código.** H1 se calcula con el cuaderno 17, que antes de empezar comprueba la huella de este documento y la de cada archivo citado, y se detiene si alguno cambió después de la firma.

## 8. H2 (secundaria): catastro del SRI

**Enunciado.** Los procesos adjudicados a contribuyentes del catastro del SRI por emitir comprobantes de transacciones inexistentes ocupan un percentil mediano de puntaje superior a 0,5.

**Población primaria.** Procesos puntuados (desde 2016, período anterior a la reforma) cuyo proveedor es uno de los **14 contribuyentes** con marca vigente al 9 de octubre de 2026. Sensibilidad: los 15 del archivo. Los procesos de 2015 quedan fuera (enmienda B).

**Puntaje (enmienda B).** Percentil a mitad de salto del puntaje del ensamble de la lista congelada, calculado **dentro de grupo × año**.

**Estadístico.** T = mediana de esos percentiles sobre todos los procesos de la población.

**Prueba: permutación por proveedor.** En cada una de 9.999 réplicas, cada contribuyente se reemplaza por un proveedor sorteado sin reposición entre los proveedores sin marca que tengan un número de procesos puntuados del mismo tramo (1; 2-3; 4-7; 8-15; 16-31; 32 o más), y se recalcula T. Valor p unilateral = (1 + réplicas con T* ≥ T) / 10.000. **Antes de calcular T** se registra el valor crítico de T (percentil 95 de la distribución nula), que es el efecto mínimo que la prueba puede detectar con estos tamaños.

**Sensibilidad.** Percentil dentro de grupo × año × decil de monto (decil dentro de grupo × año); análisis con los 15 contribuyentes; registro de contratistas incumplidos del SERCOP, con la misma prueba, si se obtiene.

**Lectura.** Un resultado no significativo se informa como no detectable con los datos disponibles, no como ausencia de efecto.

## 9. H3 (secundaria): revisión documental ciega

**Enunciado.** La proporción de procesos con hallazgos que ameritan revisión administrativa es mayor entre los priorizados que entre controles del mismo grupo, año y tramo de monto.

**Muestra (enmienda B).** Elegibles: procesos del período anterior a la reforma con inicio entre 2016 y 2024. **60 priorizados** sorteados al azar de la columna `priorizado` con semilla 20261001, con un máximo de 2 procesos por proveedor y 2 por entidad. **60 controles:** para cada priorizado, un proceso no priorizado del mismo grupo, año y decil de monto (decil dentro de grupo × año), sorteado con la misma semilla y con el mismo tope de 2 por proveedor y 2 por entidad; si no hay candidato, se usa el decil vecino y se declara.

**Ceguera.** Los 120 procesos se mezclan al azar y se entregan con un código neutro. Quien prepara la muestra no revisa. Los revisores no conocen la condición de ningún proceso. El 20 % (24 procesos, sorteados) lo revisan dos personas de forma independiente; el acuerdo se mide con el kappa de Cohen y los desacuerdos se resuelven por consenso, que es el valor que entra a la prueba.

**Medida.** Hallazgo = 1 si la guía del anexo B registra al menos un ítem de tipo A con evidencia documental.

**Prueba.** Exacta de Fisher unilateral (priorizados > controles), α = 0,05, con corrección de Holm junto a H2. Potencia de 0,72 a 0,84 para detectar 30 % frente a 10 %.

## 10. Multiplicidad y decisión general

H1 se prueba sola a α = 0,05. H2 y H3 se corrigen con Holm: la de menor valor p se rechaza si p ≤ 0,025 y la otra si p ≤ 0,05. La hipótesis general se considera **respaldada** si se cumplen H1 y al menos una de las secundarias; **parcialmente respaldada** si solo se cumple H1; si H1 no se cumple, el resultado favorece al índice simple, que es la alternativa que se recomienda.

## 11. Análisis descriptivos (no confirmatorios)

Grupos del período reformado; contribución de cada indicador (ajustes que retiran una variable a la vez, semillas 1 a 5, cambio en la recuperación de H1 y en la lista); explicación de los procesos priorizados con valores de Shapley de Isolation Forest y error de reconstrucción por variable del autoencoder; concentración de la lista por proveedor, entidad y año. Ninguno cambia las decisiones de las secciones 7 a 10.

## 12. Desviaciones y reporte

Toda desviación de este documento se informa como tal, con su motivo y su fecha. Se reportan todos los resultados, incluidos los negativos, con tamaños de efecto e intervalos de confianza.

---

## Anexo A. Enmiendas incorporadas

- **Enmienda A (16-oct-2026):** se puntúa desde 2016; debutante con ventana de 365 días; primera vez con la entidad fuera de los modelos por redundante; representación `normal_sup`. Evidencia: verificación de la celda 0 (coincidencia del 100 % con el recálculo desde fechas y RUC) y piloto con 2023.
- **Enmienda B (16-oct-2026):** H2 con percentil dentro de grupo × año y sensibilidad por decil de monto; procesos de 2015 fuera de H2; H3 con tope de 2 procesos por proveedor y por entidad en los dos lados; lista congelada con sus huellas.

## Anexo B. Guía de revisión documental (H3)

Cada revisor abre la ficha del proceso en el portal transaccional del SERCOP y registra, para cada ítem, **Sí / No / No verificable**, con el enlace o la captura que lo respalda. Solo cuentan los hechos visibles en los documentos publicados; no se usan fuentes externas ni el estado actual del proveedor.

**Ítems tipo A (cualquiera marcado "Sí" con evidencia = hallazgo):**

1. Falta en el portal un documento esencial que debería existir según el estado del proceso (pliego, resolución o acta de adjudicación, contrato).
2. El plazo entre la convocatoria y el cierre de ofertas es menor que el mínimo que establece el pliego o la norma vigente para ese procedimiento.
3. Se adjudica a una oferta que no es la de menor precio en un procedimiento donde el precio es el criterio de adjudicación, sin justificación escrita.
4. Se descalifica a todos los demás oferentes, o al único competidor, sin un motivo escrito en el acta.
5. La actividad registrada del proveedor en el portal no guarda relación con el objeto del contrato.
6. El mismo proveedor y la misma entidad tienen otros procesos de objeto similar dentro de 30 días que, sumados, superarían el monto máximo del procedimiento usado.
7. El monto del contrato supera al adjudicado sin un documento que lo respalde.

**Ítems tipo B (se registran, pero no cuentan como hallazgo):** errores de forma, datos incompletos no esenciales, documentos publicados fuera de plazo sin efecto sobre la adjudicación.

Cada proceso se revisa en no más de 30 minutos. Si la ficha no abre o no tiene documentos, se marca "No verificable" en todos los ítems y el proceso se reemplaza por el siguiente de la lista de reserva sorteada con la misma semilla, del mismo lado (priorizado o control).
