# ============ Plan A · Extracción complementaria desde el JSON crudo ============
# Trae lo que la base no tiene y la parte C confirmó que existe en el JSON:
#   fecha de adjudicación, fecha de firma, período del contrato y de adjudicación,
#   fin de preguntas, precio unitario y cantidad del ítem principal, y ofertas (bids).
# Tarda del orden de 10 a 15 minutos sobre los 19 GB. Guarda un parquet POR AÑO, así que
# si se interrumpe, al volver a correrlo retoma donde quedó en vez de empezar de cero.
import os, glob, time
import pandas as pd, duckdb
try:
    import ijson
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'ijson']); import ijson

os.chdir(r'C:\SERCOP_FINAL')
R, PARC = '03_resultados', '03_resultados/_parciales_json'
os.makedirs(PARC, exist_ok=True)
con = duckdb.connect(); con.sql("SET preserve_insertion_order=false")

def prefijo_de(ruta):
    """Los archivos son paquetes OCDS: unos empiezan con '[' y otros con '{'."""
    with open(ruta, 'rb') as fh:
        while True:
            c = fh.read(1)
            if not c: return 'releases.item'
            if not c.isspace():
                return 'item.releases.item' if c == b'[' else 'releases.item'

def lista(v):
    """Tolera las listas que vienen mal serializadas como objeto con claves numéricas."""
    if isinstance(v, list): return [x for x in v if isinstance(x, dict)]
    if isinstance(v, dict) and v and all(str(k).isdigit() for k in v):
        return [x for x in v.values() if isinstance(x, dict)]
    return []

def g(d, *ruta):
    for k in ruta:
        if not isinstance(d, dict): return None
        d = d.get(k)
    return d

def num(v):
    try: return float(v)
    except (TypeError, ValueError): return None

def fila(rel):
    t   = rel.get('tender') if isinstance(rel.get('tender'), dict) else {}
    aws = lista(rel.get('awards')); cts = lista(rel.get('contracts'))
    # ítem principal = el de mayor valor (precio unitario por cantidad)
    items = lista(t.get('items')) or [i for a in aws for i in lista(a.get('items'))]
    mejor, mejor_v = None, -1.0
    for it in items:
        pu, q = num(g(it, 'unit', 'value', 'amount')), num(it.get('quantity'))
        v = (pu or 0) * (q if q is not None else 1)
        if v > mejor_v: mejor, mejor_v = it, v
    bids = rel.get('bids')
    det  = lista(g(bids, 'details')) if isinstance(bids, dict) else lista(bids)
    vals = [x for x in (num(g(b, 'value', 'amount')) for b in det) if x is not None]
    fechas_adj   = [a.get('date') for a in aws if a.get('date')]
    fechas_firma = [c.get('dateSigned') for c in cts if c.get('dateSigned')]
    return {
        'ocid': rel.get('ocid'),
        'j_fecha_adjudicacion': min(fechas_adj) if fechas_adj else None,
        'j_fecha_firma':        min(fechas_firma) if fechas_firma else None,
        'j_contrato_inicio':    g(cts[0], 'period', 'startDate') if cts else None,
        'j_contrato_fin':       g(cts[0], 'period', 'endDate') if cts else None,
        'j_contrato_monto':     num(g(cts[0], 'value', 'amount')) if cts else None,
        'j_periodo_adj_inicio': g(t, 'awardPeriod', 'startDate'),
        'j_periodo_adj_fin':    g(t, 'awardPeriod', 'endDate'),
        'j_periodo_tender_ini': g(t, 'tenderPeriod', 'startDate'),
        'j_periodo_tender_fin': g(t, 'tenderPeriod', 'endDate'),
        'j_fin_preguntas':      g(t, 'enquiryPeriod', 'endDate'),
        'j_item_cpc':           str(g(mejor, 'classification', 'id')) if g(mejor, 'classification', 'id') else None,
        'j_item_cantidad':      num(mejor.get('quantity')) if mejor else None,
        'j_item_precio_unit':   num(g(mejor, 'unit', 'value', 'amount')) if mejor else None,
        'j_item_unidad':        g(mejor, 'unit', 'name') if mejor else None,
        'j_n_items':            len(items),
        'j_n_ofertas':          len(det) if det else None,
        'j_oferta_min':         min(vals) if vals else None,
        'j_oferta_max':         max(vals) if vals else None,
    }

FECHAS = ('j_fecha', 'j_contrato_inicio', 'j_contrato_fin', 'j_periodo', 'j_fin')
archivos = sorted(glob.glob('00_json_crudo/releases_*.json'))
archivos = [a for a in archivos
            if not (a.endswith('releases_2024.json') and os.path.exists(a.replace('.json', '_reparado.json')))]
print(f'{len(archivos)} archivos por procesar\n')
for ruta in archivos:
    base = os.path.basename(ruta).replace('.json', '')
    sal  = f'{PARC}/{base}.parquet'
    if os.path.exists(sal):
        print(f'  {base}: ya estaba hecho, se omite'); continue
    t0, filas = time.time(), []
    with open(ruta, 'rb') as fh:
        for rel in ijson.items(fh, prefijo_de(ruta)):
            if isinstance(rel, dict): filas.append(fila(rel))
    d = pd.DataFrame(filas); del filas
    for c in [c for c in d.columns if c.startswith(FECHAS)]:
        d[c] = pd.to_datetime(d[c], errors='coerce', utc=True).dt.tz_localize(None)
    d.to_parquet(sal, index=False)
    print(f'  {base}: {len(d):,} procesos ({time.time()-t0:.0f} s)'); del d

J = pd.concat([pd.read_parquet(f) for f in sorted(glob.glob(f'{PARC}/*.parquet'))], ignore_index=True)
dup = int(J.ocid.duplicated().sum())
print(f'\nextraídos: {len(J):,} filas | ocid repetidos: {dup}')
if dup: J = J.drop_duplicates('ocid', keep='first'); print('  se dejó la primera aparición de cada ocid')
SALIDA = f'{R}/c15_complemento_json.parquet'
J.to_parquet(SALIDA, index=False); del J
print(f'  -> {SALIDA}')

# ---------- Comprobación contra el universo versión 2 ----------
UNI = 'plan_A/planA_universo_v2.parquet'
if not os.path.exists(UNI): UNI = f'{R}/final_procesos.parquet'
con.sql(f"CREATE OR REPLACE VIEW u AS SELECT * FROM read_parquet('{UNI}')")
con.sql(f"CREATE OR REPLACE VIEW j AS SELECT * FROM read_parquet('{SALIDA}')")
n_u, n_un = con.sql("SELECT (SELECT count(*) FROM u), (SELECT count(*) FROM u LEFT JOIN j USING (ocid))").fetchone()
sin_par = con.sql("SELECT count(*) FROM u ANTI JOIN j USING (ocid)").fetchone()[0]
print(f'\nuniverso: {n_u:,} | tras la unión: {n_un:,} '
      f'({"no duplica" if n_u == n_un else "DUPLICA, revisar"}) | sin fila en el JSON: {sin_par:,}')

fam = 'planA_familia' if 'planA_familia' in [c[0] for c in con.sql("DESCRIBE u").fetchall()] else 'familia_procedimiento'
campos = ['j_fecha_adjudicacion','j_fecha_firma','j_contrato_fin','j_contrato_monto','j_periodo_tender_fin',
          'j_fin_preguntas','j_item_cpc','j_item_precio_unit','j_item_cantidad','j_n_ofertas']
sel = ', '.join(f'round(100.0*count({c})/count(*), 1) AS {c}' for c in campos)
print('\n% con dato, por familia (universo de modelado):')
print(con.sql(f"""SELECT {fam} AS familia, count(*) AS procesos, {sel}
                  FROM u LEFT JOIN j USING (ocid)
                  WHERE planA_segmento = 'S3_modelo_sin_catalogo'
                  GROUP BY 1 ORDER BY procesos DESC""").df().to_string(index=False))

print('\nPlazos en días (mediana) y controles de coherencia de fechas:')
print(con.sql(f"""
  SELECT {fam} AS familia,
     median(date_diff('day', fecha_inicio_tender, j_fecha_adjudicacion)) AS inicio_a_adjudicacion,
     median(date_diff('day', j_fecha_adjudicacion, j_fecha_firma))       AS adjudicacion_a_firma,
     median(date_diff('day', j_contrato_inicio, j_contrato_fin))         AS duracion_contrato,
     median(date_diff('day', j_periodo_tender_ini, j_periodo_tender_fin)) AS plazo_de_ofertas,
     count(*) FILTER (WHERE j_fecha_adjudicacion < fecha_inicio_tender)  AS adj_antes_del_inicio,
     count(*) FILTER (WHERE j_fecha_firma < j_fecha_adjudicacion)        AS firma_antes_de_la_adj,
     count(*) FILTER (WHERE j_contrato_fin < j_contrato_inicio)          AS contrato_al_reves
  FROM u LEFT JOIN j USING (ocid)
  WHERE planA_segmento = 'S3_modelo_sin_catalogo'
  GROUP BY 1 ORDER BY 1""").df().to_string(index=False))

print('\nPrecio unitario: ¿sirve para comparar dentro del CPC?')
print(con.sql(f"""
  SELECT {fam} AS familia, count(*) procesos,
     round(100.0*count(j_item_precio_unit)/count(*),1) pct_con_precio_unitario,
     round(100.0*count(j_item_cpc)/count(*),1) pct_con_cpc,
     count(DISTINCT substr(j_item_cpc,1,5)) grupos_cpc5,
     round(median(j_item_precio_unit),2) precio_unitario_mediano,
     count(*) FILTER (WHERE j_item_precio_unit <= 0) precio_cero_o_negativo
  FROM u LEFT JOIN j USING (ocid)
  WHERE planA_segmento = 'S3_modelo_sin_catalogo'
  GROUP BY 1 ORDER BY 2 DESC""").df().to_string(index=False))
print('\nPega toda la salida. Con esto cierro los indicadores de precio y de plazos.')