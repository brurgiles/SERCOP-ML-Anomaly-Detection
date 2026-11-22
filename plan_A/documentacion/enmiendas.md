
## Enmienda v6.1 — 2026-10-10
- Motivo: `percent_rank()` asigna a un bloque de empates el percentil de su primer
  miembro, por lo que los rangos con masa en el extremo anomalo no alcanzaban 0,95.
- Correccion 1: todos los rangos pasan a `cume_dist()` (funcion de distribucion
  empirica). Rangos vigentes: pct_precio_alto, pct_monto_capital, pct_proveedor_nuevo, pct_plazo_corto, pct_firma_rapida, pct_fraccionamiento_pos, pct_cuota_pos, pct_recurrencia_pos.
- Correccion 2: las variables con mas del 5% del dominio en el valor extremo de su
  grupo dejan de representarse como rango y pasan a diferencia contra la mediana del
  grupo comparable: dif_concurrencia_grupo.
- Se retiran definitivamente: pct_poca_concurrencia, pct_fraccionamiento,
  pct_cuota_12m, pct_recurrencia_par, pct_concurrencia_pos.
- Firma planA_indicadores.parquet = 65741da3b170aaae

## Enmienda v6.2 — 2026-10-10
- Motivo: con variables discretas, percent_rank subestima el percentil de un
  bloque de empates y cume_dist lo sobreestima, cada uno por media anchura de
  bloque. v6 encendia 2,49% y 0,86% en plazo y firma; v6.1 encendio 11,38% y 10,24%.
- Correccion: todos los rangos usan el percentil a mitad de salto
  (mid-distribution function), cume_dist - b/(2n), de media exactamente 0,5.
- Regla de conservacion: media 0,5000, maximo >= 0,95 y encendido entre 3,5% y 8%.
- Rangos vigentes: pct_precio_alto, pct_monto_capital, pct_proveedor_nuevo, pct_plazo_corto, pct_firma_rapida, pct_fraccionamiento_pos, pct_cuota_pos, pct_recurrencia_pos.
- Convertidas a diferencia contra la mediana del grupo: dif_concurrencia_grupo.
- Las copias de version salen de plan_A/ a plan_A/_versiones/; el manifiesto
  vuelve a listar solo los archivos de entrega.
- Firma planA_indicadores.parquet = dc87f4b8e1282d7f

## Enmienda tipologia institucional — 2026-10-10
- planA_dim_entidad.parquet gana cuatro columnas: tipo_entidad,
  tipo_entidad_origen (manual / patron / residuo), entidad_nombre_canonico
  (el nombre del proceso mas reciente del RUC) y n_nombres_distintos.
- La tipologia se asigna por RUC, no por nombre: un mismo RUC aparece con
  nombres distintos segun el anio (MIES -> Ministerio de Desarrollo Humano;
  Servicio Nacional de Gestion de Riesgos -> Gestion de Riesgos), de modo que
  contar entidades por nombre infla el numero de entidades.
- Dos asignaciones verificadas una por una contra el SRI y el portal:
  1768011230001 DIGMAT = Direccion General del Material (Armada) -> Seguridad
  y defensa; 1360066490001 Coordinacion Zonal 4 = Ministerio de Educacion ->
  Educacion. Existen doce coordinaciones zonales 4 distintas, una por ministerio.
- La clasificacion es heuristica sobre el nombre salvo las verificadas, y debe
  declararse como tal: sirve para formar grupos comparables, no es dato oficial.
- Firma planA_dim_entidad.parquet = 8419e2a0eaf9da69

## Enmienda tipologia institucional (definitiva) — 2026-10-10
- planA_dim_entidad.parquet gana: tipo_entidad, tipo_entidad_origen
  (manual/patron/residuo), tipo_entidad_regla (el patron exacto que clasifico,
  para auditoria), entidad_nombre_canonico y n_nombres_distintos.
- La tipologia se asigna por RUC y se evalua contra TODOS los nombres historicos
  del RUC, no contra uno elegido: 335 RUC tienen mas de un nombre y en al menos
  un caso (1360070840001) el nombre elegido decidia mal la clasificacion.
- Dos asignaciones verificadas una por una: 1768011230001 DIGMAT = Direccion
  General del Material (Armada) -> Seguridad y defensa; 1360066490001
  Coordinacion Zonal 4 = Ministerio de Educacion -> Educacion.
- Criterio declarado: las entidades se agrupan por su PERFIL DE COMPRA, no por
  su dependencia administrativa. Por eso las empresas publicas municipales de
  agua y electricidad son 'Empresa publica' y no 'Gobierno local', y los cuerpos
  de bomberos son 'Gobierno local'.
- Se retiro el patron \bSA\b: capturaba empresas privadas. Las empresas estatales
  que terminan en S.A. se nombran explicitamente.
- Clasificacion heuristica sobre el nombre salvo las verificadas; se declara como
  tal. Sirve para formar grupos comparables, no es dato oficial.
- Firma planA_dim_entidad.parquet = c8765d64bbd77a43

## Tipologia institucional: cierre — 2026-10-10
- Las reglas dejan de vivir en codigo y pasan a documentacion/reglas_tipologia.json
  (version 1.0), que es la fuente unica: la celda lo escribe y lo lee.
- Criterio: Las entidades se agrupan por su PERFIL DE COMPRA, no por su dependencia administrativa. Se evalua contra todos los nombres historicos del RUC y gana la primera regla de la lista que coincida con cualquiera de ellos.
- Criterio de parada declarado: el residuo no pasa del 1% del monto y ninguna
  entidad sin clasificar pasa del 0,05% del monto total.
- Residuo alcanzado: 627 entidades, 2.19% de
  los procesos, 0.6% del monto; la mayor sin clasificar es el
  0.03% del monto total.
- La clasificacion se evalua contra todos los nombres historicos del RUC.
- Hallazgo: 303 de 3774 RUC compradores aparecen tambien como proveedores. La
  revision de los mayores muestra que son empresas publicas universitarias y de
  institutos creadas para VENDER servicios al Estado, no un defecto de ids de
  buyer/parties. Quedan tres casos menores (0,4 MM) donde el campo comprador
  trae algo que no es un comprador.
- Firma planA_dim_entidad.parquet = 82c23da032e4f151
