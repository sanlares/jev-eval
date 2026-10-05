# Ficha del dataset (generada por `build.py final`)

Items finales: **1770** (choice: 500, score: 500, noul: 500, tweets: 150, hallucination: 120).

Cada item paso por: plan con etiqueta fijada de antemano -> texto escrito por un agente -> etiquetado a ciegas por otro agente -> adjudicacion humana-supervisada (Claude Opus) de todo desacuerdo o caso marcado como ambiguo -> auditoria aleatoria del 5% de los casos en acuerdo.

- Casos revisados en adjudicacion: 285 (mantenidos 183, reetiquetados 25, descartados 77).
- Auditoria aleatoria: 92 items revisados, 0 con error. Cota superior (95%) del error de etiqueta en items no adjudicados: ~3.3%.

| tarea | generados | finales | acuerdo exacto verificador | kappa | reetiquetados | descartados |
|---|---|---|---|---|---|---|
| C01 | 55 | 50 | 1.0 | 1.0 | 0 | 1 |
| C02 | 58 | 50 | 0.983 | 0.979 | 0 | 2 |
| C03 | 60 | 50 | 0.95 | 0.943 | 0 | 3 |
| C04 | 58 | 50 | 1.0 | 1.0 | 0 | 0 |
| C05 | 62 | 50 | 0.984 | 0.982 | 0 | 1 |
| C06 | 70 | 50 | 1.0 | 1.0 | 0 | 1 |
| C07 | 56 | 50 | 1.0 | 1.0 | 0 | 1 |
| C08 | 64 | 50 | 1.0 | 1.0 | 0 | 2 |
| C09 | 55 | 50 | 0.982 | 0.977 | 0 | 1 |
| C10 | 56 | 50 | 1.0 | 1.0 | 0 | 0 |
| S01 | 58 | 50 | 0.983 | 0.977 | 1 | 1 |
| S02 | 65 | 50 | 0.862 | 0.827 | 5 | 3 |
| S03 | 63 | 50 | 0.857 | 0.822 | 4 | 5 |
| S04 | 58 | 50 | 0.948 | 0.931 | 1 | 2 |
| S05 | 64 | 50 | 0.812 | 0.766 | 7 | 5 |
| S06 | 56 | 50 | 1.0 | 1.0 | 0 | 1 |
| S07 | 69 | 50 | 0.812 | 0.75 | 3 | 10 |
| S08 | 55 | 50 | 0.982 | 0.977 | 1 | 0 |
| S09 | 63 | 50 | 0.857 | 0.81 | 3 | 6 |
| S10 | 57 | 50 | 0.825 | 0.795 | 0 | 0 |
| N01 | 56 | 50 | 1.0 | 1.0 | 0 | 0 |
| N02 | 56 | 50 | 1.0 | 1.0 | 0 | 0 |
| N03 | 56 | 50 | 0.946 | 0.893 | 0 | 3 |
| N04 | 56 | 50 | 1.0 | 1.0 | 0 | 0 |
| N05 | 56 | 50 | 1.0 | 1.0 | 0 | 3 |
| N06 | 56 | 50 | 1.0 | 1.0 | 0 | 2 |
| N07 | 56 | 50 | 1.0 | 1.0 | 0 | 2 |
| N08 | 56 | 50 | 1.0 | 1.0 | 0 | 0 |
| N09 | 56 | 50 | 1.0 | 1.0 | 0 | 0 |
| N10 | 56 | 50 | 1.0 | 1.0 | 0 | 0 |
| T01 | 165 | 150 | 0.976 | 0.97 | 0 | 4 |
| H01 | 66 | 60 | 0.985 | 0.98 | 0 | 2 |
| H02 | 82 | 60 | 0.963 | 0.937 | 0 | 16 |

Notas: el 'acuerdo' se mide contra la etiqueta planeada ANTES de adjudicar. En escalas ordinales el desacuerdo suele ser de +-1 nivel. Los items marcados `topup: true` se agregaron para reponer niveles que quedaron cortos tras los descartes (dificultad media).
