# Algoritmo di Ribilanciamento

Questo documento descrive in dettaglio l'algoritmo implementato nel sistema.

## Panoramica

L'algoritmo di ribilanciamento è un processo deterministico in 8 step che trasforma un portafoglio dallo stato attuale allo stato target, rispettando vincoli pratici.

**Caratteristiche chiave**:
- ✅ Deterministico (stesso input → stesso output)
- ✅ Senza ottimizzazione numerica complessa
- ✅ Trasparente e spiegabile
- ✅ Tax-aware (gestione capital gain tax)
- ✅ Cash-flow neutral (cerca CF ≈ 0)

---

## Step 1: Calcolo dello Stato Attuale

### Obiettivo
Quantificare il valore e i pesi attuali di ogni strumento nel portafoglio.

### Formule

Per ogni strumento *i*:

```
Vᵢ = Qᵢ × Pᵢ
```

Dove:
- `Vᵢ` = valore attuale dello strumento *i* (€)
- `Qᵢ` = quantità di quote possedute
- `Pᵢ` = prezzo corrente per quota (€)

Valore totale del portafoglio:

```
V_tot = Σᵢ₌₁ᴺ Vᵢ
```

Peso percentuale attuale:

```
ŵᵢ = Vᵢ / V_tot
```

### Esempio

| Asset | Qᵢ | Pᵢ | Vᵢ | ŵᵢ |
|-------|-----|-----|-----|-----|
| VWCE | 50 | 100 | 5,000 | 45.45% |
| AGGH | 30 | 110 | 3,300 | 30.00% |
| EIMI | 20 | 135 | 2,700 | 24.55% |
| **TOTALE** | | | **11,000** | **100%** |

### Codice Python

```python
def compute_current_state(portfolio):
    for asset in portfolio.assets:
        asset.current_value = asset.quantity * asset.price
    
    total_value = sum(a.current_value for a in portfolio.assets)
    
    for asset in portfolio.assets:
        asset.current_weight = asset.current_value / total_value
    
    return total_value
```

---

## Step 2: Calcolo delle Deviazioni

### Obiettivo
Identificare quali asset sono sovrapesati (da vendere) e quali sono sottopesati (da comprare).

### Formula

```
Δwᵢ = ŵᵢ − wᵢ
```

### Interpretazione

- **Δwᵢ > 0**: Strumento sovrapesato → da vendere
- **Δwᵢ < 0**: Strumento sottopesato → da comprare
- **Δwᵢ = 0**: Strumento già a target → nessuna azione

### Esempio

| Asset | ŵᵢ | wᵢ (target) | Δwᵢ | Azione |
|-------|-----|-------------|-----|--------|
| VWCE | 45.45% | 60% | −14.55% | Comprare |
| AGGH | 30.00% | 25% | +5.00% | Vendere |
| EIMI | 24.55% | 15% | +9.55% | Vendere |

### Codice Python

```python
def compute_deviations(portfolio):
    deviations = {}
    for asset in portfolio.assets:
        deviation = asset.current_weight - asset.target_weight
        deviations[asset.symbol] = deviation
        asset.deviation = deviation
    return deviations
```

---

## Step 3: Calcolo del Valore Target

### Obiettivo
Trasformare le deviazioni percentuali in variazioni di valore in euro.

### Formula

```
ΔVᵢ = (wᵢ × V_tot) − Vᵢ
```

Alternativamente:

```
ΔVᵢ = Δwᵢ × V_tot
```

### Esempio

| Asset | wᵢ | V_tot | Vᵢ | ΔVᵢ |
|-------|-----|-------|-----|-----|
| VWCE | 60% | 11,000 | 5,000 | +1,600 |
| AGGH | 25% | 11,000 | 3,300 | −550 |
| EIMI | 15% | 11,000 | 2,700 | −1,050 |

**Verifica**: Σᵢ ΔVᵢ = 1,600 − 550 − 1,050 = 0 ✅

### Codice Python

```python
def compute_target_values(portfolio, total_value):
    for asset in portfolio.assets:
        target_value = asset.target_weight * total_value
        asset.delta_value = target_value - asset.current_value
```

---

## Step 4: Conversione in Quote

### Obiettivo
Trasformare le variazioni di valore in quantità di quote da comprare/vendere.

### Formula

```
ΔQᵢ = ΔVᵢ / Pᵢ
```

### Esempio

| Asset | ΔVᵢ | Pᵢ | ΔQᵢ |
|-------|-----|-----|-----|
| VWCE | +1,600 | 100 | +16.00 |
| AGGH | −550 | 110 | −5.00 |
| EIMI | −1,050 | 135 | −7.78 |

### Codice Python

```python
def compute_quantity_changes(portfolio):
    for asset in portfolio.assets:
        asset.delta_quantity = asset.delta_value / asset.price
```

---

## Step 5: Calcolo del Cash Flow con Tassazione

### Obiettivo
Determinare la liquidità generata dalle vendite (al netto delle tasse) e quella necessaria per gli acquisti.

### Formule

#### Per vendite (ΔQᵢ < 0)

```
cash_inᵢ = |ΔQᵢ| × Pᵢ × (1 − Tᵢ × max(0, Pᵢ − PMCᵢ))
```

**Spiegazione dettagliata**:

1. `|ΔQᵢ| × Pᵢ` = ricavo lordo della vendita
2. `Pᵢ − PMCᵢ` = capital gain per quota (può essere negativo)
3. `max(0, Pᵢ − PMCᵢ)` = capital gain tassabile (solo se > 0)
4. `Tᵢ × max(0, Pᵢ − PMCᵢ)` = tassa per quota
5. `1 − Tᵢ × max(0, Pᵢ − PMCᵢ)` = fattore di ritenzione

**Casi speciali**:
- Se `Pᵢ ≤ PMCᵢ` (vendita in perdita): `cash_inᵢ = |ΔQᵢ| × Pᵢ` (nessuna tassa)
- Se `Pᵢ > PMCᵢ` (vendita in guadagno): si applica la tassazione sul capital gain

#### Per acquisti (ΔQᵢ > 0)

```
cash_outᵢ = ΔQᵢ × Pᵢ
```

(Nessuna complicazione: paghi il prezzo di mercato)

#### Cash flow totale

```
CF = Σᵢ cash_inᵢ − Σᵢ cash_outᵢ
```

### Esempio

**Ipotesi**: PMC di AGGH = 108, PMC di EIMI = 130, T = 26%

| Asset | ΔQᵢ | Tipo | Calcolo | Cash |
|-------|-----|------|---------|------|
| VWCE | +16.00 | Acquisto | 16 × 100 | −1,600.00 |
| AGGH | −5.00 | Vendita | 5 × 110 × (1 − 0.26×2) | +537.40 |
| EIMI | −7.78 | Vendita | 7.78 × 135 × (1 − 0.26×5) | +932.86 |
| **CF** | | | | **−129.74** |

**Risultato**: CF = −129.74€ (deficit)

### Codice Python

```python
def compute_cash_flow(portfolio):
    cash_in = 0
    cash_out = 0
    
    for asset in portfolio.assets:
        if asset.delta_quantity < 0:  # Vendita
            qty_sold = abs(asset.delta_quantity)
            capital_gain = max(0, asset.price - asset.avg_cost)
            tax_factor = 1 - asset.tax_rate * capital_gain
            cash_in += qty_sold * asset.price * tax_factor
        
        elif asset.delta_quantity > 0:  # Acquisto
            cash_out += asset.delta_quantity * asset.price
    
    return cash_in - cash_out
```

---

## Step 6: Chiusura del Cash Flow

### Obiettivo
Azzerare (o minimizzare) il cash flow per evitare apporti/prelievi esterni.

### Problema

Se CF ≠ 0:
- CF < 0: servono più soldi per comprare di quanti ne generano le vendite
- CF > 0: le vendite generano più liquidità del necessario

### Soluzione: Scalatura Proporzionale

**Idea**: Scalare proporzionalmente solo gli acquisti per bilanciare il CF.

**Formula**:

```
ΔQᵢ,adjusted = ΔQᵢ × (1 + CF / Σⱼ cash_outⱼ)    per ΔQᵢ > 0
ΔQᵢ,adjusted = ΔQᵢ                                  per ΔQᵢ ≤ 0
```

**Nota**: Usiamo `1 + CF/total_cash_out` perché:
- Se CF < 0 (deficit), il fattore < 1 → riduciamo gli acquisti
- Se CF > 0 (surplus), il fattore > 1 → aumentiamo gli acquisti

### Esempio

Dal nostro esempio: CF = −129.74€, cash_out_tot = 1,600€

```
fattore = 1 + (−129.74 / 1,600) = 1 − 0.081 = 0.919
```

Nuove quantità:

| Asset | ΔQᵢ originale | Tipo | ΔQᵢ,adjusted |
|-------|---------------|------|---------------|
| VWCE | +16.00 | Acquisto | 16.00 × 0.919 = 14.70 |
| AGGH | −5.00 | Vendita | −5.00 (invariato) |
| EIMI | −7.78 | Vendita | −7.78 (invariato) |

**Nuovo CF**: 537.40 + 932.86 − (14.70 × 100) ≈ 0 ✅

### Perché non ottimizzazione complessa?

Potremmo usare solver numerici per distribuire l'aggiustamento in modo "ottimale", ma:
- Aggiungerebbe complessità
- Non sarebbe più deterministico
- La differenza pratica è minima
- Violterebbe la filosofia di semplicità del progetto

### Codice Python

```python
def close_cash_flow(portfolio, cash_flow):
    if abs(cash_flow) < 0.01:  # Tolleranza
        return  # Già bilanciato
    
    # Calcola totale cash out
    total_cash_out = sum(
        asset.delta_quantity * asset.price
        for asset in portfolio.assets
        if asset.delta_quantity > 0
    )
    
    if total_cash_out == 0:
        return  # Non ci sono acquisti da scalare
    
    # Fattore di scalatura
    scale_factor = 1 + cash_flow / total_cash_out
    
    # Applica solo agli acquisti
    for asset in portfolio.assets:
        if asset.delta_quantity > 0:
            asset.delta_quantity *= scale_factor
```

---

## Step 7: Simulazione Post-Ribilanciamento

### Obiettivo
Calcolare lo stato del portafoglio dopo aver applicato le operazioni.

### Formule

```
Qᵢ,new = Qᵢ + ΔQᵢ,adjusted
Vᵢ,new = Qᵢ,new × Pᵢ
V_tot,new = Σᵢ Vᵢ,new
ŵᵢ,new = Vᵢ,new / V_tot,new
```

### Esempio

| Asset | Qᵢ | ΔQᵢ | Qᵢ,new | Vᵢ,new | ŵᵢ,new | wᵢ (target) |
|-------|-----|-----|--------|--------|--------|-------------|
| VWCE | 50 | +14.70 | 64.70 | 6,470 | 59.50% | 60% |
| AGGH | 30 | −5.00 | 25.00 | 2,750 | 25.29% | 25% |
| EIMI | 20 | −7.78 | 12.22 | 1,650 | 15.17% | 15% |
| **TOT** | | | | **10,870** | **100%** | **100%** |

**Osservazione**: Non siamo perfettamente a target, ma molto vicini!

### Codice Python

```python
def simulate_post_rebalancing(portfolio):
    results = []
    
    for asset in portfolio.assets:
        new_qty = asset.quantity + asset.delta_quantity
        new_value = new_qty * asset.price
        results.append({
            'symbol': asset.symbol,
            'new_quantity': new_qty,
            'new_value': new_value
        })
    
    total_new_value = sum(r['new_value'] for r in results)
    
    for r in results:
        r['new_weight'] = r['new_value'] / total_new_value
    
    return results
```

---

## Step 8: Arrotondamento a Quote Intere

### Obiettivo
Adattare le quantità continue a quote intere (quando richiesto).

### Problema

Fino a questo punto, ΔQᵢ può essere un numero decimale (es. 14.70 quote). Ma nella realtà molti strumenti si comprano a quote intere.

### Soluzioni (Policy)

1. **Troncamento** (floor)
   ```
   ΔQᵢ,rounded = ⌊ΔQᵢ⌋
   ```
   Esempio: 14.70 → 14

2. **Arrotondamento matematico** (round)
   ```
   ΔQᵢ,rounded = round(ΔQᵢ)
   ```
   Esempio: 14.70 → 15

3. **Arrotondamento per eccesso** (ceiling)
   ```
   ΔQᵢ,rounded = ⌈ΔQᵢ⌉
   ```
   Esempio: 14.70 → 15

### Conseguenze

Dopo l'arrotondamento:
- Il cash flow non sarà più esattamente zero
- I pesi non saranno perfettamente a target

**Azione**: Ricalcolare CF e deviazioni residue e riportarle all'utente.

### Policy di Default

Di default, usiamo **arrotondamento matematico** (round).

### Codice Python

```python
from enum import Enum
import math

class RoundingPolicy(Enum):
    FLOOR = 'floor'
    ROUND = 'round'
    CEIL = 'ceil'

def apply_rounding(portfolio, policy=RoundingPolicy.ROUND):
    for asset in portfolio.assets:
        if policy == RoundingPolicy.FLOOR:
            asset.delta_quantity = math.floor(asset.delta_quantity)
        elif policy == RoundingPolicy.ROUND:
            asset.delta_quantity = round(asset.delta_quantity)
        elif policy == RoundingPolicy.CEIL:
            asset.delta_quantity = math.ceil(asset.delta_quantity)
```

---

## Diagramma di Flusso

```
┌─────────────────────────┐
│  Input: Portfolio       │
│  (Q, P, PMC, T, w)     │
└───────────┬─────────────┘
            │
            ▼
  ┌─────────────────────┐
  │ Step 1: Stato attuale│
  │  V, ŵ, V_tot        │
  └─────────┬───────────┘
            │
            ▼
  ┌─────────────────────┐
  │ Step 2: Deviazioni  │
  │  Δw = ŵ − w        │
  └─────────┬───────────┘
            │
            ▼
  ┌─────────────────────┐
  │ Step 3: Valore target│
  │  ΔV = Δw × V_tot   │
  └─────────┬───────────┘
            │
            ▼
  ┌─────────────────────┐
  │ Step 4: Quote       │
  │  ΔQ = ΔV / P       │
  └─────────┬───────────┘
            │
            ▼
  ┌─────────────────────┐
  │ Step 5: Cash flow   │
  │  CF con tassazione  │
  └─────────┬───────────┘
            │
            ▼
        ┌───────┐
        │CF ≈ 0?│
        └───┬───┘
            │ No
            ▼
  ┌─────────────────────┐
  │ Step 6: Chiusura CF │
  │  Scalatura acquisti │
  └─────────┬───────────┘
            │
            ▼
  ┌─────────────────────┐
  │ Step 7: Simulazione │
  │  Q_new, ŵ_new      │
  └─────────┬───────────┘
            │
            ▼
  ┌─────────────────────┐
  │ Step 8: Arrotondamento│
  │  (se richiesto)     │
  └─────────┬───────────┘
            │
            ▼
   ┌────────────────────┐
   │ Output: Operazioni │
   │  ΔQ per ogni asset │
   └────────────────────┘
```

---

## Invarianti e Proprietà

### Invarianti matematiche

1. **Somma dei pesi = 100%**
   ```
   Σᵢ wᵢ = 1
   Σᵢ ŵᵢ = 1
   Σᵢ ŵᵢ,new = 1
   ```

2. **Somma delle variazioni di valore = 0** (prima della chiusura CF)
   ```
   Σᵢ ΔVᵢ = 0
   ```

3. **Cash flow ideale = 0** (dopo step 6)
   ```
   Σᵢ cash_inᵢ − Σᵢ cash_outᵢ ≈ 0
   ```

### Proprietà desiderabili

1. **Determinismo**: Stesso input → stesso output
2. **Spiegabilità**: Ogni passaggio è ricostruibile
3. **Efficienza**: O(N) complessità temporale
4. **Robustezza**: Gestione di casi edge (portafoglio vuoto, target 100% su un asset, ecc.)

---

## Limiti e Assunzioni

### Assunzioni

1. **Prezzi costanti**: I prezzi non cambiano durante l'esecuzione delle operazioni
2. **Liquidità infinita**: Posso comprare/vendere qualsiasi quantità
3. **No costi di transazione**: Oltre alle tasse, non ci sono commissioni
4. **Esecuzione istantanea**: Tutte le operazioni avvengono simultaneamente
5. **PMC noto**: Il prezzo medio di carico è disponibile

### Limiti

1. **Non ottimizza**: Scalatura proporzionale, non ottimizzazione numerica
2. **Monovaluta**: Tutti i prezzi nella stessa valuta
3. **Tassazione semplificata**: Capital gain tax lineare, no loss harvesting
4. **No vincoli di lotto**: Non considera lotti minimi o multipli

### Possibili estensioni future

- Gestione di vincoli di lotto (es. multipli di 100)
- Tax loss harvesting
- Prioritizzazione degli acquisti in base a criteri
- Gestione multi-valuta con tassi di cambio
- Considerazione dei costi di transazione

---

## Validazione

### Test unitari

Ogni step deve essere testato individualmente con:
- Casi normali
- Casi edge (portafoglio con 1 asset, tutti target a 0 tranne uno, ecc.)
- Casi di errore (somma dei target ≠ 100%, prezzi negativi, ecc.)

### Test di integrazione

L'algoritmo completo deve essere testato end-to-end con:
- Portafogli reali
- Verificare che le invarianti siano rispettate
- Controllare che CF finale sia vicino a 0
- Validare che ŵᵢ,new ≈ wᵢ

### Property-based testing

Usare framework come Hypothesis per generare automaticamente casi di test e verificare proprietà universali.
