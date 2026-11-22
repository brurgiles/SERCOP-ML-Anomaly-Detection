# =====================================================================================
# ENMIENDA D · REGISTRO (se corre UNA sola vez, desde un cuaderno auxiliar; no desde los cuadernos 16 a 19)
#   1) Verifica, solo leyendo, que el preregistro, las enmiendas A a C, la lista congelada y el código del
#      cuaderno 19 siguen iguales, y que H3 todavía no tiene resultados.
#   2) Lee el texto de la enmienda: enmiendas\borrador_d\texto_enmienda_d.json. Tiene que ser el que revisó el grupo
#      y no puede tener datos sin completar (como la fecha de llegada de las hojas).
#   3) Con GRUPO_REVISO_EL_TEXTO = False muestra el texto y se detiene. Con True lo registra en
#      enmiendas\enmienda_AAAA-MM-DD_d.json (archivo nuevo; si ya existe una enmienda D, se detiene) y muestra su huella.
#   No imprime ningún RUC, no abre puntajes.parquet por proceso y no escribe en planA_indicadores ni planA_procesos_modelo.
# =====================================================================================
import os, json, glob, hashlib, platform
from datetime import datetime

GRUPO_REVISO_EL_TEXTO = False        # cámbialo a True solo cuando Santiago, Andrés y tú hayan leído el texto
HUELLA_BORRADOR = "effdafac3a3cd666799c5113cb67431c82596918f30d3117bd928d0d6f75df23"   # SHA-256 del texto que se revisó
HUELLA_ENMIENDA_C = "b26e9fd95e490f23d13d301e54106a295528d96129e4dd78c2f19e8867256ea8"  # la misma que guardó registro_h2.json

SERCOP = r"C:\SERCOP_FINAL"
ENM, PREREG, MODELOS = (os.path.join(SERCOP, d) for d in ("enmiendas", "preregistro", "modelos"))

def sha_archivo(path):
    """SHA-256 de un archivo, leído por bloques (no lo carga entero en memoria)."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()

def parar(motivo):
    raise SystemExit("NO SE REGISTRA NADA. " + motivo)

# ---------- 1. El preregistro firmado y todos los archivos que cita siguen intactos ----------
print("Verificando huellas (los archivos grandes pueden tardar un minuto)...")
firma_path = os.path.join(PREREG, "preregistro_firma.json")
if not os.path.exists(firma_path):
    parar("No encuentro preregistro_firma.json.")
FIRMA = json.load(open(firma_path, encoding="utf-8"))
if sha_archivo(os.path.join(PREREG, FIRMA["documento"])) != FIRMA["huella_documento"]:
    parar("El preregistro cambió después de firmarlo.")
for rel, h in FIRMA["huellas_citadas"].items():
    ruta = os.path.join(SERCOP, rel.replace("\\", os.sep))
    if not os.path.exists(ruta) or sha_archivo(ruta) != h:
        parar(f"{rel} falta o cambió después de la firma.")
print(f"Preregistro verificado: {FIRMA['huella_documento'][:16]}, firmado el {FIRMA['fecha_firma']}; "
      f"{len(FIRMA['huellas_citadas'])} archivos citados, todos iguales.")

# ---------- 2. Enmiendas A, B y C, y el registro de H1 que cita la C ----------
h_enm = {}
for letra, nombre in (("a", "enmienda_2026-10-16.json"), ("b", "enmienda_2026-10-16_b.json"), ("c", "enmienda_2026-10-16_c.json")):
    ruta = os.path.join(ENM, nombre)
    if not os.path.exists(ruta):
        parar(f"No encuentro {nombre}.")
    h_enm[letra] = sha_archivo(ruta)
if h_enm["c"] != HUELLA_ENMIENDA_C:
    parar("La enmienda C no tiene la huella que guardó registro_h2.json.")
ENM_C = json.load(open(os.path.join(ENM, "enmienda_2026-10-16_c.json"), encoding="utf-8"))
ruta_h1 = os.path.join(MODELOS, ENM_C["sigue_a"]["corrida_h1"], "registro_h1.json")
if not os.path.exists(ruta_h1) or sha_archivo(ruta_h1) != ENM_C["sigue_a"]["registro_h1"]:
    parar("El registro de H1 falta o cambió respecto de la huella que cita la enmienda C.")
print("Enmiendas A, B y C y registro de H1: iguales a lo registrado.")

# ---------- 3. El código del cuaderno 19 es el registrado el 25 de octubre (solo las celdas 1, 2 y 3) ----------
REG19 = json.load(open(os.path.join(PREREG, "huella_cuaderno19.json"), encoding="utf-8"))
nb = json.load(open(os.path.join(SERCOP, "plan_A", "cuaderno19.ipynb"), encoding="utf-8"))
def titulo(f):
    l = f.splitlines()
    return l[1].strip("# ").strip() if len(l) > 1 else ""
codigo = ["".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]
analisis = [f for f in codigo if titulo(f)[:8] in ("CELDA 1.", "CELDA 2.", "CELDA 3.")]
if [titulo(f)[:7] for f in analisis] != ["CELDA 1", "CELDA 2", "CELDA 3"]:
    parar("No encuentro las celdas 1, 2 y 3 del cuaderno 19 en ese orden.")
SEP = "\n# ----- fin de celda -----\n"
h19 = hashlib.sha256(SEP.join(analisis).encode("utf-8")).hexdigest()
if h19 != REG19["huella_codigo_sha256"]:
    parar("El código del cuaderno 19 cambió después de registrar su huella.")
print(f"Cuaderno 19: código igual al registrado el {REG19['fecha_hora']} ({h19[:16]}).")

# ---------- 4. Estado al registrar: H3 sin resultados y ninguna corrida exploratoria ----------
llenas = os.path.join(SERCOP, "revision_h3_llenas")
if os.path.isdir(llenas) and os.listdir(llenas):
    parar("Hay archivos en revision_h3_llenas: la enmienda D se registra antes de copiar las hojas a esa carpeta. "
          "Sácalos de ahí, registra la D y después cópialos.")
if glob.glob(os.path.join(MODELOS, "*_h3", "registro_h3.json")):
    parar("Ya existe un registro_h3.json: H3 ya se calculó.")
if glob.glob(os.path.join(MODELOS, "*expD*")):
    parar("Ya existe una corrida exploratoria de la enmienda D.")
if glob.glob(os.path.join(ENM, "enmienda_*_d*.json")):
    parar("Ya existe una enmienda D. Esta celda no sobrescribe ni crea una segunda.")
print("Estado: revision_h3_llenas vacía o inexistente, sin registro_h3.json, sin corridas exploratorias, sin otra enmienda D.")

# ---------- 5. El texto que se revisó ----------
borrador = os.path.join(ENM, "borrador_d", "texto_enmienda_d.json")
if not os.path.exists(borrador):
    parar("No encuentro enmiendas\\borrador_d\\texto_enmienda_d.json.")
if sha_archivo(borrador) != HUELLA_BORRADOR:
    parar("El texto de la enmienda no es el que se revisó (su huella cambió). Avísame antes de seguir.")
TEXTO = json.load(open(borrador, encoding="utf-8"))
SECCIONES = ["titulo", "declaracion", "motivo", "no_cambia", "decisiones", "analisis_exploratorios", "confirmacion", "integridad"]
if list(TEXTO) != SECCIONES:
    parar("El texto de la enmienda no tiene las secciones esperadas.")
if "POR CONFIRMAR" in json.dumps(TEXTO, ensure_ascii=False):
    parar("El texto todavía tiene datos sin completar (la fecha de llegada de las hojas). Pídeme el texto final.")
print(f"Texto de la enmienda: igual al revisado ({HUELLA_BORRADOR[:16]}).")

# ====================================== ARMADO ======================================
ahora = datetime.now()
hoy = ahora.strftime("%Y-%m-%d")
D = {
 "fecha": ahora.isoformat(timespec="seconds"),
 "id": f"enmienda_{hoy}_d",
 "titulo": TEXTO["titulo"],
 "sigue_a": {
  "preregistro": FIRMA["huella_documento"], "firma_fecha": FIRMA["fecha_firma"],
  "enmienda_a": h_enm["a"], "enmienda_b": h_enm["b"], "enmienda_c": h_enm["c"],
  "registro_h1": ENM_C["sigue_a"]["registro_h1"], "corrida_h1": ENM_C["sigue_a"]["corrida_h1"],
  "lista_congelada": {
   "corrida": "20261016_1017_completo_normal_sup",
   "puntajes.parquet": FIRMA["huellas_citadas"]["modelos\\20261016_1017_completo_normal_sup\\puntajes.parquet"][:16],
   "registro_corrida.json": FIRMA["huellas_citadas"]["modelos\\20261016_1017_completo_normal_sup\\registro_corrida.json"][:16]},
  "cuaderno19": {"huella_codigo_sha256": REG19["huella_codigo_sha256"], "registrada": REG19["fecha_hora"]}},
 "firmantes_del_preregistro": FIRMA["firmantes"],
 "revisada_por_el_grupo_antes_de_registrar": bool(GRUPO_REVISO_EL_TEXTO),
 "texto_revisado": {"archivo": "enmiendas\\borrador_d\\texto_enmienda_d.json", "sha256": HUELLA_BORRADOR},
}
for clave in SECCIONES[1:]:
    D[clave] = TEXTO[clave]
D["verificaciones_al_registrar"] = {
 "archivos_citados_por_la_firma_iguales": len(FIRMA["huellas_citadas"]),
 "registro_h1_igual_al_citado_por_la_enmienda_c": True,
 "codigo_cuaderno19_igual_al_registrado": True,
 "revision_h3_llenas": "no existe o está vacía",
 "registro_h3_json": "no existe",
 "corridas_exploratorias_de_la_d": "ninguna",
 "otra_enmienda_d": "ninguna",
 "python": platform.python_version()}
datos = json.dumps(D, ensure_ascii=False, indent=1).encode("utf-8")

if not GRUPO_REVISO_EL_TEXTO:
    print("\n" + "=" * 100)
    print("REVISIÓN: todas las verificaciones pasaron. El texto de abajo todavía NO está registrado.")
    print("Si los tres están de acuerdo, pon GRUPO_REVISO_EL_TEXTO = True y vuelve a correr la celda.")
    print("=" * 100)
    print(json.dumps(TEXTO, ensure_ascii=False, indent=1))
    raise SystemExit("Revisión: no se escribió nada.")

# ====================================== REGISTRO ======================================
destino = os.path.join(ENM, f"enmienda_{hoy}_d.json")
with open(destino, "xb") as f:                      # "x": crea el archivo; si existe, falla
    f.write(datos)
huella = sha_archivo(destino)
if huella != hashlib.sha256(datos).hexdigest():
    parar("El archivo escrito no coincide con lo que se quiso escribir. Avísame.")
print("\nEnmienda D registrada en", destino)
print("  fecha y hora            :", D["fecha"])
print("  bytes                   :", len(datos))
print("  huella SHA-256 completa :", huella)
print("  16 primeros caracteres  :", huella[:16])
print("\nAhora: copia la huella completa y mándala por correo a la tutora y a tus compañeros hoy mismo,")
print("y pégame esta salida para anotar la enmienda en el proyecto.")
print("Recién ahora puedes crear C:\\SERCOP_FINAL\\revision_h3_llenas\\ y copiar ahí las dos hojas con los nombres")
print("revisor_A.xlsx y revisor_B.xlsx (sin el 'para_' del principio). Después sigue la celda 1 del cuaderno 19.")
