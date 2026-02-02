# Definizioni Formali delle Variabili

Questo documento fornisce la definizione rigorosa di tutte le variabili utilizzate nel sistema.

## Convenzioni

- **Indice**: `i` rappresenta l'indice dello strumento finanziario (i = 1, 2, ..., N)
- **Unità di misura**: I valori monetari sono espressi in euro (€), salvo diversa indicazione
- **Percentuali**: Espresse come valori decimali (es. 0.26 per 26%, 0.6 per 60%)

## Variabili di Input

Queste sono le variabili che devono essere fornite dall'utente.

### N
**Tipo**: Intero  
**Descrizione**: Numero totale di strumenti nel portafoglio  
**Vincoli**: N ≥ 1  
**Esempio**: N = 5 (il portafoglio contiene 5 ETF)

### Qᵢ
**Tipo**: Numero decimale (può essere intero per quote intere)  
**Descrizione**: Quantità attuale di quote possedute dello strumento i  
**Vincoli**: Qᵢ ≥ 0  
**Unità**: quote  
**Esempio**: Q₁ = 50 (possiedo 50 quote del primo ETF)

### Pᵢ
**Tipo**: Numero decimale positivo  
**Descrizione**: Prezzo corrente di una quota dello strumento i  
**Vincoli**: Pᵢ > 0  
**Unità**: €/quota  
**Esempio**: P₁ = 100.50 €

### PMCᵢ
**Tipo**: Numero decimale positivo  
**Descrizione**: Prezzo medio di carico (average cost basis) dello strumento i  
**Vincoli**: PMCᵢ > 0  
**Unità**: €/quota  
**Uso**: Calcolo del capital gain per la tassazione  
**Esempio**: PMC₁ = 95.00 € (ho comprato in media a 95€/quota)

### Tᵢ
**Tipo**: Numero decimale  
**Descrizione**: Aliquota fiscale applicabile al capital gain dello strumento i  
**Vincoli**: 0 ≤ Tᵢ ≤ 1  
**Formato**: Valore decimale (es. 0.26 per il 26%)  
**Note speciali**:
- Se Pᵢ ≤ PMCᵢ (vendita in perdita), la tassazione effettiva è zero
- Tᵢ può variare per strumento (es. tassazione agevolata per alcuni bond)

**Esempio**: T₁ = 0.26 (26% di capital gain tax in Italia)

### wᵢ
**Tipo**: Numero decimale  
**Descrizione**: Percentuale target (desiderata) per lo strumento i nel portafoglio  
**Vincoli**: 
- 0 ≤ wᵢ ≤ 1 per ogni i
- Σᵢ wᵢ = 1 (la somma deve essere esattamente 100%)

**Esempio**: w₁ = 0.60 (voglio che il 60% del portafoglio sia in questo strumento)

---

## Variabili Derivate

Queste variabili sono calcolate automaticamente dal sistema.

### Vᵢ
**Tipo**: Numero decimale  
**Descrizione**: Valore attuale dello strumento i nel portafoglio  
**Formula**: `Vᵢ = Qᵢ × Pᵢ`  
**Unità**: €  
**Esempio**: V₁ = 50 × 100.50 = 5,025.00 €

### V_tot
**Tipo**: Numero decimale  
**Descrizione**: Valore totale del portafoglio  
**Formula**: `V_tot = Σᵢ Vᵢ`  
**Unità**: €  
**Esempio**: V_tot = 11,000.00 €

### ŵᵢ
**Tipo**: Numero decimale  
**Descrizione**: Peso percentuale attuale dello strumento i  
**Formula**: `ŵᵢ = Vᵢ / V_tot`  
**Vincoli**: 
- 0 ≤ ŵᵢ ≤ 1
- Σᵢ ŵᵢ = 1

**Interpretazione**: Indica quanto del portafoglio è attualmente allocato in questo strumento  
**Esempio**: ŵ₁ = 5,025 / 11,000 = 0.4568 (45.68%)

### Δwᵢ
**Tipo**: Numero decimale (può essere positivo o negativo)  
**Descrizione**: Deviazione percentuale del peso attuale dal target  
**Formula**: `Δwᵢ = ŵᵢ − wᵢ`  
**Interpretazione**:
- Δwᵢ > 0 → strumento sovrapesato (da vendere)
- Δwᵢ < 0 → strumento sottopesato (da comprare)
- Δwᵢ = 0 → strumento già a target

**Esempio**: Δw₁ = 0.4568 − 0.60 = −0.1432 (sottopesato del 14.32%)

---

## Variabili di Decisione

Queste sono le variabili che rappresentano le azioni da intraprendere.

### ΔVᵢ
**Tipo**: Numero decimale (può essere positivo o negativo)  
**Descrizione**: Variazione di valore necessaria per lo strumento i (in euro)  
**Formula**: `ΔVᵢ = (wᵢ × V_tot) − Vᵢ`  
**Unità**: €  
**Interpretazione**:
- ΔVᵢ > 0 → aumentare la posizione (comprare)
- ΔVᵢ < 0 → ridurre la posizione (vendere)
- ΔVᵢ = 0 → non fare nulla

**Esempio**: ΔV₁ = (0.60 × 11,000) − 5,025 = 1,575 € (devo aumentare di 1,575€)

### ΔQᵢ
**Tipo**: Numero decimale (può essere positivo o negativo)  
**Descrizione**: Variazione di quote necessaria per lo strumento i  
**Formula**: `ΔQᵢ = ΔVᵢ / Pᵢ`  
**Unità**: quote  
**Interpretazione**:
- ΔQᵢ > 0 → comprare ΔQᵢ quote
- ΔQᵢ < 0 → vendere |ΔQᵢ| quote
- ΔQᵢ = 0 → non fare nulla

**Esempio**: ΔQ₁ = 1,575 / 100.50 = 15.67 quote da acquistare

---

## Variabili di Cash Flow

### cash_inᵢ
**Tipo**: Numero decimale non negativo  
**Descrizione**: Liquidità generata dalla vendita dello strumento i (al netto delle tasse)  
**Formula**: 
```
cash_inᵢ = |ΔQᵢ| × Pᵢ × (1 − Tᵢ × max(0, Pᵢ − PMCᵢ))   se ΔQᵢ < 0
cash_inᵢ = 0                                              altrimenti
```
**Unità**: €  
**Nota**: La formula tiene conto della tassazione solo sul capital gain

**Esempio**:  
Se vendo 10 quote a 110€ (PMC = 108€, T = 0.26):  
```
cash_in = 10 × 110 × (1 − 0.26 × (110 − 108))
        = 10 × 110 × (1 − 0.26 × 2)
        = 10 × 110 × 0.948
        = 1,042.80 €
```

### cash_outᵢ
**Tipo**: Numero decimale non negativo  
**Descrizione**: Liquidità necessaria per l'acquisto dello strumento i  
**Formula**: 
```
cash_outᵢ = ΔQᵢ × Pᵢ   se ΔQᵢ > 0
cash_outᵢ = 0          altrimenti
```
**Unità**: €  

**Esempio**:  
Se compro 15.67 quote a 100.50€:  
```
cash_out = 15.67 × 100.50 = 1,574.84 €
```

### CF
**Tipo**: Numero decimale (può essere positivo o negativo)  
**Descrizione**: Cash flow totale del ribilanciamento  
**Formula**: `CF = Σᵢ cash_inᵢ − Σᵢ cash_outᵢ`  
**Unità**: €  
**Interpretazione**:
- CF > 0 → le vendite generano più liquidità del necessario per gli acquisti (surplus)
- CF < 0 → servono più soldi per gli acquisti di quanti ne generano le vendite (deficit)
- CF = 0 → perfetto bilanciamento (obiettivo ideale)

**Vincolo operativo**: Il sistema cerca di minimizzare |CF| per non richiedere apporti/prelievi esterni.

---

## Variabili Post-Ribilanciamento

Queste variabili descrivono lo stato del portafoglio dopo il ribilanciamento.

### Qᵢ,new
**Tipo**: Numero decimale  
**Descrizione**: Nuova quantità di quote dello strumento i dopo il ribilanciamento  
**Formula**: `Qᵢ,new = Qᵢ + ΔQᵢ`  
**Unità**: quote  

### Vᵢ,new
**Tipo**: Numero decimale  
**Descrizione**: Nuovo valore dello strumento i dopo il ribilanciamento  
**Formula**: `Vᵢ,new = Qᵢ,new × Pᵢ`  
**Unità**: €  

### ŵᵢ,new
**Tipo**: Numero decimale  
**Descrizione**: Nuovo peso percentuale dello strumento i dopo il ribilanciamento  
**Formula**: `ŵᵢ,new = Vᵢ,new / Σᵢ Vᵢ,new`  
**Vincoli**: 0 ≤ ŵᵢ,new ≤ 1, Σᵢ ŵᵢ,new = 1  

**Obiettivo**: Idealmente ŵᵢ,new ≈ wᵢ (quanto più vicino al target, meglio è)

---

## Glossario dei Simboli

| Simbolo | Nome | Significato |
|---------|------|-------------|
| i | Indice | Identifica uno specifico strumento |
| N | Numero strumenti | Totale degli asset nel portafoglio |
| Q | Quantity | Quantità di quote |
| P | Price | Prezzo corrente |
| PMC | Prezzo Medio di Carico | Average cost basis |
| T | Tax rate | Aliquota fiscale |
| w | Weight | Peso percentuale |
| ŵ | Weight attuale | Peso percentuale corrente (con cappello) |
| Δ | Delta | Variazione, differenza |
| V | Value | Valore in euro |
| CF | Cash Flow | Flusso di cassa |
| Σ | Sigma | Somma su tutti gli strumenti |
| | | max(a,b) | Massimo tra a e b |

---

## Note Implementative

### Precisione numerica

Tutti i calcoli devono essere eseguiti con precisione decimale (non float) per evitare errori di arrotondamento nei calcoli finanziari.

**Python**: Usare `Decimal` del modulo `decimal`

### Validazione input

Prima di eseguire i calcoli, verificare:
1. Σᵢ wᵢ = 1 (con tolleranza di 1e-6)
2. Tutti i valori positivi rispettano i vincoli
3. Non ci sono valori NaN o infiniti

### Arrotondamento

L'arrotondamento delle quantità a quote intere avviene **dopo** il calcolo delle ΔQᵢ continue, usando policy configurabili definite in `policies/`.
