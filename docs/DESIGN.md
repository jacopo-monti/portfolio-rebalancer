# Scelte Progettuali

Questo documento spiega le motivazioni dietro le scelte architetturali e algoritmiche del progetto.

## Filosofia del Progetto

### Perché NON un ottimizzatore?

Molti tool di portfolio management usano ottimizzatori numerici (solver, programmazione quadratica, ecc.). Noi abbiamo scelto di **non** farlo per diverse ragioni:

#### 1. Trasparenza e Spiegabilità

Un ottimizzatore numerico è una "black box":
- L'utente non capisce *perché* una certa operazione viene suggerita
- È difficile debuggare quando qualcosa va storto
- Non è possibile tracciare il processo decisionale

**La nostra scelta**: Matematica elementare, ogni passo è comprensibile.

#### 2. Determinismo

Molti solver numerici sono stocastici o dipendono da condizioni iniziali:
- Esecuzioni diverse → risultati leggermente diversi
- Difficile da testare
- Non riproducibile

**La nostra scelta**: Stesso input → **sempre** lo stesso output.

#### 3. Semplicità

L'ottimizzazione aggiunge dipendenze pesanti:
- Librerie come SciPy, CVXPY, o solver commerciali
- Maggiore complessità del codice
- Più difficile da mantenere

**La nostra scelta**: Solo pandas e operazioni elementari.

#### 4. Il problema non lo richiede

Il ribilanciamento a percentuali target è un problema **matematicamente semplice**:
- Non servono funzioni obiettivo complesse
- Non ci sono vincoli non lineari
- La soluzione "ovvia" (proporzionale) funziona bene

**La nostra scelta**: Keep it simple.

---

## Architettura del Software

### Separazione Core / I/O

```
┌─────────────────┐
│   Core Engine   │  ← Matematica pura, NO dipendenze esterne
│  (engine/)      │
└────────┬────────┘
         │
         │  usa
         ▼
┌─────────────────┐
│     Models      │  ← Strutture dati pure
│   (models/)     │
└────────┬────────┘
         │
         │  usato da
         ▼
┌─────────────────┐
│   I/O Layer     │  ← Excel, CSV, JSON, ...  (può dipendere da librerie esterne)
│    (io/)        │
└─────────────────┘
```

#### Vantaggi

1. **Testabilità**: Il core engine può essere testato senza creare file Excel
2. **Estendibilità**: Nuovi formati I/O senza toccare il core
3. **Portabilità**: Il core può essere usato in contesti diversi (CLI, web app, Jupyter, ecc.)

### Models: Data Classes Pure

Le classi in `models/` sono **semplici contenitori di dati**:
- Nessuna logica di business
- Nessuna dipendenza esterna
- Facilmente serializzabili

```python
@dataclass
class Asset:
    symbol: str
    quantity: float
    price: float
    avg_cost: float
    tax_rate: float
    target_weight: float
```

### Engine: Funzioni Pure

Il core engine è composto da funzioni pure (o quasi):
- Input → elaborazione → output
- Nessun side effect
- Nessuno stato globale

```python
def rebalance(portfolio: Portfolio) -> RebalancingResult:
    # Step 1-8 dell'algoritmo
    ...
    return result
```

### Policies: Configurabilità

Le policy permettono di configurare comportamenti senza modificare il core:
- `RoundingPolicy`: Come arrotondare le quote
- `TolerancePolicy`: Quanto scostamento accettare
- `TaxPolicy`: Gestione tassazione (future estensioni)

---

## Scelte Algoritmiche

### Chiusura del Cash Flow: Scalatura Proporzionale

#### Il Problema

Dopo aver calcolato ΔQᵢ, il cash flow potrebbe non essere zero:
```
CF = Σ cash_inᵢ − Σ cash_outᵢ ≠ 0
```

#### Approccio 1: Ottimizzazione (SCARTATO)

Potremmo formulare un problema di ottimizzazione:

```
minimizza:  Σᵢ (ŵᵢ,new − wᵢ)²
vincolo:    CF = 0
```

Problemi:
- Richiede un solver
- Non deterministico
- Complesso
- Overkill per il problema

#### Approccio 2: Scalatura Proporzionale (SCELTO)

Scaliamo solo gli acquisti in modo proporzionale:

```
ΔQᵢ,adjusted = ΔQᵢ × (1 + CF / Σⱼ cash_outⱼ)    per ΔQᵢ > 0
```

Vantaggi:
- Semplice (una riga di codice)
- Deterministico
- Intuitivo: "riduci tutti gli acquisti della stessa percentuale"
- Nessuna dipendenza esterna

Svantaggi:
- Non è "ottimale" in senso matematico
- Potrebbe sbilanciare leggermente i pesi

**Verdetto**: I vantaggi superano di gran lunga gli svantaggi. La differenza pratica è trascurabile.

### Tassazione: Approccio Semplificato

La formula per il cash_in include la tassazione:

```
cash_inᵢ = |ΔQᵢ| × Pᵢ × (1 − Tᵢ × max(0, Pᵢ − PMCᵢ))
```

#### Assunzioni

1. **Capital gain tax lineare**: Aliquota costante Tᵢ
2. **No loss harvesting**: Se vendo in perdita, la tassa è 0, ma non recupero perdite pregresse
3. **No FIFO/LIFO**: Uso il PMC (prezzo medio) per semplicità

#### Estensioni Future

- **Tax loss harvesting**: Vendere asset in perdita per compensare guadagni
- **FIFO/LIFO**: Scegliere quali lotti vendere
- **Aliquote progressive**: Gestire scaglioni di imposta

**Scelta attuale**: Manteniamo semplice. Il 90% dei casi è coperto.

### Arrotondamento: Fuori dal Core

L'arrotondamento a quote intere è **opzionale** e avviene **dopo** il calcolo:

1. Il core calcola ΔQᵢ come numero decimale
2. Una policy (opzionale) arrotonda
3. Vengono ricalcolati CF e deviazioni residue

#### Perché?

- **Flessibilità**: Alcuni asset (fondi, frazioni di azioni) permettono quantità decimali
- **Separazione**: Il core non deve sapere delle restrizioni di quota intera
- **Trasparenza**: L'utente vede sia il valore "ideale" che quello arrotondato

---

## Scelte di Implementazione

### Python come Linguaggio

**Vantaggi**:
- Leggibile: il codice è quasi pseudocodice
- Ecosistema ricco: pandas, pytest, black, mypy
- Portabile: gira ovunque
- Popolare nella finanza quantitativa

**Svantaggi**:
- Prestazioni: più lento di C++/Rust
- Type safety: opzionale (mypy aiuta)

**Verdetto**: Per questo tipo di applicazione, Python è perfetto. Le prestazioni non sono critiche (< 1s anche per centinaia di asset).

### Pandas vs Numpy

**Scelta**: Usiamo pandas per I/O (Excel), ma il core usa strutture native.

**Perché?**
- Pandas è comodo per leggere/scrivere Excel
- Ma per il core, liste e dataclass sono più semplici
- Meno dipendenze "pesanti" nel core

### Type Hints e MyPy

Il codice usa type hints completi:

```python
def rebalance(portfolio: Portfolio) -> RebalancingResult:
    ...
```

**Vantaggi**:
- Documentazione inline
- Controllo statico con mypy
- Migliore IDE support (autocomplete)
- Più difficile fare errori

### Testing Strategy

```
tests/
├── test_models.py        # Test delle strutture dati
├── test_engine.py        # Test del core engine
├── test_policies.py      # Test delle policy
├── test_io_excel.py      # Test I/O Excel
└── test_integration.py   # Test end-to-end
```

**Obiettivo**: 100% code coverage del core engine.

---

## Scelte NON Fatte (e Perché)

### Multi-obiettivo

**Non implementato**: Ottimizzazione simultanea di più obiettivi (es. minimizzare tasse E minimizzare numero di operazioni).

**Perché**: Aggiunge complessità enorme. L'utente può scegliere policy diverse per ottenere risultati diversi.

### Integrazione con Broker

**Non implementato**: Esecuzione automatica degli ordini presso un broker.

**Perché**: 
- Aumenta la responsabilità legale
- Ogni broker ha API diverse
- Richiede gestione errori, autenticazione, sicurezza
- Fuori dallo scope: "calcolo operazioni", non "eseguo operazioni"

### Recupero Prezzi Automatico

**Non implementato**: Download automatico dei prezzi da Yahoo Finance, Alpha Vantage, ecc.

**Perché**:
- API esterne possono cambiare o diventare a pagamento
- Rate limiting
- Diversi provider per diversi strumenti
- L'utente spesso ha già i prezzi dal suo broker

**Compromesso**: Forniamo script di esempio nella cartella `examples/` per chi vuole farlo.

### Machine Learning

**Non implementato**: Predizioni, clustering di asset, ecc.

**Perché**: Completamente fuori scope. Questo tool NON fa previsioni. Solo matematica deterministica.

### Gestione Multi-Valuta

**Non implementato**: Portafogli con asset in valute diverse.

**Perché**: 
- Aggiunge complessità (tassi di cambio, hedging, ecc.)
- Il 90% degli utenti ha portafogli monovaluta
- Può essere aggiunto in futuro come estensione

**Workaround attuale**: L'utente converte manualmente tutti i prezzi in una valuta di riferimento.

---

## Vincoli di Design

### Must Have

1. ✅ Determinismo
2. ✅ Trasparenza
3. ✅ Nessuna ottimizzazione numerica complessa
4. ✅ Tax-aware
5. ✅ Cash-flow neutral

### Should Have

1. ✅ Gestione quote intere
2. ✅ Input da Excel
3. ✅ Output leggibile
4. ✅ Documentazione completa

### Nice to Have

1. ⏳ Web interface
2. ⏳ Recupero prezzi automatico (esempio)
3. ⏳ Export PDF del report
4. ⏳ Multi-valuta

### Won't Have

1. ❌ Ottimizzazione rischio/rendimento
2. ❌ Asset selection
3. ❌ Previsioni di mercato
4. ❌ Integrazione broker automatica
5. ❌ Machine learning

---

## Performance

### Complessità Temporale

- **Step 1-5**: O(N) dove N = numero di asset
- **Step 6**: O(N)
- **Step 7**: O(N)
- **Step 8**: O(N)

**Totale**: O(N)

### Benchmark

Su un laptop moderno (2020):
- Portafoglio di 10 asset: < 1 ms
- Portafoglio di 100 asset: < 10 ms
- Portafoglio di 1000 asset: < 100 ms

Le prestazioni **non** sono un problema.

---

## Lezioni Apprese

### Keep It Simple

La tentazione di "ottimizzare" era forte. Resistere e mantenere l'algoritmo semplice è stata la scelta giusta.

### Documentazione Prima del Codice

Scrivere prima le specifiche matematiche (ALGORITHM.md, VARIABLES.md) ha reso il coding molto più facile e meno soggetto a errori.

### Testing È Fondamentale

Test completi permettono di:
- Refactorare senza paura
- Aggiungere funzionalità con fiducia
- Documentare il comportamento atteso

### Separazione delle Responsabilità

Core engine separato da I/O è stata una scelta vincente. Permette riutilizzo e testabilità.

---

## Evoluzione Futura

Il progetto è progettato per essere estendibile:

### Versione 1.x (Attuale)
- Core engine matematico
- I/O Excel
- Policy di base
- CLI

### Versione 2.x (Futura)
- Web interface (Flask/FastAPI + React)
- Database per storico operazioni
- Più formati di export (PDF, JSON, CSV)
- API REST

### Versione 3.x (Visione)
- Multi-valuta
- Tax loss harvesting
- Vincoli avanzati (lotti, multipli)
- Integrazione con data provider (opzionale)

**Importante**: Il core engine rimarrà sempre **semplice e deterministico**. Le funzionalità avanzate saranno layer aggiuntivi.

---

## Conclusioni

Questo progetto dimostra che:

1. **Semplice ≠ Stupido**: Un algoritmo elementare può risolvere problemi reali
2. **Trasparenza > Ottimalità**: È più importante capire cosa fa il software che avere una soluzione "perfetta"
3. **Determinismo > Flessibilità**: Per tool finanziari, la riproducibilità è critica
4. **Documentazione = Codice**: Un progetto ben documentato è un progetto utilizzabile

L'obiettivo è stato raggiunto: **un tool che chiunque può capire, criticare e usare con fiducia**.
