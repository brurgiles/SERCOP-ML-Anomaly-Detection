# Base Plan A - Deteccion de anomalias en compras publicas del Ecuador (SERCOP, OCDS)

Generado desde los datos el 2026-10-09 22:58. No editar a mano.

- Corte de descarga de los datos: 2026-09-05
- Universo: 2,785,355 releases OCDS, 2015-2026
- Valor contratado del universo: 67033.0 millones USD
- Base de modelado: 446,677 procesos, 54012.3 millones USD

## Archivos

```
                        archivo          caja                     grano   filas  columnas    MB llave  llave_unica        sha256_16
          planA_procesos_modelo      A nucleo         proceso modelable  446677       147  75.8  ocid         True adb1768ebd2dd83a
              planA_indicadores      A nucleo         proceso modelable  446677        60  30.2  ocid         True ca8d7a8838da235c
            planA_dim_proveedor      A nucleo           proveedor (RUC)   74778        45   3.8   ruc         True 6ca961e876f1e5e5
              planA_dim_entidad      A nucleo             entidad (RUC)    4244        32   0.4   ruc         True eea23963f57a11eb
                 planA_universo   B auditoria              release OCDS 2785355       143 266.2  ocid         True ea0466ff8a66f59f
                 planA_catalogo B descriptivo       proceso de catalogo 2285455       143 173.3  ocid         True d20dda23afda5d5c
planA_excluidos_solo_planeacion   C evidencia          proceso excluido   32161       143   0.3  ocid         True 8629b61c9dbff20e
      planA_excluidos_sin_monto   C evidencia          proceso excluido   16807       143   0.2  ocid         True 4654abeddce98c08
  planA_excluidos_sin_proveedor   C evidencia          proceso excluido    4255       143   0.7  ocid         True 0cf19c81bc335011
           planA_validacion_sri  C validacion proveedor marcado por SRI      15        12   0.0   ruc         True e5e0ab288826f537
```

## Como se unen

- `planA_procesos_modelo` <-- ocid --> `planA_indicadores`  (1 a 1, verificado)
- `planA_procesos_modelo.proveedor_ruc_final` --> `planA_dim_proveedor.ruc`
- `planA_procesos_modelo.entidad_ruc` --> `planA_dim_entidad.ruc`

## Reglas de uso

1. `monto_final` es la suma de las adjudicaciones del proceso. Nunca usar `monto_tender`.
2. `anio_proceso` es el año de inicio del periodo de ofertas, con retroceso al año del codigo
   del proceso y luego al del release; `anio_proceso_origen` declara de donde sale cada valor.
   `anio_publicacion_release` NO es el año del proceso: acierta el año del codigo solo en el
   77,49% de los casos frente al 99,36% del inicio del tender.
3. LAS SERIES TEMPORALES SE CORTAN EN 2024. Por el retraso de publicacion (mediana 106 a 147
   dias desde 2021, p95 sobre 450) los años 2025 y 2026 estan incompletos y sus totales no son
   comparables. El modelo si puede usar todas las filas.
4. `planA_validacion_sri` no entra como variable en ningun modelo: es validacion externa y vive
   aparte para que no pueda filtrarse a una tabla de features.
5. Prohibido usar columnas de estado administrativo actual (SRI, Superintendencia) para explicar
   procesos pasados: eso es anacronismo y rompe el punto en el tiempo.
6. Las 56 columnas de red (`red_`, `cob_`, `com_`, `rep_`, `grupo_`, `idx_`) fueron eliminadas:
   corresponden al item #48 del catalogo, que es de otro grupo.
7. Los nueve `pct_` son rangos percentiles calculados SOLO sobre filas con dato; la ausencia la
   carga la indicadora `falta_*`. `pct_poca_concurrencia` satura en 0.8315 por los empates de
   los procesos con un solo oferente.
8. `duracion_dias_imputada` es solo para estadistica descriptiva (19,0% de valores sinteticos) y
   lleva su bandera `duracion_imputada`. Para la tesis usar `ind_duracion_contrato_dias`
   declarando su cobertura.
9. `es_multilote` y `n_awards` son variables de estratificacion, no de anomalia.
10. Toda cifra con cola larga se reporta con mediana, nunca con promedio.

## Definiciones verificadas por reproduccion

- `ind_monto_sobre_capital`: monto adjudicado / capital social; reproducida al 100%
- `ind_fraccionamiento_monto_30d`: suma del monto del mismo par entidad-proveedor y mismo CPC5 en los 30 dias anteriores, sin el dia del proceso; reproducida al 100%
- `ind_cuota_prov_en_entidad_12m`: monto del par / monto de la entidad, 365 dias anteriores; reproducida al 100% en las filas discriminantes
- `ind_cuota_procesos_12m`: procesos del par / procesos de la entidad, 365 dias anteriores; reproducida al 100% en las filas discriminantes
- `ind_desv_precio_unit_z`: z robusto del ln del precio unitario del item en su grupo de referencia de precio; NO depende de monto_final
- `monto_final`: suma de las adjudicaciones del proceso

- Grupo comparable: familia x periodo normativo, con descenso a familia y luego a global cuando
  el grupo tiene menos de 30 casos con dato.
- Referencia de precio: CPC5 x unidad x familia x año, con retroceso a CPC5, CPC3 y familia,
  minimo 30 procesos.
- Ventana de historial: 365 dias anteriores, sin incluir el dia del proceso.
- Ventana de fraccionamiento: 30 dias anteriores, mismo par entidad-proveedor y mismo CPC5.

## Completitud por archivo

- **planA_procesos_modelo**: 147 columnas | 64 completas | 51 con faltantes | 9 constantes | 0 sin un solo dato
- **planA_indicadores**: 60 columnas | 31 completas | 24 con faltantes | 0 constantes | 0 sin un solo dato
- **planA_dim_proveedor**: 45 columnas | 13 completas | 14 con faltantes | 1 constantes | 0 sin un solo dato
- **planA_dim_entidad**: 32 columnas | 10 completas | 12 con faltantes | 2 constantes | 0 sin un solo dato
- **planA_universo**: 143 columnas | 11 completas | 101 con faltantes | 1 constantes | 0 sin un solo dato
- **planA_catalogo**: 143 columnas | 45 completas | 52 con faltantes | 17 constantes | 9 sin un solo dato
- **planA_excluidos_solo_planeacion**: 143 columnas | 4 completas | 2 con faltantes | 7 constantes | 130 sin un solo dato
- **planA_excluidos_sin_monto**: 143 columnas | 5 completas | 2 con faltantes | 6 constantes | 130 sin un solo dato
- **planA_excluidos_sin_proveedor**: 143 columnas | 43 completas | 22 con faltantes | 16 constantes | 45 sin un solo dato
- **planA_validacion_sri**: 12 columnas | 10 completas | 0 con faltantes | 2 constantes | 0 sin un solo dato

El detalle columna por columna esta en `diccionario_columnas.csv` y en los
`perfil_nulos_<archivo>.csv`. Las enmiendas de version, con fecha, motivo y huella, en
`especificacion_indicadores.json`. El tablero de control, en `tablero_de_control.csv`. Las
versiones anteriores de cada archivo se conservan en `_version_1_historico\`: no se borra nada.