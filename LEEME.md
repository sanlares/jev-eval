# Benchmark para evaluar a Jev (TypeSafe)

Un set de preguntas con **respuesta correcta conocida** (ground truth) para medir si Jev clasifica y puntúa tan bien
como dice, comparado con Claude Haiku 4.5. Todo el texto es sintético, en inglés y con nombres ficticios.

## Qué contiene

| Grupo | Qué pregunta | Tareas | Ítems |
|---|---|---|---|
| Choice | "¿Cuál de estas opciones?" (5 a 20 opciones) | 10: tickets de soporte, emociones, noticias, cocina, papers, smart home, síntomas, programación, moderación, reseñas de hotel | 500 |
| Score | "¿En qué nivel de esta escala?" (3 a 7 niveles) | 10: severidad de bugs, frustración, formalidad, complejidad, cortesía, urgencia, relevancia de respuestas, estrellas, riesgo, experiencia | 500 |
| Noul | "¿Sí o no?" (50% sí, 50% no) | 10: pide reembolso, datos personales, RAG, citas, mismo producto, phishing, problema de envío, pide humano, tareas asignadas, evento ocurrido | 500 |
| Tweets | Sentimiento sobre acciones, de muy bajista (0) a muy alcista (4), preguntado de 3 formas | 1 (tu pedido) | 150 |
| Alucinación | ¿Admite "no se puede saber" cuando el texto no tiene la respuesta? | H01 (Choice con opción "no se puede determinar"), H02 (Noul: lo ideal es P = 0,5) | 120 |

Los tweets usan empresas y tickers inventados. La etiqueta es la **dirección que sugiere el tweet**, no lo que pasó
después con la acción. Para predecir retornos reales harían falta tweets y precios reales.

## Cómo se construyó la ground truth (5 pasos)

1. **Etiqueta primero.** Un script sorteó de antemano la etiqueta, la dificultad y el estilo de cada ítem
   (`data/plan/`). El texto se escribe después, para que encaje con esa etiqueta.
2. **Redacción.** Agentes Sonnet escribieron los textos siguiendo un instructivo por tarea (`data/briefs/gen_*.md`).
3. **Verificación a ciegas.** Otro agente Sonnet etiquetó cada texto **sin ver la etiqueta** (`data/verify/`).
4. **Adjudicación.** Yo (Claude Opus) revisé cada desacuerdo y cada caso marcado como ambiguo, y decidí mantener,
   reetiquetar o descartar. Cada decisión queda anotada con su motivo en `data/review/decisions.jsonl`.
5. **Auditoría.** Revisé además un 5% al azar de los ítems en los que hubo acuerdo, para estimar cuántos errores
   se escapan.

Haiku (el modelo de comparación) no participó en ningún paso, así que no juega con ventaja. Los números de cada
paso, por tarea, están en `data/final/DATASET.md`.

## Por qué este tamaño

- Con **500 ítems por grupo**, la accuracy se estima con un margen de aproximadamente ±4 puntos.
- Hay **10 tareas por grupo** porque "Jev clasifica bien" es una afirmación sobre tareas en general, no sobre una
  sola. Los intervalos del reporte tienen en cuenta que las tareas difieren entre sí: son un poco más anchos, pero
  honestos.
- 500 ítems alcanzan para detectar una diferencia de 5 puntos entre Jev y Haiku, si la hay.
- Mirado por tarea (50 ítems), el margen es de ±11 puntos. Sirve para ver dónde falla, no para sacar conclusiones.

## Validalo vos mismo

1. Abrí `data/final/revision_humana.csv` en Excel o Google Sheets. Tiene 3 ítems por tarea, mezclados y **sin la
   respuesta**.
2. Completá la columna `tu_respuesta` según lo que diga la columna `opciones`: el nombre de la opción, el número de
   nivel, o `true` / `false` / `unknown`.
3. Corré:

   ```bash
   python3 build.py human-check
   ```

   Te muestra tu porcentaje de coincidencia con la ground truth y la lista de desacuerdos. Si coincidís en más del
   ~90%, la ground truth es confiable. Si no, mirá los desacuerdos y su motivo en `data/review/decisions.jsonl`.
4. Todos los datos, con todas las columnas, están en `data/final/*.csv` (`dataset_completo.csv` los junta):
   - `texto`, `pregunta` y `opciones`: lo que ve el modelo.
   - `label`: la respuesta correcta.
   - `difficulty` y `hard_type`: qué tan difícil es y por qué.
   - `review`: si yo lo revisé a mano (`queue` = había desacuerdo, `audit` = muestra al azar).

## Cómo correr la evaluación

```bash
cd jev_eval
export TYPESAFE_API_KEY=...        # console.typesafe.ai
export ANTHROPIC_API_KEY=...       # para el baseline de Haiku
.venv/bin/python run_jev.py --dry-run          # valida todo sin gastar
.venv/bin/python run_jev.py --repeat 100       # Jev (cuesta menos de US$0,05); repite 100 ítems para ver si es determinista
.venv/bin/python run_baseline.py               # Haiku 4.5 (aprox. US$1-2)
.venv/bin/python analyze.py                    # genera results/report.md
```

Los tres scripts se pueden cortar y volver a correr: retoman donde quedaron.

## Cómo leer `results/report.md`

Empezá por **"Resumen simple"**:

- **Accuracy [IC 95%]**: el porcentaje de aciertos y el rango en el que está el valor real con 95% de confianza.
  En las escalas (Score y tweets) cuenta como acierto quedar **a ±1 nivel** de la respuesta correcta, y el nivel
  exacto aparece como métrica secundaria (`jev_exact`). La razón es tu revisión: en las escalas coincidiste
  exactamente en 6 de 12 ítems, pero en 11 de 12 dentro de ±1 nivel. El nivel exacto es subjetivo incluso para
  personas.
- **Referencia humana**: tu revisión a ciegas aparece en el reporte como techo de referencia.
- **¿Jev distinto de Haiku?**: "sí" solo si la diferencia es estadísticamente significativa.
- **¿Probabilidades calibradas?** TypeSafe dice que cuando Jev da 80%, acierta el 80% de las veces. Esto lo pone a
  prueba descontando el ruido natural por el tamaño de la muestra. "No (p<0,05)" quiere decir que Jev está
  demasiado seguro, o demasiado poco, más allá de lo explicable por azar.
- **Alucinación**:
  - Cuánto elige "no se puede determinar" cuando corresponde (más es mejor).
  - Cuánto lo elige cuando sí había respuesta (menos es mejor).
  - En Noul, qué porcentaje de preguntas sin información responde con confianza (P < 0,2 o P > 0,8). Menos es mejor.

Después vienen los desgloses: por tarea, por dificultad, por tipo de trampa (sarcasmo, negación, números, texto
largo irrelevante…) y por cantidad de opciones. Ahí se ve **dónde** falla.

## Limitaciones (leelas antes de sacar conclusiones)

- **Estilo Claude.** Los textos los escribieron modelos Claude. Los textos reales pueden ser más sucios o más
  ambiguos.
- **Etiquetas claras a propósito.** Se descartaron los casos genuinamente ambiguos, así que el benchmark mide
  aciertos sobre casos con una respuesta defendible. Una accuracy alta acá no garantiza lo mismo en datos reales.
- **Efecto techo.** El verificador (Sonnet) coincidió casi siempre, así que muchos ítems son "fáciles" para un
  modelo fuerte. Si Jev y Haiku sacan ~95%, las diferencias finas van a ser difíciles de ver.
- **Haiku no da probabilidades.** Por eso la calibración y H02 "sin información" solo se miden para Jev.
- **Congelado.** Las preguntas (`specs.py`) y el análisis (`analyze.py`) quedaron fijos antes de correr Jev.
  Si ajustás los prompts mirando los resultados, las conclusiones dejan de valer para datos nuevos.
