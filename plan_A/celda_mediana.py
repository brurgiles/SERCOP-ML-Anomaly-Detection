# CAPÍTULO 1 · CONSULTA. Mediana de licitación frente a la de cotización (solo lectura)
#   Pregunta: en la tabla B del capítulo 1 la mediana de licitación (93.208,7 USD) sale por debajo de la de cotización
#   (271.879,4 USD), aunque la licitación es el procedimiento de los montos más altos. Esta celda separa la base por
#   período (antes y desde la reforma del 7-oct-2025), por año y por objeto, y compara monto_final con monto_tender.
#   Hipótesis a revisar: desde la reforma la licitación absorbe procesos más pequeños (2026 tiene muchas más licitaciones
#   que 2024) y eso baja la mediana de toda la serie. No es la única posible: la última tabla mira si el monto
#   adjudicado (monto_final) queda muy por debajo del presupuesto (monto_tender).
#   Universo: los 446.677 procesos de planA_procesos_modelo (los de la tabla B). No lee columnas de RUC, no usa la muestra de
#   H3 ni planA_validacion_sri, no imprime procesos, no escribe sobre planA_indicadores ni planA_procesos_modelo.
#   Escribe en una carpeta nueva capitulo1\mediana_AAAAMMDD_HHMMSS\ y no sobrescribe nada.
import hashlib, json, platform, unicodedata
from datetime import datetime
from pathlib import Path
import numpy as np, pandas as pd, duckdb

BASE = Path(r"C:\SERCOP_FINAL")
PM = BASE / "plan_A" / "planA_procesos_modelo.parquet"
HUELLA_PM = "adb1768ebd2dd83a"                    # la del preregistro
N_BASE = 446677                                   # filas de la base (tabla B)
TABLA_B = {"licitacion": (16542, 93208.7), "cotizacion": (19204, 271879.4)}   # (procesos, mediana de monto_final) de la tabla B
CORTE_REFORMA = pd.Timestamp("2025-10-07")        # reforma de la LOSNCP

# ---------------- 1. Verificar el archivo y leer solo las columnas necesarias ----------------
def sha(r):
    h = hashlib.sha256()
    with open(r, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()

huella_pm = sha(PM)
if not huella_pm.startswith(HUELLA_PM):
    raise SystemExit(f"{PM.name} no tiene la huella registrada ({HUELLA_PM}): para y avisa. No se escribió nada.")
try:
    CODIGO = _ih[-1]                              # texto de esta celda (cuando se corre en el cuaderno)
except NameError:
    CODIGO = ""
HUELLA_CODIGO = hashlib.sha256(CODIGO.encode("utf-8")).hexdigest() if CODIGO else "no disponible"

con = duckdb.connect()
cols = [r[0] for r in con.execute(f"DESCRIBE SELECT * FROM read_parquet('{PM.as_posix()}')").fetchall()]
falta = [c for c in ["familia_procedimiento", "fecha_inicio_tender", "monto_final", "monto_tender", "categoria_principal"]
         if c not in cols]
if falta:
    raise SystemExit(f"Faltan columnas: {falta}. Para y avisa. No se escribió nada.")
d = con.execute(f"""
    SELECT familia_procedimiento AS familia, fecha_inicio_tender AS f, monto_final, monto_tender, categoria_principal
    FROM read_parquet('{PM.as_posix()}')
""").df()
if len(d) != N_BASE:
    raise SystemExit(f"La base tiene {len(d)} filas y se esperaban {N_BASE}: para y avisa. No se escribió nada.")

def sin_tildes(x):
    return unicodedata.normalize("NFKD", str(x)).encode("ascii", "ignore").decode().lower().strip()

# Familias: se buscan por su nombre sin tildes, para no depender de cómo estén escritas
nombres = sorted(d["familia"].dropna().unique())
def buscar(prefijo):
    hallados = [n for n in nombres if sin_tildes(n).startswith(prefijo)]
    if len(hallados) != 1:
        raise SystemExit(f"No encontré una sola familia que empiece con '{prefijo}': {nombres}. Para y avisa. No se escribió nada.")
    return hallados[0]
LIC, COT = buscar("licitaci"), buscar("cotizaci")

fecha = pd.to_datetime(d["f"], errors="coerce")
try:
    if fecha.dt.tz is not None:
        fecha = fecha.dt.tz_convert("America/Guayaquil").dt.tz_localize(None)
except AttributeError:
    pass
d["anio"] = fecha.dt.year
d["periodo"] = np.where(fecha.isna(), "sin fecha",
                np.where(fecha >= CORTE_REFORMA, "posterior (desde 7-oct-2025)", "anterior (hasta 6-oct-2025)"))
d["mf"] = pd.to_numeric(d["monto_final"], errors="coerce")
d["mt"] = pd.to_numeric(d["monto_tender"], errors="coerce")
d["razon"] = (d["mf"] / d["mt"]).where((d["mf"] > 0) & (d["mt"] > 0))     # monto adjudicado sobre presupuesto

RUN = datetime.now().strftime("%Y%m%d_%H%M%S")
DIR = BASE / "capitulo1" / f"mediana_{RUN}"
DIR.mkdir(exist_ok=False)
LINEAS = []
def say(*a):
    s = " ".join(str(x) for x in a); print(s); LINEAS.append(s)
fmt = lambda n: f"{int(n):,}".replace(",", ".")
def usd(x):
    return "" if pd.isna(x) else f"{x:,.1f}".replace(",", "X").replace(".", ",").replace("X", ".")
def pct(x):
    return "" if pd.isna(x) else f"{100 * x:.1f}".replace(".", ",") + " %"

# ---------------- 2. Cálculo de medianas y percentiles ----------------
def tabla(df, claves, col):
    filas = []
    for k, g in df.groupby(claves, dropna=False, sort=True):
        k = k if isinstance(k, tuple) else (k,)
        x = g[col].dropna()
        x = x[x > 0]
        fila = dict(zip(claves, k))
        fila["procesos"] = len(g)
        fila["con_dato"] = len(x)
        if len(x):
            q = x.quantile([0.10, 0.25, 0.50, 0.75, 0.90])
            fila.update(p10=q[0.10], p25=q[0.25], mediana=q[0.50], p75=q[0.75], p90=q[0.90])
            if col == "mf":                       # porcentaje de procesos con monto final bajo cada umbral (USD)
                for u in (50000, 100000, 250000):
                    fila[f"pct_bajo_{u // 1000}mil"] = float((x < u).mean())
            if col == "razon":                    # porcentaje que se adjudicó por menos de la mitad del presupuesto
                fila["pct_razon_bajo_0_5"] = float((x < 0.5).mean())
        filas.append(fila)
    return pd.DataFrame(filas)

say(f"Corrida {RUN} | capítulo 1: mediana de licitación frente a cotización | archivo {PM.name} {huella_pm[:16]} | "
    f"código {HUELLA_CODIGO[:16]} | Python {platform.python_version()}, pandas {pd.__version__}, DuckDB {duckdb.__version__}")
say(f"Universo: {fmt(len(d))} procesos de la base (sin catálogo, con RUC de proveedor y monto positivo). "
    f"Familias: {', '.join(nombres)}.")
sin_fecha = int((d["periodo"] == "sin fecha").sum())
say(f"Procesos sin fecha de inicio: {fmt(sin_fecha)}. Con monto_final positivo: {fmt((d['mf'] > 0).sum())}. "
    f"Con monto_tender positivo: {fmt((d['mt'] > 0).sum())}.")

# ---------------- A. Control: reproducir la tabla B ----------------
say("\n=== A. Control: la mediana de monto_final de toda la serie debe reproducir la tabla B ===")
control = {}
for nombre, fam in [("licitacion", LIC), ("cotizacion", COT)]:
    x = d.loc[d["familia"] == fam, "mf"].dropna()
    x = x[x > 0]
    med = float(x.median())
    n_b, med_b = TABLA_B[nombre]
    ok = (len(x) == n_b) and abs(med - med_b) <= 0.05
    control[nombre] = dict(procesos=int(len(x)), mediana=med, tabla_B_procesos=n_b, tabla_B_mediana=med_b, reproduce=bool(ok))
    say(f"  {fam}: {fmt(len(x))} procesos, mediana {usd(med)} USD; tabla B {fmt(n_b)} y {usd(med_b)} -> "
        f"{'REPRODUCE' if ok else 'NO REPRODUCE: no sigas con la lectura y pega esta salida'}")

# ---------------- B. Por familia y período ----------------
say("\n=== B. Monto final por familia y período (USD) ===")
B = tabla(d[d["periodo"] != "sin fecha"], ["familia", "periodo"], "mf")
Bt = tabla(d[d["periodo"] != "sin fecha"], ["familia", "periodo"], "mt")[["familia", "periodo", "con_dato", "mediana"]]
Bt.columns = ["familia", "periodo", "con_monto_tender", "mediana_monto_tender"]
B = B.merge(Bt, on=["familia", "periodo"], how="left")
vis = B.copy()
for c in ["p10", "p25", "mediana", "p75", "p90", "mediana_monto_tender"]:
    vis[c] = vis[c].map(usd)
for c in ["pct_bajo_50mil", "pct_bajo_100mil", "pct_bajo_250mil"]:
    vis[c] = vis[c].map(pct)
vis["procesos"] = vis["procesos"].map(fmt)
say(vis[["familia", "periodo", "procesos", "p25", "mediana", "p75", "mediana_monto_tender"]].to_string(index=False))
say("\n  Porcentaje de procesos con monto_final bajo 50.000, 100.000 y 250.000 USD")
say(vis[["familia", "periodo", "pct_bajo_50mil", "pct_bajo_100mil", "pct_bajo_250mil"]].to_string(index=False))

# ---------------- C. Licitación y cotización por año ----------------
say("\n=== C. Licitación y cotización por año de inicio (monto_final, USD) ===")
LC = d[d["familia"].isin([LIC, COT])]
C = tabla(LC, ["familia", "anio", "periodo"], "mf")
Ct = tabla(LC, ["familia", "anio", "periodo"], "mt")[["familia", "anio", "periodo", "mediana"]].rename(columns={"mediana": "mediana_monto_tender"})
C = C.merge(Ct, on=["familia", "anio", "periodo"], how="left")
vis = C.copy()
for c in ["p25", "mediana", "p75", "mediana_monto_tender"]:
    vis[c] = vis[c].map(usd)
vis["pct_bajo_100mil"] = vis["pct_bajo_100mil"].map(pct)
vis["procesos"] = vis["procesos"].map(fmt)
vis["anio"] = vis["anio"].map(lambda v: "" if pd.isna(v) else str(int(v)))
vis["periodo"] = vis["periodo"].str.split(" ").str[0]
say(vis[["familia", "anio", "periodo", "procesos", "p25", "mediana", "p75", "mediana_monto_tender", "pct_bajo_100mil"]].to_string(index=False))

# ---------------- D. Por objeto (categoria_principal), período anterior ----------------
say("\n=== D. Licitación y cotización por objeto, período anterior a la reforma (monto_final, USD) ===")
LCa = LC[LC["periodo"] == "anterior (hasta 6-oct-2025)"].copy()
LCa["objeto"] = LCa["categoria_principal"].fillna("(vacío)")
D = tabla(LCa, ["familia", "objeto"], "mf")
vis = D.copy()
for c in ["p25", "mediana", "p75"]:
    vis[c] = vis[c].map(usd)
vis["procesos"] = vis["procesos"].map(fmt)
say(vis[["familia", "objeto", "procesos", "p25", "mediana", "p75"]].to_string(index=False))

# ---------------- E. Monto adjudicado sobre presupuesto ----------------
say("\n=== E. Razón monto_final / monto_tender (procesos con los dos montos positivos; 1 = se adjudicó por todo el presupuesto) ===")
E = tabla(LC[LC["periodo"] != "sin fecha"], ["familia", "periodo"], "razon")
vis = E.copy()
for c in ["p10", "p25", "mediana", "p75", "p90"]:
    vis[c] = vis[c].map(lambda v: "" if pd.isna(v) else f"{v:.3f}".replace(".", ","))
vis["con_dato"] = vis["con_dato"].map(fmt)
vis["pct_razon_bajo_0_5"] = vis["pct_razon_bajo_0_5"].map(pct)
say(vis[["familia", "periodo", "con_dato", "p10", "mediana", "p90", "pct_razon_bajo_0_5"]].to_string(index=False))

# ---------------- F. Lectura automática de las cifras ----------------
say("\n=== F. Comparación directa ===")
def med(fam, per):
    r = B[(B["familia"] == fam) & (B["periodo"] == per)]
    return float(r["mediana"].iloc[0]) if len(r) and "mediana" in r and not pd.isna(r["mediana"].iloc[0]) else np.nan
ANT, POS = "anterior (hasta 6-oct-2025)", "posterior (desde 7-oct-2025)"
lic_a, lic_p, cot_a = med(LIC, ANT), med(LIC, POS), med(COT, ANT)
n_lic = {p: int(((d["familia"] == LIC) & (d["periodo"] == p)).sum()) for p in (ANT, POS)}
say(f"  Mediana de licitación, período anterior: {usd(lic_a)} USD ({fmt(n_lic[ANT])} procesos).")
say(f"  Mediana de licitación, período posterior: {usd(lic_p)} USD ({fmt(n_lic[POS])} procesos).")
say(f"  Mediana de cotización, período anterior: {usd(cot_a)} USD (la cotización no existe en el posterior).")
if not (pd.isna(lic_a) or pd.isna(cot_a)):
    say(f"  En el período anterior la licitación {'supera' if lic_a > cot_a else 'NO supera'} a la cotización "
        f"({usd(lic_a)} frente a {usd(cot_a)}).")
tot = n_lic[ANT] + n_lic[POS]
say(f"  Licitaciones del período posterior: {pct(n_lic[POS] / tot)} del total de licitaciones de la base.")

# ---------------- G. Escribir archivos ----------------
B.to_csv(DIR / "B_monto_final_por_familia_y_periodo.csv", index=False, encoding="utf-8-sig")
C.to_csv(DIR / "C_licitacion_cotizacion_por_anio.csv", index=False, encoding="utf-8-sig")
D.to_csv(DIR / "D_licitacion_cotizacion_por_objeto_anterior.csv", index=False, encoding="utf-8-sig")
E.to_csv(DIR / "E_razon_final_sobre_tender.csv", index=False, encoding="utf-8-sig")
reg = dict(corrida=RUN, archivo=PM.name, huella_archivo=huella_pm, huella_codigo=HUELLA_CODIGO, filas=int(len(d)),
           familia_licitacion=LIC, familia_cotizacion=COT, sin_fecha=sin_fecha, control_tabla_B=control,
           corte_reforma=str(CORTE_REFORMA.date()), python=platform.python_version(), pandas=pd.__version__,
           duckdb=duckdb.__version__)
(DIR / "registro_mediana.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
(DIR / "resumen_para_chat.txt").write_text("\n".join(LINEAS) + "\n", encoding="utf-8")
say(f"\nListo. Archivos en {DIR}. Pega aquí solo el contenido de resumen_para_chat.txt.")
