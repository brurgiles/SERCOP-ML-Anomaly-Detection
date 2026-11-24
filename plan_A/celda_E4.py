# CUADERNO 20 · CELDA E4. Amontonamiento con los techos oficiales (enmienda D, sección 5.6; descriptivo, solo lectura)
#   Pregunta: ¿el amontonamiento de presupuestos referenciales bajo los techos legales se mantiene con los valores
#   oficiales de cada año y al separar obras, bienes y servicios y consultoría?
#   Techo = coeficiente de la LOSNCP x Presupuesto Inicial del Estado (PIE) del año. La tabla de techos (abajo) se
#   transcribió de las páginas oficiales del SERCOP "Montos de contratación pública AAAA" antes de calcular nada;
#   la celda comprueba que cada valor publicado sea igual al coeficiente por el PIE.
#   Reglas de la Tabla 7 del anteproyecto: último 1 % del techo frente a la densidad media de los tramos de 0,2 %
#   entre el 90 % y el 99 %; ventana del 2 % bajo el techo frente a sus tramos vecinos de 2 % (desde el 80 %);
#   umbrales ficticios al 30, 40, 50, 60 y 70 %. Desglose por año. Procesos iniciados antes del 7-oct-2025.
#   Presupuesto referencial = monto_tender (si falta, monto_final), igual que la Tabla 7.
#   Objeto: categoria_principal (works = obras; goods o services = bienes y servicios); lista corta = consultoría.
#   No ajusta modelos, no usa la muestra de H3 ni planA_validacion_sri, no lee columnas de RUC ni imprime procesos.
#   Escribe en una carpeta nueva modelos\AAAAMMDD_HHMM_expD_E4\ y no sobrescribe nada.
import hashlib, json, platform, unicodedata
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd, duckdb

BASE = Path(r"C:\SERCOP_FINAL")
IX = BASE / "plan_A" / "planA_indicadores.parquet"
PM = BASE / "plan_A" / "planA_procesos_modelo.parquet"
ENM_D = BASE / "enmiendas" / "enmienda_2026-11-10_d.json"
ESPERADAS = {IX: "dc87f4b8e1282d7f", ENM_D: "55b01c16035d3b2b"}
CORTE_REFORMA = pd.Timestamp("2025-10-07")       # reforma de la LOSNCP en el Registro Oficial
INICIO_LOIP = pd.Timestamp("2025-06-26")         # vigencia de la Ley Orgánica de Integridad Pública (eliminó menor cuantía y cotización)
FAMILIAS = ["Menor cuantia", "Cotizacion", "Lista corta"]

# ---------------- tabla oficial (transcrita el 22-nov-2026 de portal.compraspublicas.gob.ec/sercop/) ----------------
URL = "https://portal.compraspublicas.gob.ec/sercop/"
PIE = {   # año: (PIE en USD, documento fuente, nota)
    2015: ("36317117010.35", "SERCOP, Montos de contratación pública 2015 (página web)", ""),
    2016: ("29835098320.79", "SERCOP, Montos de contratación pública 2016 (página web)", ""),
    2017: ("29835098320.79", "SERCOP, Montos de contratación pública 2017 (página web)", "mismo PIE y montos que 2016"),
    2018: ("34853371653.72", "SERCOP, Montos de contratación pública 2018 (página web)", ""),
    2019: ("35529394461.72", "SERCOP, Montos de contratación pública 2019 (página web)", ""),
    2020: ("35498420637.20", "SERCOP, Montos de contratación pública 2020 (página web)", "PIE leído en la sección BID de la página"),
    2021: ("32080363387.48", "SERCOP, Montos de contratación pública 2021 (página web)", "la página lo llama PGE"),
    2022: ("33899734759.85", "SERCOP, Montos de contratación pública 2022 (página web)", "la página lista los coeficientes"),
    2023: ("31502865593.76", "SERCOP, montos_contratacion_2023.pdf (wp-content/uploads/2023/01)", ""),
    2024: ("33296819775.31", "SERCOP, montos_contratacion_2024.pdf (wp-content/uploads/2024/01)", ""),
    2025: ("36063017083.08", "SERCOP, INFOGRAFIA-MONTOS-copia-1.pdf (wp-content/uploads/2025/08), régimen LOIP",
           "montos de 2025 anteriores a la LOIP derivados como coeficiente x PIE: la infografía de enero es imagen"),
}
COEF = {  # (familia, objeto): coeficiente del PIE (LOSNCP anterior a la reforma de 2025)
    ("Menor cuantia", "bienes_servicios"): "0.000002",
    ("Menor cuantia", "obras"): "0.000007",
    ("Cotizacion", "bienes_servicios"): "0.000015",
    ("Cotizacion", "obras"): "0.00003",
    ("Lista corta", "consultoria"): "0.000015",
}
PUBLICADO = {  # valores leídos en las fuentes (USD); los que faltan se derivan y se rotulan
    2015: {"mc_bs": "72634.23", "co_bs": "544756.76", "mc_ob": "254219.82", "co_ob": "1089513.51", "lc": "544756.76"},
    2016: {"mc_bs": "59670.20", "co_bs": "447526.47", "mc_ob": "208845.69", "co_ob": "895052.95", "lc": "447526.47"},
    2017: {"mc_bs": "59670.20", "co_bs": "447526.47", "mc_ob": "208845.69", "co_ob": "895052.95", "lc": "447526.47"},
    2018: {"mc_bs": "69706.74", "co_bs": "522800.57", "mc_ob": "243973.60", "co_ob": "1045601.15", "lc": "522800.57"},
    2019: {"mc_bs": "71058.79", "co_bs": "532940.92", "mc_ob": "248705.76", "co_ob": "1065881.83", "lc": "532940.92"},
    2020: {"mc_bs": "70996.84", "mc_ob": "248488.94", "co_ob": "1064952.62"},
    2021: {"mc_bs": "64160.73", "co_bs": "481205.45", "mc_ob": "224562.54", "co_ob": "962410.90", "lc": "481205.45"},
    2022: {"mc_bs": "67799.47", "co_bs": "508496.02", "mc_ob": "237298.14", "co_ob": "1016992.04", "lc": "508496.02"},
    2023: {"mc_bs": "63005.73", "co_bs": "472542.98", "mc_ob": "220520.06", "co_ob": "945085.97", "lc": "472542.98"},
    2024: {"mc_bs": "66593.64", "co_bs": "499452.30", "mc_ob": "233077.74", "co_ob": "998904.59", "lc": "499452.30"},
    2025: {},
}
CLAVE = {("Menor cuantia", "bienes_servicios"): "mc_bs", ("Menor cuantia", "obras"): "mc_ob",
         ("Cotizacion", "bienes_servicios"): "co_bs", ("Cotizacion", "obras"): "co_ob", ("Lista corta", "consultoria"): "lc"}
PAGINA = {a: URL + f"montos-de-contratacion-publica-{a}/" for a in PIE}

from decimal import Decimal, ROUND_HALF_UP
filas_t = []
for anio, (pie, fuente, nota) in PIE.items():
    for (fam, obj), coef in COEF.items():
        calc = (Decimal(pie) * Decimal(coef)).quantize(Decimal("0.01"), ROUND_HALF_UP)
        pub = PUBLICADO[anio].get(CLAVE[(fam, obj)])
        if pub is not None and Decimal(pub) != calc:
            raise SystemExit(f"{anio} {fam} {obj}: publicado {pub} distinto de coeficiente x PIE {calc}. Para y avisa. No se escribió nada.")
        filas_t.append(dict(anio=anio, familia=fam, objeto=obj, coeficiente=coef, pie=pie, techo=float(calc),
                            origen_valor="publicado" if pub is not None else "derivado (coeficiente x PIE oficial)",
                            fuente=fuente, pagina=PAGINA[anio], nota=nota))
TECHOS = pd.DataFrame(filas_t)

# ---------------- verificaciones y datos ----------------
def sha(r):
    h = hashlib.sha256()
    with open(r, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()
HUELLAS = {}
for ruta, esperada in ESPERADAS.items():
    HUELLAS[ruta.name] = sha(ruta)
    if not HUELLAS[ruta.name].startswith(esperada):
        raise SystemExit(f"{ruta.name} no tiene la huella registrada ({esperada}): para y avisa. No se escribió nada.")
HUELLAS[PM.name] = sha(PM)                      # se registra; no hay huella esperada para este archivo
try:
    CODIGO = _ih[-1]
except NameError:
    CODIGO = open(__file__, encoding="utf-8").read()
HUELLA_CODIGO = hashlib.sha256(CODIGO.encode("utf-8")).hexdigest()

con = duckdb.connect()
cols_ix = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{IX.as_posix()}')").fetchall()]
cols_pm = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{PM.as_posix()}')").fetchall()]
falta = [c for c in ["ocid", "familia"] if c not in cols_ix] + \
        [c for c in ["ocid", "monto_tender", "monto_final", "categoria_principal"] if c not in cols_pm]
if "fecha_inicio_tender" not in cols_ix and "fecha_inicio_tender" not in cols_pm:
    falta.append("fecha_inicio_tender")
if falta:
    raise SystemExit(f"Faltan columnas: {falta}. Para y avisa. No se escribió nada.")
fch_de = "ix" if "fecha_inicio_tender" in cols_ix else "pm"
d = con.execute(f"""
    SELECT ix.ocid, ix.familia, {fch_de}.fecha_inicio_tender AS f,
           pm.monto_tender, pm.monto_final, pm.categoria_principal
    FROM read_parquet('{IX.as_posix()}') ix
    JOIN read_parquet('{PM.as_posix()}') pm ON pm.ocid = ix.ocid
    WHERE ix.familia IN ('Menor cuantia', 'Cotizacion', 'Lista corta')
""").df()
fecha = pd.to_datetime(d["f"], errors="coerce")
try:
    if fecha.dt.tz is not None:
        fecha = fecha.dt.tz_convert("America/Guayaquil").dt.tz_localize(None)
except AttributeError:
    pass
d["fecha"] = fecha
d["anio"] = fecha.dt.year
mt = pd.to_numeric(d["monto_tender"], errors="coerce")
mf = pd.to_numeric(d["monto_final"], errors="coerce")
d["pliego"] = mt.where(mt > 0, mf)
d["pliego_de"] = np.where(mt > 0, "monto_tender", np.where(mf > 0, "monto_final", "sin monto"))

def sin_tildes(x):
    return unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower().strip()
cat = d["categoria_principal"].map(lambda x: None if pd.isna(x) else sin_tildes(x))
obj = np.select([cat.fillna("").str.contains("work|obra"), cat.fillna("").str.contains("good|bien|servic")],
                ["obras", "bienes_servicios"], default="sin_objeto")
d["objeto"] = np.where(d["familia"] == "Lista corta", "consultoria", obj)

n_total = len(d)
u = d[(d["fecha"] < CORTE_REFORMA) & d["anio"].between(2015, 2025) & (d["pliego"] > 0)].copy()
U0 = len(u)
if U0 == 0:
    raise SystemExit("Universo vacío: para y avisa. No se escribió nada.")

RUN = datetime.now().strftime("%Y%m%d_%H%M") + "_expD_E4"
DIR = BASE / "modelos" / RUN
DIR.mkdir(exist_ok=False)
LINEAS = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s); LINEAS.append(s)
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
fmt = lambda n: f"{n:,}".replace(",", ".")

say(f"Corrida {RUN} | descriptivo, enmienda D (5.6, E4) | indicadores {HUELLAS[IX.name][:16]} | "
    f"procesos_modelo {HUELLAS[PM.name][:16]} | código {HUELLA_CODIGO[:16]}")
say(f"Tabla de techos: {len(TECHOS)} combinaciones (11 años x 5); publicadas {int((TECHOS.origen_valor == 'publicado').sum())}, "
    f"derivadas {int((TECHOS.origen_valor != 'publicado').sum())}; todas las publicadas = coeficiente x PIE al centavo.")
say(f"Procesos de menor cuantía, cotización y lista corta: {fmt(n_total)}; iniciados entre 2015 y el 6-oct-2025 con monto: {fmt(U0)} "
    f"(pliego de monto_tender {fmt(int((u.pliego_de == 'monto_tender').sum()))}, de monto_final {fmt(int((u.pliego_de == 'monto_final').sum()))})")
say("\nObjeto según categoria_principal (procesos del universo):")
say(pd.crosstab(u["familia"], u["objeto"], margins=True, margins_name="total").to_string())
say("Valores crudos de categoria_principal: " +
    ", ".join(f"{k}={fmt(v)}" for k, v in u["categoria_principal"].fillna("(nulo)").astype(str).value_counts().head(8).items()))

u = u.merge(TECHOS[["anio", "familia", "objeto", "techo", "origen_valor"]], on=["anio", "familia", "objeto"], how="left")
u["razon"] = u["pliego"] / u["techo"]
con_techo = u["techo"].notna()
say(f"\nCon techo oficial: {fmt(int(con_techo.sum()))}; sin objeto identificado (fuera del análisis oficial): {fmt(int((~con_techo).sum()))}")

# techo estimado de la Tabla 7 (máximo observado por familia y año), para comparar
u["techo_est"] = u.groupby(["familia", "anio"])["pliego"].transform("max")
u["razon_est"] = u["pliego"] / u["techo_est"]

COMBOS = [("Menor cuantia", "bienes_servicios"), ("Menor cuantia", "obras"), ("Cotizacion", "bienes_servicios"),
          ("Cotizacion", "obras"), ("Lista corta", "consultoria")]

def medidas(r):
    """r: razones pliego/techo de un conjunto. Devuelve las tres medidas de la Tabla 7."""
    r = r[(r > 0)]
    sobre = int((r > 1.0000001).sum())
    r = r[r <= 1.0000001].clip(upper=0.999999)
    b02 = np.floor(r / 0.002) * 0.002
    base_bins = [round(0.90 + 0.002 * k, 3) for k in range(45)]          # 90,0 % a 98,8 %
    c02 = b02.round(3).value_counts()
    base = float(np.mean([c02.get(b, 0) for b in base_bins]))
    obs1 = int((r >= 0.99).sum()); esp1 = base * 5
    b2 = (np.floor(r / 0.02) * 0.02).round(2).value_counts()
    vec = [b2.get(round(0.80 + 0.02 * k, 2), 0) for k in range(9)]       # 80 % a 96 %
    ult2 = int((r >= 0.98).sum())
    return dict(procesos=int(len(r)) + sobre, sobre_el_techo=sobre, ultimo_1pct=obs1,
                esperados_1pct=round(esp1, 1), exceso_1pct=round(obs1 / esp1, 2) if esp1 > 0 else np.nan,
                sobran_1pct=int(round(obs1 - esp1)), ventana_2pct=ult2, vecinos_2pct=round(float(np.mean(vec)), 1),
                exceso_2pct=round(ult2 / np.mean(vec), 2) if np.mean(vec) > 0 else np.nan)

def placebo(r):
    r = r[(r > 0) & (r <= 1.0000001)].clip(upper=0.999999)
    b2 = (np.floor(r / 0.02) * 0.02).round(2).value_counts()
    out = {}
    for c in [0.30, 0.40, 0.50, 0.60, 0.70, 0.98]:
        tramo = b2.get(round(c, 2), 0)
        vec = [b2.get(round(c - 0.02 * k, 2), 0) for k in range(1, 10)]
        out[("real_" if c == 0.98 else "ficticio_") + f"{int(c * 100)}"] = round(tramo / np.mean(vec), 2) if np.mean(vec) > 0 else np.nan
    return out

# (A) total 2015 a 6-oct-2025, techo oficial
filas_a = []
for fam, ob in COMBOS:
    s = u[(u.familia == fam) & (u.objeto == ob)]
    filas_a.append(dict(familia=fam, objeto=ob, techo="oficial", **medidas(s["razon"]), **placebo(s["razon"])))
for fam in FAMILIAS:                                      # Tabla 7 reproducida: techo estimado, objetos juntos
    s = u[u.familia == fam]
    filas_a.append(dict(familia=fam, objeto="todos", techo="estimado (Tabla 7)", **medidas(s["razon_est"]), **placebo(s["razon_est"])))
A = pd.DataFrame(filas_a)
A.to_csv(DIR / "E4_total.csv", index=False, encoding="utf-8-sig")
say("\n(A) Último 1 % y ventana del 2 % bajo el techo, 2015 a 6-oct-2025")
say(A[["familia", "objeto", "techo", "procesos", "sobre_el_techo", "ultimo_1pct", "esperados_1pct", "exceso_1pct",
       "sobran_1pct", "ventana_2pct", "vecinos_2pct", "exceso_2pct"]].to_string(index=False))
say("\n(B) Control: cociente de la ventana de 2 % frente a sus 9 tramos vecinos, en umbrales ficticios y en el real")
say(A[["familia", "objeto", "techo"] + [c for c in A.columns if c.startswith(("ficticio_", "real_"))]].to_string(index=False))

# (C) por año (2025 dividido en antes de la LOIP y durante la LOIP)
u["tramo_anio"] = u["anio"].astype("Int64").astype(str)
m25 = u["anio"] == 2025
u.loc[m25 & (u["fecha"] < INICIO_LOIP), "tramo_anio"] = "2025 antes LOIP"
u.loc[m25 & (u["fecha"] >= INICIO_LOIP), "tramo_anio"] = "2025 LOIP (26-jun a 6-oct)"
filas_c = []
for fam, ob in COMBOS:
    for ta, s in u[(u.familia == fam) & (u.objeto == ob)].groupby("tramo_anio"):
        mm = medidas(s["razon"])
        filas_c.append(dict(familia=fam, objeto=ob, anio=ta, procesos=mm["procesos"], sobre_el_techo=mm["sobre_el_techo"],
                            pct_sobre=round(100 * mm["sobre_el_techo"] / mm["procesos"], 2) if mm["procesos"] else np.nan,
                            ultimo_1pct=mm["ultimo_1pct"], exceso_1pct=mm["exceso_1pct"], exceso_2pct=mm["exceso_2pct"],
                            pct_en_ultimo_2pct=round(100 * mm["ventana_2pct"] / mm["procesos"], 2) if mm["procesos"] else np.nan))
C = pd.DataFrame(filas_c)
C.to_csv(DIR / "E4_por_anio.csv", index=False, encoding="utf-8-sig")
say("\n(C) Por año (techo oficial). Con pocos procesos por año, el exceso del 1 % es inestable; pct_en_ultimo_2pct es más estable.")
for fam, ob in COMBOS:
    sub = C[(C.familia == fam) & (C.objeto == ob)].drop(columns=["familia", "objeto"])
    say(f"\n{fam} | {ob}")
    say(sub.to_string(index=False))

# (D) zoom: tramos de 0,2 % entre el 96 % y el 100 % del techo oficial
filas_d = []
for fam, ob in COMBOS:
    r = u.loc[(u.familia == fam) & (u.objeto == ob), "razon"]
    r = r[(r >= 0.96) & (r <= 1.0000001)].clip(upper=0.999999)
    cnt = (np.floor(r / 0.002) * 0.002).round(3).value_counts()
    for k in range(20):
        b = round(0.96 + 0.002 * k, 3)
        filas_d.append(dict(familia=fam, objeto=ob, desde_pct_del_techo=round(100 * b, 1), procesos=int(cnt.get(b, 0))))
Dz = pd.DataFrame(filas_d)
Dz.to_csv(DIR / "E4_zoom_96_100.csv", index=False, encoding="utf-8-sig")
say("\n(D) Zoom 96 % a 100 % del techo oficial (tramos de 0,2 %): procesos por tramo")
say(Dz.pivot_table(index="desde_pct_del_techo", columns=["familia", "objeto"], values="procesos").astype(int).to_string())

TECHOS.to_csv(DIR / "E4_tabla_techos_oficiales.csv", index=False, encoding="utf-8-sig")
salidas = {p.name: sha(p) for p in sorted(DIR.glob("*.csv"))}
reg = dict(corrida=RUN, fecha=datetime.now().isoformat(timespec="seconds"), analisis="E4",
           estatus="descriptivo, enmienda D 5.6; fuera de H1, H2 y H3", huellas=HUELLAS, huella_codigo=HUELLA_CODIGO,
           universo=dict(procesos_familias=n_total, universo=U0, con_techo_oficial=int(con_techo.sum()),
                         sin_objeto=int((~con_techo).sum()), anios="2015 a 2025", fecha_tope="2025-10-06",
                         pliego="monto_tender; si falta, monto_final", objeto="categoria_principal; lista corta = consultoria"),
           reglas=dict(ultimo_1pct="[0,99; 1,00] frente a 5 x media de tramos de 0,2 % en [0,90; 0,99)",
                       ventana_2pct="[0,98; 1,00] frente a media de 9 tramos de 2 % en [0,80; 0,98)",
                       placebo="ventanas de 2 % en 0,30 0,40 0,50 0,60 0,70 frente a sus 9 tramos anteriores",
                       sobre_el_techo="razón mayor que 1: se cuentan y quedan fuera de las densidades"),
           nota_loip=("La LOIP (vigente desde el 26-jun-2025) eliminó menor cuantía y cotización; la Corte Constitucional la "
                      "declaró inconstitucional el 26-sep-2025 y la reforma de la LOSNCP rige desde el 7-oct-2025. "
                      "Los techos de 2025 son los anteriores a la LOIP; el tramo LOIP se informa aparte."),
           tabla_techos=TECHOS.to_dict("records"),
           python=platform.python_version(), pandas=pd.__version__, duckdb=duckdb.__version__, salidas=salidas)
(DIR / "registro_E4.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
(DIR / "codigo_celda_E4.py").write_text(CODIGO, encoding="utf-8")
(DIR / "resumen_para_chat.txt").write_text("\n".join(LINEAS), encoding="utf-8")
say(f"\nArchivos en {DIR}")
print("Pega esta salida en el chat (no trae RUC ni procesos uno por uno).")
