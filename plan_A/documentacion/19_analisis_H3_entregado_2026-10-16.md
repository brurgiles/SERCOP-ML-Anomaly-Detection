# Cuaderno 19: análisis de H3 (kappa, Fisher y Holm)

Preparado el 16 de octubre de 2026. Se corre cuando los revisores devuelvan sus hojas. Lo probé con hojas simuladas que tenían procesos no verificables, reservas, desacuerdos, un "Sí" sin evidencia y un consenso, y con pandas 3.0 y 2.2 (mismo resultado).

## 1. Antes de correr: dónde van las hojas

1. Crea la carpeta `C:\SERCOP_FINAL\revision_h3_llenas`.
2. Guarda ahí las hojas devueltas como `revisor_A.xlsx` y `revisor_B.xlsx`, tal como las llenaron. No cambies los nombres de las columnas.
3. **Reservas.** Si un revisor marca un proceso como "No verificable" en todos los ítems, le das el código de reserva siguiendo el `LEEME.txt` de la carpeta de la clave. El revisor agrega una fila al final de su misma hoja, con el código y el ocid de la reserva, y la llena igual que las demás. Si el proceso no verificable era de los 24 de doble revisión, la reserva la revisan los dos.

## 2. Cómo decide el cuaderno

- **Con hallazgo:** al menos un ítem A1 a A7 en "Sí" y algo escrito en la columna de evidencia. Es lo que pide el preregistro ("ítem de tipo A con evidencia documental").
- **"Sí" sin evidencia:** queda pendiente hasta que el revisor ponga el enlace o la captura.
- **No verificable:** los siete ítems en "No verificable". Se reemplaza por su reserva.
- **Sin hallazgo:** ningún "Sí" y ningún ítem en blanco. Si algunos ítems son "No" y otros "No verificable", cuenta como sin hallazgo.
- Acepta "si" sin tilde y "nv" como abreviatura.

**Lo que ya sabemos por H2:** como su p fue 0,606, la corrección de Holm deja a H3 con un umbral de p ≤ 0,025.

## 3. Orden de trabajo

1. En cuanto tengas las dos hojas, corre las **celdas 1 y 2**. Resuelve con los revisores lo que salga en "Por resolver" y vuelve a correrlas hasta que la celda 1 diga "Hojas completas".
2. Santiago y Andrés llenan juntos `consenso_h3.xlsx` (está en la misma carpeta). Vuelve a correr la celda 2 hasta que diga "sin consenso todavía: 0".
3. Recién entonces corre la **celda 3**, que abre la clave. No la corras antes: si hay pendientes, el resultado sale marcado como PROVISIONAL, y no conviene que quien ve el resultado siga coordinando correcciones con los revisores.
4. Adjúntame el `resumen_para_chat.txt` de la carpeta `...\modelos\<fecha>_h3`.

## 4. Cuaderno 19

### Celda 1 · Verificación y lectura de las hojas

Comprueba que la clave es la del sorteo (la huella que te mandaste por correo), lee las dos hojas y revisa que estén completas. **No muestra qué código es priorizado.** **Qué mirar:** la lista 'Por resolver'. Cada línea dice el revisor, el código y qué falta. Se corrige con el revisor y se vuelve a correr.

```python
# =====================================================================================
# CELDA 1. Configuración, verificación y lectura de las hojas llenas
#   Comprueba que la clave de H3 es la registrada, lee las hojas de los dos revisores y revisa
#   que estén completas. Aquí NO se mira qué código es priorizado y cuál control.
# =====================================================================================
import os, glob, json, time, hashlib, platform, unicodedata
from datetime import datetime
import numpy as np
import pandas as pd
from scipy.stats import fisher_exact, norm

SALIDA_TXT, CELDA_ACTUAL = {}, "celda 1"
def say(*args):
    texto = " ".join(str(a) for a in args)
    print(texto)
    SALIDA_TXT.setdefault(CELDA_ACTUAL, []).append(texto)

def guardar_txt():
    if "DIR_RUN" in globals():
        with open(os.path.join(DIR_RUN, "resumen_para_chat.txt"), "w", encoding="utf-8") as f:
            for celda, lineas in SALIDA_TXT.items():
                f.write(f"\n##### {celda.upper()} #####\n" + "\n".join(lineas) + "\n")

def empezar(nombre):
    global CELDA_ACTUAL
    guardar_txt()
    CELDA_ACTUAL = nombre
    SALIDA_TXT[nombre] = []

def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()

def sin_tildes(texto):
    t = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in t if not unicodedata.combining(c)).lower().strip()

# --- rutas y valores registrados ---
SERCOP = r"C:\SERCOP_FINAL"
LLENAS = os.path.join(SERCOP, "revision_h3_llenas")        # aquí van las hojas devueltas por los revisores
HUELLA_CLAVE = "66429288e56aae4073c2d36c5cc384bc77aadbda06af69514899e9548825419d"   # la que te mandaste por correo
ITEMS = ["A1_falta_documento_esencial", "A2_plazo_menor_al_minimo", "A3_no_es_menor_precio",
         "A4_descalifica_sin_motivo", "A5_actividad_no_relacionada", "A6_fraccionamiento_30_dias",
         "A7_contrato_mayor_al_adjudicado"]
EVID = "evidencia_enlaces_o_capturas"
ETIQ = {"hallazgo": "Con hallazgo", "sin_hallazgo": "Sin hallazgo", "no_verificable": "No verificable",
        "pendiente": "Pendiente"}
pd.set_option("display.width", 250)
T_INICIO = time.time()
say(f"Python {platform.python_version()} | numpy {np.__version__} | pandas {pd.__version__}")

# (a) preregistro firmado y sin cambios
PREREG = os.path.join(SERCOP, "preregistro")
FIRMA = json.load(open(os.path.join(PREREG, "preregistro_firma.json"), encoding="utf-8"))
if sha(os.path.join(PREREG, FIRMA["documento"])) != FIRMA["huella_documento"]:
    raise SystemExit("El preregistro cambió después de firmarlo: no se calcula H3.")

# (b) la corrida del cuaderno 18 cuya clave tiene la huella registrada (la que te mandaste por correo)
corridas = []
for reg in sorted(glob.glob(os.path.join(SERCOP, "modelos", "*_h2_h3", "registro_h3_muestra.json"))):
    if json.load(open(reg, encoding="utf-8"))["huellas"]["clave_h3.csv"] == HUELLA_CLAVE:
        corridas.append(os.path.dirname(reg))
if not corridas:
    raise SystemExit("No encuentro la corrida del cuaderno 18 con la huella de clave registrada.")
DIR18 = corridas[0]
CLAVE_PATH = os.path.join(DIR18, "CLAVE_H3_NO_COMPARTIR", "clave_h3.csv")
if sha(CLAVE_PATH) != HUELLA_CLAVE:
    raise SystemExit("La clave de H3 cambió después del sorteo: no sigo. Avísame.")
REG_H2 = json.load(open(os.path.join(DIR18, "registro_h2.json"), encoding="utf-8"))
K = pd.read_csv(CLAVE_PATH, dtype=str, encoding="utf-8-sig")
K["codigo"] = K["codigo"].str.strip().str.upper()
K["orden_reserva"] = pd.to_numeric(K["orden_reserva"], errors="coerce")
K["doble_revision"] = K["doble_revision"].astype(str).str.lower().eq("true")
say(f"Preregistro verificado ({FIRMA['huella_documento'][:16]}) | corrida del sorteo: {os.path.basename(DIR18)} | "
    f"clave verificada ({HUELLA_CLAVE[:16]})")

RUN_ID = datetime.now().strftime("%Y%m%d_%H%M") + "_h3"
DIR_RUN = os.path.join(SERCOP, "modelos", RUN_ID)
os.makedirs(DIR_RUN, exist_ok=True)
say("Corrida:", RUN_ID)

# (c) lectura de las hojas llenas
def respuesta(x):
    if pd.isna(x) or str(x).strip() == "":
        return np.nan
    k = sin_tildes(x)
    if k in ("si", "s"):
        return "Sí"
    if k == "no":
        return "No"
    if k in ("no verificable", "nv", "n/v", "no verificado"):
        return "No verificable"
    return "?"

def leer_hoja(rev):
    for ext in ("xlsx", "csv"):
        p = os.path.join(LLENAS, f"revisor_{rev}.{ext}")
        if os.path.exists(p):
            t = (pd.read_excel(p, dtype=str) if ext == "xlsx"
                 else pd.read_csv(p, dtype=str, sep=None, engine="python", encoding="utf-8-sig"))
            t.columns = [str(c).strip() for c in t.columns]
            faltan = [c for c in ["codigo", "ocid"] + ITEMS + [EVID] if c not in t.columns]
            if faltan:
                raise SystemExit(f"A la hoja del revisor {rev} le faltan columnas: {faltan}")
            t = t[t["codigo"].notna() & (t["codigo"].astype(str).str.strip() != "")].copy()
            t["codigo"] = t["codigo"].str.strip().str.upper()
            if t["codigo"].duplicated().any():
                raise SystemExit(f"Códigos repetidos en la hoja {rev}: {sorted(t.loc[t['codigo'].duplicated(), 'codigo'])}")
            for c in ITEMS:
                t[c] = t[c].map(respuesta)
            t["revisor"] = rev
            return t, p
    raise SystemExit(f"No encuentro revisor_{rev}.xlsx en {LLENAS}. Guarda ahí las hojas devueltas.")

def estado_fila(r):
    v = [r[c] for c in ITEMS]
    if all(x == "No verificable" for x in v):
        return "no_verificable", ""
    if any(x == "?" for x in v):
        return "pendiente", "respuesta no válida"
    hay_si = any(x == "Sí" for x in v)
    evid = isinstance(r[EVID], str) and r[EVID].strip() != ""
    if hay_si and evid:
        return "hallazgo", ""
    if hay_si:
        return "pendiente", "'Sí' sin evidencia"
    if any(pd.isna(x) for x in v):
        return "pendiente", "ítems en blanco"
    return "sin_hallazgo", ""

HOJA, PROBLEMAS = {}, []
for rev in ["A", "B"]:
    t, p = leer_hoja(rev)
    est = t.apply(estado_fila, axis=1, result_type="expand")
    t["estado"], t["motivo"] = est[0], est[1]
    kk = K.set_index("codigo")
    for r in t.itertuples():
        if r.codigo not in kk.index:
            PROBLEMAS.append((rev, r.codigo, "código que no existe en el sorteo"))
        elif str(r.ocid).strip() != kk.loc[r.codigo, "ocid"]:
            PROBLEMAS.append((rev, r.codigo, "el ocid no corresponde al código"))
        elif kk.loc[r.codigo, "tipo"] == "muestra" and rev not in kk.loc[r.codigo, "revisor"]:
            PROBLEMAS.append((rev, r.codigo, "proceso asignado al otro revisor"))
        if r.estado == "pendiente":
            PROBLEMAS.append((rev, r.codigo, r.motivo))
    asignados = set(K.loc[(K["tipo"] == "muestra") & K["revisor"].str.contains(rev, na=False), "codigo"])
    for c in sorted(asignados - set(t["codigo"])):
        PROBLEMAS.append((rev, c, "falta en la hoja"))
    HOJA[rev] = t
    say(f"\nRevisor {rev}: {len(t)} filas ({os.path.basename(p)}, huella {sha(p)[:16]})")
    say("  " + ", ".join(f"{ETIQ[k]}: {int((t['estado'] == k).sum())}" for k in ETIQ))
    m = pd.to_numeric(t["minutos"], errors="coerce") if "minutos" in t.columns else pd.Series(dtype=float)
    if m.notna().any():
        say(f"  minutos por proceso: mediana {m.median():.0f}, máximo {m.max():.0f}")
if PROBLEMAS:
    say("\nPor resolver antes del resultado final (revisor, código, motivo):")
    for p_ in PROBLEMAS:
        say("  ", *p_)
else:
    say("\nHojas completas: no hay nada por resolver.")
guardar_txt()
```

### Celda 2 · Acuerdo entre revisores y consenso

Calcula el kappa de Cohen con los procesos que revisaron los dos y crea `consenso_h3.xlsx` con los desacuerdos. **Tampoco muestra el lado.** Santiago y Andrés llenan juntos la columna `consenso` (lista desplegable) y la nota. Si vuelves a correr la celda, se conserva lo que ya escribieron.

```python
# =====================================================================================
# CELDA 2. Doble revisión: acuerdo (kappa de Cohen) y consenso, todavía sin ver el lado
#   Los desacuerdos van a consenso_h3.xlsx, que los revisores llenan juntos. Si ya existe, se
#   conservan los valores escritos y solo se agregan los desacuerdos nuevos.
# =====================================================================================
empezar("celda 2")
A, B = HOJA["A"].set_index("codigo"), HOJA["B"].set_index("codigo")
DOBLES = sorted(set(A.index) & set(B.index))
D = pd.DataFrame({"codigo": DOBLES, "estado_A": A.loc[DOBLES, "estado"].to_numpy(),
                  "estado_B": B.loc[DOBLES, "estado"].to_numpy()})
asig = set(K.loc[K["doble_revision"], "codigo"])
say(f"Procesos revisados por los dos: {len(D)} (asignados para doble revisión: {len(asig)}; "
    f"faltan {len(asig - set(DOBLES))})")

def kappa(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    po = float(np.mean(a == b))
    pe = a.mean() * b.mean() + (1 - a.mean()) * (1 - b.mean())
    return ((po - pe) / (1 - pe) if pe < 1 else np.nan), po

ok = D["estado_A"].isin(["hallazgo", "sin_hallazgo"]) & D["estado_B"].isin(["hallazgo", "sin_hallazgo"])
KAPPA, ACUERDO = (kappa(D.loc[ok, "estado_A"].eq("hallazgo"), D.loc[ok, "estado_B"].eq("hallazgo"))
                  if ok.sum() else (np.nan, np.nan))
say(f"Kappa de Cohen (hallazgo sí/no) en {int(ok.sum())} procesos verificables para los dos: "
    f"{KAPPA:.3f} | acuerdo simple {ACUERDO:.1%}")
say("Lectura usual del kappa: < 0,20 pobre; 0,21-0,40 débil; 0,41-0,60 moderado; 0,61-0,80 bueno; > 0,80 muy bueno.")
if ok.sum():
    acu = {c: float((A.loc[D.loc[ok, 'codigo'], c].to_numpy() == B.loc[D.loc[ok, 'codigo'], c].to_numpy()).mean())
           for c in ITEMS}
    say("Acuerdo por ítem (descriptivo):", {c[:2]: f"{v:.0%}" for c, v in acu.items()})

# consenso de los desacuerdos (incluye desacuerdos sobre si el proceso es verificable)
DES = D[(D["estado_A"] != D["estado_B"]) & ~D[["estado_A", "estado_B"]].isin(["pendiente"]).any(axis=1)].copy()
CONS_PATH = os.path.join(LLENAS, "consenso_h3.xlsx")
previo = pd.DataFrame(columns=["codigo", "consenso", "nota"])
if os.path.exists(CONS_PATH):
    previo = pd.read_excel(CONS_PATH, dtype=str)
    previo["codigo"] = previo["codigo"].str.strip().str.upper()
plantilla = DES.assign(revisor_A=DES["estado_A"].map(ETIQ), revisor_B=DES["estado_B"].map(ETIQ))
plantilla = plantilla.merge(K[["codigo", "ocid"]], on="codigo", how="left")
plantilla = plantilla.merge(previo[["codigo", "consenso", "nota"]], on="codigo", how="left")
plantilla = plantilla[["codigo", "ocid", "revisor_A", "revisor_B", "consenso", "nota"]]
if len(plantilla):
    try:
        import openpyxl
        from openpyxl.worksheet.datavalidation import DataValidation
        plantilla.to_excel(CONS_PATH, index=False, sheet_name="consenso")
        wb = openpyxl.load_workbook(CONS_PATH)
        ws = wb["consenso"]
        dv = DataValidation(type="list", formula1='"Con hallazgo,Sin hallazgo,No verificable"', allow_blank=True)
        ws.add_data_validation(dv)
        dv.add(f"E2:E{len(plantilla) + 1}")
        for col, ancho in zip("ABCDEF", [9, 45, 16, 16, 18, 40]):
            ws.column_dimensions[col].width = ancho
        wb.save(CONS_PATH)
    except PermissionError:
        raise SystemExit("Cierra consenso_h3.xlsx en Excel y vuelve a correr esta celda.")

def a_estado(x):
    k = sin_tildes(x) if isinstance(x, str) else ""
    return {"con hallazgo": "hallazgo", "sin hallazgo": "sin_hallazgo", "no verificable": "no_verificable"}.get(k)

CONS = {r.codigo: a_estado(r.consenso) for r in plantilla.itertuples()}
falta_cons = [c for c, v in CONS.items() if v is None]
say(f"\nDesacuerdos: {len(plantilla)} | con consenso escrito: {len(plantilla) - len(falta_cons)} | "
    f"sin consenso todavía: {len(falta_cons)}")
if falta_cons:
    say(f"Los revisores deben llenar juntos la columna 'consenso' de {CONS_PATH} para: {', '.join(falta_cons)}")
    say("(La hoja de consenso no dice qué proceso es priorizado: se puede abrir delante de ellos.)")

# valor final de cada código revisado (todavía sin lado)
FINAL = {}
for rev in ["A", "B"]:
    for r in HOJA[rev].itertuples():
        FINAL.setdefault(r.codigo, r.estado)
for r in D.itertuples():
    if r.estado_A == r.estado_B:
        FINAL[r.codigo] = r.estado_A
    elif "pendiente" in (r.estado_A, r.estado_B):
        FINAL[r.codigo] = "pendiente"
    else:
        FINAL[r.codigo] = CONS.get(r.codigo) or "pendiente"
guardar_txt()
```

### Celda 3 · Prueba de H3, Holm y decisión

**Abre la clave.** Reemplaza los no verificables por sus reservas, calcula la prueba exacta de Fisher unilateral, aplica Holm con el p de H2 y da la decisión. Después muestra descriptivos: ítems por lado, hallazgos por grupo y la tasa de cada revisor. Guarda `registro_h3.json`.

```python
# =====================================================================================
# CELDA 3. Se abre la clave: reemplazos por reservas, prueba exacta de Fisher, Holm con H2
#   y decisión. Correr solo cuando la celda 1 no tenga nada por resolver y la celda 2 tenga
#   todos los consensos; si no, el resultado sale marcado como PROVISIONAL.
# =====================================================================================
empezar("celda 3")
est = lambda c: FINAL.get(c, "no_revisado")
VALIDO = ("hallazgo", "sin_hallazgo")
filas, AVISOS = [], []

# lado priorizado: los no verificables se reemplazan por las reservas en orden (1, 2, ...)
P_m = K[(K["tipo"] == "muestra") & (K["lado"] == "priorizado")]
P_r = K[(K["tipo"] == "reserva") & (K["lado"] == "priorizado")].sort_values("orden_reserva")
nv_p = [c for c in P_m["codigo"] if est(c) == "no_verificable"]
for c in P_m["codigo"]:
    if est(c) != "no_verificable":
        filas.append(dict(lado="priorizado", original=c, final=c, estado=est(c)))
usadas = [c for c in P_r["codigo"] if est(c) != "no_revisado"]
validas = [c for c in P_r["codigo"] if est(c) in VALIDO]
for j, c in enumerate(nv_p):
    if j < len(validas):
        filas.append(dict(lado="priorizado", original=c, final=validas[j], estado=est(validas[j])))
    else:
        filas.append(dict(lado="priorizado", original=c, final="", estado="pendiente"))
        AVISOS.append(f"{c} (no verificable) necesita una reserva de priorizado revisada")
orden_usadas = P_r.set_index("codigo").loc[usadas, "orden_reserva"].tolist() if usadas else []
if orden_usadas and orden_usadas != list(range(1, len(orden_usadas) + 1)):
    AVISOS.append(f"las reservas de priorizado revisadas no siguen el orden 1, 2, ...: {orden_usadas}")

# lado control: cada control no verificable se reemplaza por SUS reservas (columna reemplaza_a)
C_m = K[(K["tipo"] == "muestra") & (K["lado"] == "control")]
C_r = K[(K["tipo"] == "reserva") & (K["lado"] == "control")].sort_values("orden_reserva")
for c in C_m["codigo"]:
    if est(c) != "no_verificable":
        filas.append(dict(lado="control", original=c, final=c, estado=est(c)))
        continue
    cand = [r for r in C_r.loc[C_r["reemplaza_a"] == c, "codigo"] if est(r) in VALIDO]
    if cand:
        filas.append(dict(lado="control", original=c, final=cand[0], estado=est(cand[0])))
    else:
        filas.append(dict(lado="control", original=c, final="", estado="pendiente"))
        AVISOS.append(f"{c} (no verificable) necesita revisar su reserva de control")
for c in K.loc[K["tipo"] == "reserva", "codigo"]:
    if est(c) != "no_revisado" and c not in [f["final"] for f in filas] and est(c) != "no_verificable":
        AVISOS.append(f"la reserva {c} se revisó pero no reemplaza a ningún proceso no verificable")

R3 = pd.DataFrame(filas).merge(K[["codigo", "grupo", "anio"]].rename(columns={"codigo": "final"}), on="final", how="left")
R3["hallazgo"] = R3["estado"].map({"hallazgo": 1, "sin_hallazgo": 0})
pend = R3["hallazgo"].isna()
PROVISIONAL = bool(pend.any() or PROBLEMAS or falta_cons)
for f in AVISOS:
    say("AVISO:", f)

# prueba exacta de Fisher unilateral (priorizados > controles)
def wilson(k, n, z=1.959964):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    c = (p + z * z / (2 * n)) / (1 + z * z / n)
    m = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return (c - m, c + m)

v = R3[~pend]
a, n1 = int(v.loc[v["lado"] == "priorizado", "hallazgo"].sum()), int((v["lado"] == "priorizado").sum())
c_, n2 = int(v.loc[v["lado"] == "control", "hallazgo"].sum()), int((v["lado"] == "control").sum())
OR, P_H3 = fisher_exact([[a, n1 - a], [c_, n2 - c_]], alternative="greater") if n1 and n2 else (np.nan, np.nan)
p1, p2 = (a / n1 if n1 else np.nan), (c_ / n2 if n2 else np.nan)
ci1, ci2 = wilson(a, n1), wilson(c_, n2)
NV = {"priorizado": len(nv_p), "control": int(sum(est(c) == "no_verificable" for c in C_m["codigo"]))}
say(f"\nProcesos con resultado: priorizados {n1} de 60 | controles {n2} de 60 | no verificables de la muestra "
    f"(se reemplazan por reserva): {NV}")
say(f"Con hallazgo: priorizados {a}/{n1} = {p1:.1%} (IC 95 % {ci1[0]:.1%} a {ci1[1]:.1%}) | "
    f"controles {c_}/{n2} = {p2:.1%} (IC 95 % {ci2[0]:.1%} a {ci2[1]:.1%})")
say(f"Diferencia {100 * (p1 - p2):+.1f} puntos | razón de odds {OR:.2f} | p unilateral de Fisher = {P_H3:.4f}")

# Holm con H2 (preregistro, sección 10)
P_H2 = next(r["p_unilateral"] for r in REG_H2["h2"] if r["estatus"] == "confirmatoria")
orden = sorted([("H2", P_H2), ("H3", P_H3)], key=lambda t: t[1])
RECHAZA, seguir = {}, True
for umbral, (h, p) in zip([0.025, 0.05], orden):
    RECHAZA[h] = bool(seguir and p <= umbral)
    seguir = RECHAZA[h]
say(f"\nHolm: p de H2 = {P_H2:.4f}, p de H3 = {P_H3:.4f} | umbrales 0,025 para el menor y 0,05 para el otro")
say(f"  H2 {'se rechaza' if RECHAZA['H2'] else 'no se rechaza'} | H3 {'SE CUMPLE' if RECHAZA['H3'] else 'NO SE CUMPLE'}")
say("Decisión general (sección 10): H1 no se cumplió, así que la hipótesis general no queda respaldada y el "
    "resultado favorece al índice simple, salga lo que salga en H2 y H3.")

# descriptivos (no confirmatorios)
items = []
for f in R3[~pend].itertuples():
    revs = [HOJA[r].set_index("codigo") for r in ["A", "B"] if f.final in set(HOJA[r]["codigo"])]
    fila = {"lado": f.lado}
    for c in ITEMS:
        fila[c[:2]] = int(any(h.loc[f.final, c] == "Sí" for h in revs))
    items.append(fila)
if items:
    say("\nÍtems marcados 'Sí' por lado (en los de doble revisión cuenta si al menos un revisor lo marcó):")
    say(pd.DataFrame(items).groupby("lado").sum().to_string())
say("\nHallazgos por grupo (procesos con resultado):")
say(R3[~pend].assign(hallazgo=lambda t: t["hallazgo"].astype(int))
    .pivot_table(index="grupo", columns="lado", values="hallazgo", aggfunc=["sum", "count"], fill_value=0)
    .rename(columns={"sum": "con_hallazgo", "count": "procesos"}).to_string())
sev = []
for rev in ["A", "B"]:
    h = HOJA[rev].merge(K[["codigo", "lado"]], on="codigo")
    h = h[h["estado"].isin(VALIDO)]
    for lado, g in h.groupby("lado"):
        sev.append(dict(revisor=rev, lado=lado, revisados=len(g), con_hallazgo=f"{g['estado'].eq('hallazgo').mean():.0%}"))
say("\nTasa de hallazgo por revisor (para ver si uno es más estricto que el otro):")
say(pd.DataFrame(sev).to_string(index=False))

# registro
R3.to_csv(os.path.join(DIR_RUN, "h3_procesos_final.csv"), index=False)
REGISTRO = dict(corrida=RUN_ID, fecha=datetime.now().isoformat(timespec="seconds"), provisional=PROVISIONAL,
                preregistro=FIRMA["huella_documento"], corrida_sorteo=os.path.basename(DIR18), huella_clave=HUELLA_CLAVE,
                huellas_hojas={rev: sha(os.path.join(LLENAS, f)) for rev in ["A", "B"]
                               for f in os.listdir(LLENAS) if f.startswith(f"revisor_{rev}.")},
                huella_consenso=sha(CONS_PATH) if os.path.exists(CONS_PATH) else None,
                kappa=KAPPA, acuerdo=ACUERDO, dobles=len(D), desacuerdos=len(plantilla),
                h3=dict(priorizados=[a, n1], controles=[c_, n2], p_fisher=P_H3, razon_odds=OR,
                        ic95_priorizados=list(ci1), ic95_controles=list(ci2)),
                holm=dict(p_H2=P_H2, p_H3=P_H3, rechaza=RECHAZA), avisos=AVISOS,
                minutos=round((time.time() - T_INICIO) / 60, 1))
with open(os.path.join(DIR_RUN, "registro_h3.json"), "w", encoding="utf-8") as f:
    json.dump(REGISTRO, f, ensure_ascii=False, indent=1, default=float)
say("\n" + "=" * 100)
say(("RESULTADO PROVISIONAL: hay pendientes (ver arriba). " if PROVISIONAL else "RESULTADO FINAL. ") +
    f"H3 {'se cumple' if RECHAZA['H3'] else 'no se cumple'} | {a}/{n1} frente a {c_}/{n2} | p {P_H3:.4f} | kappa {KAPPA:.3f}")
say("Archivos en", DIR_RUN)
guardar_txt()
say("Adjunta en el chat el archivo resumen_para_chat.txt de esa carpeta.")
guardar_txt()
```

## 5. Si algo falla

- "No encuentro la corrida del cuaderno 18 con la huella de clave registrada" o "La clave de H3 cambió": no sigas; avísame.
- "Faltan columnas": alguien cambió el nombre de una columna de la hoja; devuélvele su nombre original.
- "Códigos repetidos": una fila está dos veces en la misma hoja; deja una.
- `consenso_h3.xlsx` abierto en Excel: ciérralo y vuelve a correr la celda 2.
- Cualquier otro error: las últimas 20 líneas y el `resumen_para_chat.txt`.