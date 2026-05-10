"""
Agente Inteligente de Recomendación de Ejercicio
Equipo: Enya Flores Villicana, Santiago Jiménez Morales, Brandon Yahir Castro Ramos
UDLAP - Inteligencia Artificial - Entrega 3
"""

from dataclasses import dataclass, field
from typing import List, Optional
import random


# ─────────────────────────────────────────────
# DEFINICIÓN DEL ESTADO  S = (energía, tiempo, objetivo, restricciones, historial, feedback)
# ─────────────────────────────────────────────

@dataclass
class Estado:
    energia: str          # 'baja' | 'media' | 'alta'
    tiempo: int           # minutos disponibles [5, 120]
    objetivo: str         # 'fuerza' | 'cardio' | 'movilidad' | 'recuperacion'
    restricciones: str    # 'ninguna' | 'lesion' | 'fatiga' | 'molestia'
    historial: List[str] = field(default_factory=list)   # ejercicios recientes
    feedback: float = 3.0  # calificación previa del usuario [1.0 - 5.0]

    def __str__(self):
        return (
            f"Estado actual:\n"
            f"  Energía     : {self.energia}\n"
            f"  Tiempo      : {self.tiempo} min\n"
            f"  Objetivo    : {self.objetivo}\n"
            f"  Restricción : {self.restricciones}\n"
            f"  Historial   : {self.historial}\n"
            f"  Feedback    : {self.feedback}/5.0"
        )


# ─────────────────────────────────────────────
# BASE DE CONOCIMIENTO DE EJERCICIOS
# ─────────────────────────────────────────────

EJERCICIOS = [
    # nombre                 objetivo       intensidad  tiempo_min  restricciones_incompatibles
    ("sentadillas",         "fuerza",       "alta",     20,         ["lesion", "molestia"]),
    ("peso muerto",         "fuerza",       "alta",     25,         ["lesion"]),
    ("flexiones",           "fuerza",       "media",    15,         ["molestia"]),
    ("plancha",             "fuerza",       "media",    10,         []),
    ("bicicleta",           "cardio",       "media",    30,         ["lesion"]),
    ("correr",              "cardio",       "alta",     30,         ["lesion", "molestia"]),
    ("caminar",             "cardio",       "baja",     20,         []),
    ("saltar cuerda",       "cardio",       "alta",     20,         ["lesion", "fatiga"]),
    ("yoga",                "movilidad",    "baja",     30,         []),
    ("estiramientos",       "movilidad",    "baja",     15,         []),
    ("movilidad articular", "movilidad",    "baja",     20,         []),
    ("foam roller",         "recuperacion", "baja",     15,         []),
    ("respiración",         "recuperacion", "baja",     10,         []),
    ("caminata suave",      "recuperacion", "baja",     20,         []),
]


# ─────────────────────────────────────────────
# FUNCIÓN DE EVALUACIÓN  f(s, a) = w1·preferencia + w2·adecuación + w3·seguridad − w4·fatiga
# ─────────────────────────────────────────────

PESOS = {
    "w1": 0.25,   # preferencia  — coincidencia con historial
    "w2": 0.35,   # adecuación   — ajuste al objetivo y tiempo
    "w3": 0.30,   # seguridad    — penaliza restricciones
    "w4": 0.10,   # fatiga       — penaliza sobrecarga física
}

ENERGIA_VALOR = {"baja": 0.2, "media": 0.6, "alta": 1.0}
INTENSIDAD_VALOR = {"baja": 0.2, "media": 0.6, "alta": 1.0}


def calcular_preferencia(nombre: str, historial: List[str], feedback: float) -> float:
    """
    Calcula preferencia basada en historial del usuario.
    Si el ejercicio aparece en el historial reciente, el agente lo prefiere
    proporcionalmente al feedback previo.
    """
    if nombre in historial:
        return (feedback / 5.0)  # normalizado entre 0 y 1
    return 0.3  # puntaje base para ejercicios no vistos (exploración)


def calcular_adecuacion(objetivo_ejercicio: str, objetivo_usuario: str,
                         tiempo_ejercicio: int, tiempo_usuario: int) -> float:
    """
    Calcula qué tan bien se ajusta el ejercicio al objetivo y tiempo disponible.
    """
    coincide_objetivo = 1.0 if objetivo_ejercicio == objetivo_usuario else 0.0
    ajuste_tiempo = 1.0 if tiempo_ejercicio <= tiempo_usuario else max(0.0, 1.0 - (tiempo_ejercicio - tiempo_usuario) / 60.0)
    return (coincide_objetivo * 0.7) + (ajuste_tiempo * 0.3)


def calcular_seguridad(restricciones_ejercicio: List[str], restriccion_usuario: str) -> float:
    """
    Retorna 1.0 si es seguro, 0.0 si el ejercicio está contraindicado.
    """
    if restriccion_usuario in restricciones_ejercicio:
        return 0.0
    return 1.0


def calcular_fatiga(intensidad_ejercicio: str, energia_usuario: str) -> float:
    """
    Penaliza cuando la intensidad del ejercicio supera la energía del usuario.
    Retorna un valor de fatiga entre 0 y 1 (mayor = más fatiga = más penalización).
    """
    nivel_intensidad = INTENSIDAD_VALOR[intensidad_ejercicio]
    nivel_energia = ENERGIA_VALOR[energia_usuario]
    exceso = max(0.0, nivel_intensidad - nivel_energia)
    return exceso


def evaluar_accion(estado: Estado, ejercicio: tuple) -> float:
    """
    f(s, a) = w1·preferencia + w2·adecuación + w3·seguridad − w4·fatiga
    Aplica la función de evaluación completa para un par (estado, acción).
    """
    nombre, objetivo_ej, intensidad, tiempo_ej, restricciones_ej = ejercicio

    preferencia  = calcular_preferencia(nombre, estado.historial, estado.feedback)
    adecuacion   = calcular_adecuacion(objetivo_ej, estado.objetivo, tiempo_ej, estado.tiempo)
    seguridad    = calcular_seguridad(restricciones_ej, estado.restricciones)
    fatiga       = calcular_fatiga(intensidad, estado.energia)

    score = (
        PESOS["w1"] * preferencia +
        PESOS["w2"] * adecuacion  +
        PESOS["w3"] * seguridad   -
        PESOS["w4"] * fatiga
    )

    return round(score, 4)


# ─────────────────────────────────────────────
# SISTEMA DE REGLAS  (capa de conocimiento explícito)
# ─────────────────────────────────────────────

def aplicar_reglas(estado: Estado, ejercicio: tuple) -> bool:
    """
    Reglas duras que filtran ejercicios antes de evaluar con f(s,a).
    Retorna False si el ejercicio debe descartarse definitivamente.
    """
    nombre, objetivo_ej, intensidad, tiempo_ej, restricciones_ej = ejercicio

    # Regla 1: Si hay lesión, solo ejercicios de baja intensidad
    if estado.restricciones == "lesion" and intensidad != "baja":
        return False

    # Regla 2: Si la energía es baja, no recomendar alta intensidad
    if estado.energia == "baja" and intensidad == "alta":
        return False

    # Regla 3: Si el ejercicio está explícitamente contraindicado
    if estado.restricciones in restricciones_ej:
        return False

    # Regla 4: Si el tiempo es muy limitado (< 15 min), solo ejercicios cortos
    if estado.tiempo < 15 and tiempo_ej > estado.tiempo:
        return False

    return True


# ─────────────────────────────────────────────
# AGENTE PRINCIPAL  a* = argmax f(s, a)
# ─────────────────────────────────────────────

class AgenteEjercicio:
    """
    Agente inteligente de recomendación de ejercicio.
    Implementa el ciclo: Percepción → Estado → Decisión → Acción
    """

    def __init__(self):
        self.ejercicios = EJERCICIOS
        self.historial_decisiones = []  # registro de decisiones tomadas

    def percibir(self, datos: dict) -> Estado:
        """
        Construye el estado S a partir de los datos percibidos del entorno (usuario).
        """
        return Estado(
            energia      = datos.get("energia", "media"),
            tiempo       = datos.get("tiempo", 30),
            objetivo     = datos.get("objetivo", "cardio"),
            restricciones= datos.get("restricciones", "ninguna"),
            historial    = datos.get("historial", []),
            feedback     = datos.get("feedback", 3.0),
        )

    def decidir(self, estado: Estado) -> dict:
        """
        Selecciona la mejor acción: a* = argmax f(s, a)
        Paso 1: Filtrar ejercicios con reglas duras
        Paso 2: Evaluar cada ejercicio con f(s, a)
        Paso 3: Seleccionar el de mayor puntaje
        """
        candidatos = []

        for ejercicio in self.ejercicios:
            if aplicar_reglas(estado, ejercicio):
                score = evaluar_accion(estado, ejercicio)
                candidatos.append((score, ejercicio))

        if not candidatos:
            # Fallback: si no hay candidatos válidos, recomendar descanso
            return {
                "accion": "a4 - sugerir descanso activo",
                "ejercicio": "descanso activo",
                "intensidad": "baja",
                "duracion": min(estado.tiempo, 15),
                "score": 0.0,
                "top_candidatos": [],
                "justificacion": "No se encontraron ejercicios seguros para el estado actual."
            }

        # Ordenar por score descendente
        candidatos.sort(key=lambda x: x[0], reverse=True)
        mejor_score, mejor_ejercicio = candidatos[0]
        nombre, objetivo_ej, intensidad, tiempo_ej, _ = mejor_ejercicio

        # Determinar tipo de acción
        if objetivo_ej == estado.objetivo:
            accion = "a2 - recomendar rutina completa"
        elif mejor_score < 0.4:
            accion = "a4 - sugerir descanso activo"
        else:
            accion = "a1 - recomendar ejercicio"

        resultado = {
            "accion": accion,
            "ejercicio": nombre,
            "intensidad": intensidad,
            "duracion": min(tiempo_ej, estado.tiempo),
            "score": mejor_score,
            "top_candidatos": [(s, e[0]) for s, e in candidatos[:3]],
            "justificacion": self._generar_justificacion(estado, nombre, mejor_score)
        }

        # Registrar decisión
        self.historial_decisiones.append({
            "estado": estado,
            "resultado": resultado
        })

        return resultado

    def _generar_justificacion(self, estado: Estado, ejercicio: str, score: float) -> str:
        """Genera una explicación legible de la decisión tomada."""
        razon = f"Se seleccionó '{ejercicio}' con score {score:.4f}. "
        if estado.restricciones != "ninguna":
            razon += f"Se consideró la restricción '{estado.restricciones}'. "
        if estado.historial and ejercicio in estado.historial:
            razon += "Aparece en el historial del usuario (preferencia detectada). "
        razon += f"Objetivo: {estado.objetivo}, energía: {estado.energia}, tiempo: {estado.tiempo} min."
        return razon

    def ejecutar(self, datos_usuario: dict) -> dict:
        """
        Ciclo completo del agente: Percepción → Estado → Decisión → Acción
        """
        estado = self.percibir(datos_usuario)
        decision = self.decidir(estado)
        return {"estado": estado, "decision": decision}


# ─────────────────────────────────────────────
# EJECUCIÓN DE EJEMPLO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    agente = AgenteEjercicio()

    # Caso del mini experimento del documento
    entrada = {
        "energia": "media",
        "tiempo": 30,
        "objetivo": "cardio",
        "restricciones": "ninguna",
        "historial": ["caminar", "bicicleta"],
        "feedback": 4.0
    }

    print("=" * 55)
    print("  AGENTE DE RECOMENDACIÓN DE EJERCICIO")
    print("=" * 55)
    resultado = agente.ejecutar(entrada)

    print(resultado["estado"])
    print()
    d = resultado["decision"]
    print(f"Acción seleccionada : {d['accion']}")
    print(f"Ejercicio           : {d['ejercicio']}")
    print(f"Intensidad          : {d['intensidad']}")
    print(f"Duración            : {d['duracion']} min")
    print(f"Score f(s,a)        : {d['score']}")
    print(f"\nTop 3 candidatos:")
    for score, nombre in d["top_candidatos"]:
        print(f"  {nombre:<25} score: {score}")
    print(f"\nJustificación: {d['justificacion']}")
