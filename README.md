# Agente Inteligente de Recomendación de Ejercicio
**UDLAP — Inteligencia Artificial | Entrega 3**  
Equipo: Enya Flores Villicana (179938) · Santiago Jiménez Morales (179915) · Brandon Yahir Castro Ramos (179842)

---

## Descripción del proyecto

Sistema de agente inteligente que genera recomendaciones personalizadas de ejercicio a partir del estado físico del usuario. El agente implementa el ciclo:

```
Percepción → Estado → Decisión → Acción
```

El estado se representa como la tupla `S = (energía, tiempo, objetivo, restricciones, historial, feedback)` y la decisión se toma mediante:

```
a* = argmax f(s, a)
f(s, a) = w1·preferencia + w2·adecuación + w3·seguridad − w4·fatiga
```

---

## Estructura del proyecto

```
project/
├── src/
│   └── agent.py              # Lógica completa del agente
├── experiments/
│   └── run_experiments.py    # 5 experimentos con diferentes estados
├── results/
│   └── (generado al ejecutar experimentos)
└── README.md
```

---

## Dependencias

El proyecto usa únicamente la librería estándar de Python 3.8+. No requiere instalación de paquetes externos.

```bash
python --version   # Requiere Python 3.8 o superior
```

---

## Cómo ejecutar el sistema

### Ejemplo básico (mini experimento del documento)

```bash
python src/agent.py
```

Salida esperada:
```
=======================================================
  AGENTE DE RECOMENDACIÓN DE EJERCICIO
=======================================================
Estado actual:
  Energía     : media
  Tiempo      : 30 min
  Objetivo    : cardio
  Restricción : ninguna
  Historial   : ['caminar', 'bicicleta']
  Feedback    : 4.0/5.0

Acción seleccionada : a2 - recomendar rutina completa
Ejercicio           : bicicleta
Intensidad          : media
Duración            : 30 min
Score f(s,a)        : 0.85

Top 3 candidatos:
  bicicleta                 score: 0.85
  caminar                   score: 0.85
  correr                    score: 0.685

Justificación: Se seleccionó 'bicicleta' con score 0.8500. ...
```

### Ejecutar todos los experimentos

```bash
python experiments/run_experiments.py
```

### Usar el agente desde otro script

```python
from src.agent import AgenteEjercicio

agente = AgenteEjercicio()

resultado = agente.ejecutar({
    "energia": "media",
    "tiempo": 30,
    "objetivo": "cardio",
    "restricciones": "ninguna",
    "historial": ["caminar", "bicicleta"],
    "feedback": 4.0
})

print(resultado["decision"]["ejercicio"])    # → bicicleta
print(resultado["decision"]["score"])        # → 0.85
```

---

## Ejemplo de ejecución completo

```bash
$ python experiments/run_experiments.py

=================================================================
  EXPERIMENTOS DEL AGENTE DE RECOMENDACIÓN DE EJERCICIO
=================================================================

─────────────────────────────────────────────────────────────────
Experimento 1: Usuario con energía media, objetivo cardio
─────────────────────────────────────────────────────────────────
  Entrada  : energía=media, tiempo=30min, objetivo=cardio, restricción=ninguna
  Acción   : a2 - recomendar rutina completa
  Ejercicio: bicicleta (media, 30 min)
  Score    : 0.85
...

RESUMEN DE MÉTRICAS
  Score promedio     : 0.8115
  Score máximo       : 0.8825
  Score mínimo       : 0.7250
  Decisiones tomadas : 5
  Ejercicios únicos  : 5
```

---

## Técnicas de IA implementadas

| Componente | Técnica |
|---|---|
| Representación del estado | Tupla estructurada |
| Decisión base | Sistema basado en reglas |
| Evaluación de acciones | Función heurística ponderada `f(s,a)` |
| Preferencia de usuario | Aprendizaje por historial + feedback |

---

## Acciones del agente

| Acción | Descripción |
|---|---|
| `a1` | Recomendar ejercicio individual |
| `a2` | Recomendar rutina completa |
| `a3` | Ajustar intensidad |
| `a4` | Sugerir descanso activo |
| `a5` | Evitar ejercicio restringido |

---

## Métricas de evaluación

- **Score f(s,a):** calidad de la recomendación (0.0 – 1.0)
- **Tasa de aceptación:** % de recomendaciones seguidas por el usuario
- **Calificación promedio:** satisfacción del usuario (1–5)
- **Tiempo de decisión:** eficiencia del sistema
