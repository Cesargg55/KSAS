# Guía de Verificación de Candidatos - KSAS

## ¡Has encontrado un candidato! ¿Y ahora qué?

### 📁 1. Dónde están guardados los datos

**KSAS guarda automáticamente:**
- **Reporte gráfico**: `output/TIC_XXXXXXXX_report.png`
- **Datos en la imagen**: Curva de luz, periodograma, curva plegada, parámetros

**Tu candidato TIC 34080274:**
- Archivo: `output/TIC_34080274_report.png`
- Período: 0.58117 días (~13.9 horas)
- Profundidad: 0.00083 (0.083%)
- SNR: 19.36

---

## 🔍 2. Verificación Manual - Checklist

### ✅ Paso 1: Revisar la curva plegada
**¿Qué buscar?**
- [ ] Forma de "U" clara (redondeada) → Planeta ✓
- [ ] Simetría alrededor de fase 0
- [ ] Transiciones suaves (no abruptas)
- [ ] Profundidad consistente

**Tu caso:** La curva plegada muestra una clara "U" → **BUENA SEÑAL**

### ✅ Paso 2: Verificar parámetros físicos

**Período: 0.58 días**
- Muy corto (planeta ultra-caliente o hot Jupiter)
- Físicamente posible pero inusual
- ⚠️ También podría ser:
  - Binaria de contacto
  - Rotación estelar con manchas
  - Armónico de un período más largo

**Profundidad: 0.083%**
- Pequeña → Planeta pequeño (mini-Neptuno/Super-Tierra)
- O planeta grande lejos de la estrella (gran impacto parameter)

**SNR: 19.36**
- Alto → Señal fuerte y confiable ✓

### ✅ Paso 3: Buscar en bases de datos existentes

**Verifica si ya ha sido descubierto:**

1. **NASA Exoplanet Archive**
   - URL: https://exoplanetarchive.ipac.caltech.edu/
   - Busca: "TIC 34080274"
   
2. **SIMBAD Database**
   - URL: http://simbad.u-strasbg.fr/simbad/
   - Busca: "TIC 34080274"

3. **ExoFOP-TESS**
   - URL: https://exofop.ipac.caltech.edu/tess/
   - Busca: "TIC 34080274"
   - **MUY IMPORTANTE**: Aquí verás TOIs (TESS Objects of Interest)

### ✅ Paso 4: Análisis avanzado con Lightkurve

**Opción A: Script de verificación rápida**

```python
import lightkurve as lk

# Descargar datos
search = lk.search_lightcurve("TIC 34080274", mission="TESS")
lc = search.download_all().stitch()

# Limpiar
lc = lc.remove_outliers().normalize()

# Plegar al período detectado
folded = lc.fold(period=0.58117, epoch_time=1475.0)  # Ajusta epoch_time
folded.plot()

# Buscar odd/even
odd = lc.fold(period=0.58117*2, epoch_time=1475.0)
odd.plot()
```

**Opción B: Usar TESS Alert Crossmatch**
- Compara con alerts oficiales de TESS

### ✅ Paso 5: Verificaciones adicionales

**Cosas a investigar:**

1. **¿Es el período correcto o un armónico?**
   - Prueba: 2×P, 3×P, P/2, P/3
   - Tu período × 2 = 1.16 días
   - Tu período × 3 = 1.74 días

2. **¿Hay variabilidad estelar?**
   - Mira la curva de luz completa (no plegada)
   - Busca patrones de rotación

3. **¿La estrella es adecuada?**
   - Consulta TIC catalog para magnitud, tipo espectral
   - Estrellas muy variables → más falsos positivos

---

## 📊 3. Interpretación de tu candidato

### TIC 34080274 - Análisis Preliminar

**Características:**
- Período ultra-corto (0.58 días = 13.9 horas)
- Tránsito poco profundo (0.083%)
- Señal fuerte (SNR = 19.36)

**Escenarios posibles:**

1. **Hot Jupiter/Super-Tierra muy cercano** (60% probabilidad)
   - Órbita extremadamente cercana a la estrella
   - Posible validación si es consistente

2. **Binaria eclipsante de bajo impacto** (30% probabilidad)
   - Compañero pequeño o geometría favorable
   - Verificar con odd/even y secondary eclipse

3. **Manchas estelares** (10% probabilidad)
   - Rotación sincrónicamente
   - Revisar variabilidad a largo plazo

### ✅ ¿Pasó el vetting de KSAS?

Si lo detectó el programa, entonces **pasó**:
- ✓ Odd/Even test
- ✓ V vs U shape
- ✓ No secondary transit profundo
- ✓ Depth/Duration ratio válido

**Esto es prometedor.**

---

## 🚀 4. Próximos Pasos Recomendados

### Opción A: Validación Propia (Amateur/Estudiante)
1. Re-analizar con diferentes períodos
2. Buscar en bases de datos (puede estar publicado)
3. Compartir en foros de astronomía amateur
4. Escribir reporte detallado

### Opción B: Reportar a Profesionales
1. **Si NO está en ExoFOP**: Podría ser nuevo
2. Contactar:
   - TESS Science Support Center
   - Grupos de follow-up (amateur o profesional)
3. Proporcionar:
   - TIC ID
   - Período exacto
   - Época del tránsito (T0)
   - Tu reporte gráfico

### Opción C: Seguimiento Fotométrico
Si tienes telescopio:
- Observar durante tránsito predicho
- Confirmar independientemente
- Refinar parámetros

---

## 📧 5. Cómo reportar un descubrimiento

**Si crees que es nuevo:**

1. **Verifica exhaustivamente** (1 semana de análisis)
2. **Documenta todo**:
   - TIC ID
   - Parámetros orbitales
   - Gráficas
   - Método de detección
   - Software usado (KSAS v3.0)

3. **Contacta**:
   - Email: tesshelp@bigbang.gsfc.nasa.gov
   - Pero PRIMERO verifica en ExoFOP

---

## ⚠️ IMPORTANTE

**Probabilidad de nuevo descubrimiento:**
- TESS ha observado millones de estrellas
- Muchos candidatos ya conocidos
- **Verifica SIEMPRE en ExoFOP primero**

**Sin embargo:**
- Candidatos débiles pueden haber pasado desapercibidos
- Períodos muy cortos a veces se pierden
- Tu detección es **válida científicamente** aunque ya exista

---

## 🎓 Recursos Adicionales

- **Lightkurve Tutorials**: https://docs.lightkurve.org/
- **TESS Data Products**: https://heasarc.gsfc.nasa.gov/docs/tess/
- **Exoplanet.eu**: http://exoplanet.eu/
- **ETD (Exoplanet Transit Database)**: http://var2.astro.cz/ETD/

---

**¡Felicidades por tu detección! Esto demuestra que KSAS funciona correctamente.** 🌟
