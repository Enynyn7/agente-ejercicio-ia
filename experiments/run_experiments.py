"""
Experimentos del Agente de Recomendación de Ejercicio
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agent import AgenteEjercicio

agente = AgenteEjercicio()

EXPERIMENTOS = [
    {
        "id": 1,
        "descripcion": "Usuario con energía media, objetivo cardio (mini experimento del doc)",
        "entrada": {
            "energia": "media", "tiempo": 30, "objetivo": "cardio",
            "restricciones": "ninguna", "historial": ["caminar", "bicicleta"], "feedback": 4.0
        }
    },
    {
        "id": 2,
        "descripcion": "Usuario con lesión, necesita movilidad",
        "entrada": {
            "energia": "baja", "tiempo": 20, "objetivo": "movilidad",
            "restricciones": "lesion", "historial": ["yoga"], "feedback": 5.0
        }
    },
    {
        "id": 3,
        "descripcion": "Usuario con alta energía, quiere fuerza",
        "entrada": {
            "energia": "alta", "tiempo": 45, "objetivo": "fuerza",
            "restricciones": "ninguna", "historial": ["sentadillas", "peso muerto"], "feedback": 4.5
        }
    },
    {
        "id": 4,
        "descripcion": "Usuario con fatiga, tiempo muy limitado",
        "entrada": {
            "energia": "baja", "tiempo": 10, "objetivo": "recuperacion",
            "restricciones": "fatiga", "historial": ["foam roller"], "feedback": 3.5
        }
    },
    {
        "id": 5,
        "descripcion": "Usuario sin historial previo, exploración inicial",
        "entrada": {
            "energia": "media", "tiempo": 60, "objetivo": "fuerza",
            "restricciones": "ninguna", "historial": [], "feedback": 3.0
        }
    },
]

def correr_experimentos():
    output = []

    output.append("=" * 65)
    output.append("EXPERIMENTOS DEL AGENTE DE RECOMENDACIÓN DE EJERCICIO")
    output.append("=" * 65)

    resumen = []

    for exp in EXPERIMENTOS:
        output.append("\n" + "─" * 65)
        output.append(f"Experimento {exp['id']}: {exp['descripcion']}")
        output.append("─" * 65)

        resultado = agente.ejecutar(exp["entrada"])
        d = resultado["decision"]

        output.append(
            f"Entrada: energía={exp['entrada']['energia']}, "
            f"tiempo={exp['entrada']['tiempo']}min, "
            f"objetivo={exp['entrada']['objetivo']}, "
            f"restricción={exp['entrada']['restricciones']}"
        )
        output.append(f"Acción: {d['accion']}")
        output.append(f"Ejercicio: {d['ejercicio']} ({d['intensidad']}, {d['duracion']} min)")
        output.append(f"Score: {d['score']}")
        output.append(f"Top 3: {[(n, s) for s, n in d['top_candidatos']]}")

        resumen.append({
            "exp": exp["id"],
            "ejercicio": d["ejercicio"],
            "score": d["score"],
            "accion": d["accion"]
        })

    # métricas
    output.append("\n" + "=" * 65)
    output.append("RESUMEN DE MÉTRICAS")
    output.append("=" * 65)

    scores = [r["score"] for r in resumen]

    output.append(f"Score promedio: {sum(scores)/len(scores):.4f}")
    output.append(f"Score máximo: {max(scores):.4f}")
    output.append(f"Score mínimo: {min(scores):.4f}")
    output.append(f"Decisiones tomadas: {len(resumen)}")
    output.append(f"Ejercicios únicos: {len(set(r['ejercicio'] for r in resumen))}")

    # GUARDAR ARCHIVO (DENTRO de la función)
    ruta = os.path.join(os.path.dirname(__file__), "..", "results", "resultados.txt")

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(output))

    print("resultados fueron generados correctamente")
print("resultados fueron generados correctamente")

if __name__ == "__main__":
    correr_experimentos()
