# Portfolio Rebalancer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Un tool deterministico per il ribilanciamento di portafogli finanziari con gestione della tassazione.

## ⚠️ Disclaimer

**Questo software NON fornisce consulenza finanziaria.**

Questo tool è uno strumento di calcolo matematico che:
- ✅ Calcola le operazioni necessarie per riportare un portafoglio a percentuali target predefinite
- ✅ Tiene conto di vincoli pratici (tassazione, cash flow, quote intere)
- ❌ NON ottimizza rendimento o rischio
- ❌ NON fa previsioni di mercato
- ❌ NON suggerisce asset da acquistare
- ❌ NON fornisce consigli di investimento

L'utilizzo di questo software è a esclusivo rischio dell'utente.

## 🎯 Obiettivi del Progetto

Questo progetto nasce con una filosofia chiara:

1. **Trasparenza**: Ogni calcolo è ispezionabile e riproducibile
2. **Determinismo**: Stesso input → stesso output (sempre)
3. **Separazione delle responsabilità**: Core engine matematico indipendente da I/O
4. **Semplicità**: Nessuna black box di ottimizzazione, solo matematica elementare
5. **Spiegabilità**: Ogni decisione deve essere ricostruibile

### Pubblico di riferimento

- Utenti avanzati / smanettoni interessati al personal finance
- Community di investitori che vogliono automatizzare il ribilanciamento
- Docenti e studenti di finanza computazionale
- Chiunque voglia capire esattamente cosa succede nel proprio portafoglio

## 🔧 Cosa fa (e cosa NON fa)

### ✅ Il tool DEVE fare

- Calcolare lo stato attuale del portafoglio
- Confrontarlo con percentuali target per ogni strumento
- Determinare quantità da comprare/vendere per ogni asset
- Tenere conto della tassazione sulle vendite (capital gain tax)
- Rispettare il vincolo di cash flow ≈ 0
- Gestire tolleranze configurabili
- Simulare il portafoglio post-ribilanciamento
- Supportare arrotondamenti a quote intere

### ❌ Il tool NON DEVE fare

- Previsioni di mercato
- Ottimizzazione rischio/rendimento
- Suggerire nuovi strumenti da acquistare
- Integrazione diretta con broker
- Recupero automatico dei prezzi
- Gestione multi-valuta avanzata
- Machine learning o AI

## 📐 Algoritmo

L'algoritmo implementa un processo deterministico in 8 step:

### Step 1: Stato attuale del portafoglio

Per ogni strumento *i*:
```
Vᵢ = Qᵢ × Pᵢ
```
Dove:
- `Vᵢ` = valore attuale dello strumento *i*
- `Qᵢ` = quantità di quote possedute
- `Pᵢ` = prezzo corrente

```
V_tot = Σ Vᵢ
ŵᵢ = Vᵢ / V_tot
```
Dove:
- `V_tot` = valore totale del portafoglio
- `ŵᵢ` = peso percentuale attuale di *i*

### Step 2: Deviazione dal target

```
Δwᵢ = ŵᵢ − wᵢ
```
Dove:
- `wᵢ` = peso target desiderato per lo strumento *i*
- `Δwᵢ > 0` → strumento sovrapesato (da vendere)
- `Δwᵢ < 0` → strumento sottopesato (da comprare)

### Step 3: Valore target in euro

```
ΔVᵢ = (wᵢ × V_tot) − Vᵢ
```
`ΔVᵢ` rappresenta la variazione di valore necessaria in euro.

### Step 4: Conversione in quote

```
ΔQᵢ = ΔVᵢ / Pᵢ
```
- `ΔQᵢ > 0` → acquisto
- `ΔQᵢ < 0` → vendita

### Step 5: Cash flow con tassazione

Per vendite (`ΔQᵢ < 0`):
```
cash_inᵢ = |ΔQᵢ| × Pᵢ × (1 − Tᵢ × max(0, Pᵢ − PMCᵢ))
```
Dove:
- `PMCᵢ` = prezzo medio di carico
- `Tᵢ` = aliquota fiscale (es. 0.26 per il 26%)
- La tassazione si applica solo sul capital gain: `(Pᵢ − PMCᵢ)`

Per acquisti (`ΔQᵢ > 0`):
```
cash_outᵢ = ΔQᵢ × Pᵢ
```

Cash flow totale:
```
CF = Σ cash_inᵢ − Σ cash_outᵢ
```

### Step 6: Chiusura del cash flow

Se `CF ≠ 0`, viene applicata una scalatura proporzionale alle quantità da acquistare:
```
ΔQᵢ,adjusted = ΔQᵢ × (1 − CF / Σ cash_outᵢ)    per ΔQᵢ > 0
```

**Nota importante**: Non usiamo solver numerici o ottimizzatori. La scalatura è una semplice proporzione.

### Step 7: Simulazione post-ribilanciamento

```
Qᵢ,new = Qᵢ + ΔQᵢ
Vᵢ,new = Qᵢ,new × Pᵢ
ŵᵢ,new = Vᵢ,new / Σ Vᵢ,new
```

### Step 8: Arrotondamento

L'arrotondamento a quote intere viene applicato **fuori dal core engine**, secondo policy configurabili:
- Troncamento
- Arrotondamento matematico
- Arrotondamento per eccesso

Dopo l'arrotondamento, si ricalcolano CF e deviazioni residue.

## 🏗️ Architettura

```
portfolio-rebalancer/
│
├── src/
│   ├── portfolio_rebalancer/
│   │   ├── __init__.py
│   │   ├── models/          # Modelli dati (Portfolio, Asset, RebalancingResult)
│   │   ├── engine/          # Core engine matematico (NO I/O)
│   │   ├── policies/        # Policy di arrotondamento e tolleranze
│   │   └── io/              # Input/Output (Excel, CSV, JSON)
│   │
├── examples/
│   ├── example_basic.py
│   ├── example_excel.py
│   └── portfolio_template.xlsx
│
├── tests/
│   ├── test_engine.py
│   ├── test_models.py
│   └── test_policies.py
│
├── docs/
│   ├── ALGORITHM.md         # Documentazione algoritmo dettagliata
│   ├── VARIABLES.md         # Definizioni formali
│   └── DESIGN.md            # Scelte progettuali
│
├── README.md
├── LICENSE
├── pyproject.toml
└── .gitignore
```

### Principi architetturali

1. **Separazione core/IO**: Il core engine (`engine/`) non dipende da Excel o altri formati
2. **Determinismo**: Nessun RNG, nessuna ottimizzazione stocastica
3. **Testabilità**: Ogni componente è testabile in isolamento
4. **Estendibilità**: Nuove policy e formati I/O senza modificare il core

## 🚀 Installazione

### Da PyPI (quando sarà pubblicato)

```bash
pip install portfolio-rebalancer
```

### Da sorgente

```bash
git clone https://github.com/jacopo-monti/portfolio-rebalancer.git
cd portfolio-rebalancer
pip install -e .
```

### Per sviluppatori

```bash
pip install -e ".[dev]"
```

## 💡 Esempio pratico

### Scenario

Hai un portafoglio di 3 ETF:

| ETF | Quantità | Prezzo | Valore | Peso attuale | Target |
|-----|----------|--------|--------|--------------|--------|
| VWCE | 50 | €100 | €5,000 | 45.45% | 60% |
| AGGH | 30 | €110 | €3,300 | 30.00% | 25% |
| EIMI | 20 | €135 | €2,700 | 24.55% | 15% |
| **Totale** | | | **€11,000** | **100%** | **100%** |

**Problema**: Il portafoglio è sbilanciato rispetto ai target.

### Soluzione

```python
from portfolio_rebalancer.models import Portfolio, Asset
from portfolio_rebalancer.engine import RebalancingEngine

# Definisci il portafoglio
portfolio = Portfolio(
    assets=[
        Asset(symbol="VWCE", quantity=50, price=100.0, avg_cost=95.0, tax_rate=0.26, target_weight=0.60),
        Asset(symbol="AGGH", quantity=30, price=110.0, avg_cost=108.0, tax_rate=0.26, target_weight=0.25),
        Asset(symbol="EIMI", quantity=20, price=135.0, avg_cost=130.0, tax_rate=0.26, target_weight=0.15),
    ]
)

# Esegui il ribilanciamento
engine = RebalancingEngine()
result = engine.rebalance(portfolio)

# Visualizza risultati
print(result.summary())
```

**Output**:
```
Ribilanciamento Portafoglio
============================

Stato attuale:
  VWCE: 50 quote × €100.00 = €5,000.00 (45.45%)
  AGGH: 30 quote × €110.00 = €3,300.00 (30.00%)
  EIMI: 20 quote × €135.00 = €2,700.00 (24.55%)
  TOTALE: €11,000.00

Operazioni necessarie:
  VWCE: +16.00 quote (acquisto €1,600.00)
  AGGH: -5.00 quote (vendita €537.40 dopo tasse)
  EIMI: -7.00 quote (vendita €932.86 dopo tasse)

Cash flow: €-129.74 (quasi bilanciato)

Stato post-ribilanciamento:
  VWCE: 66 quote × €100.00 = €6,600.00 (60.00%)
  AGGH: 25 quote × €110.00 = €2,750.00 (25.00%)
  EIMI: 13 quote × €135.00 = €1,755.00 (15.95%)
```

### Con Excel

1. Crea un file Excel con il template fornito (`examples/portfolio_template.xlsx`)
2. Compila i dati del tuo portafoglio
3. Esegui:

```python
from portfolio_rebalancer.io import ExcelIO

io = ExcelIO()
portfolio = io.read_portfolio("mio_portafoglio.xlsx")
result = engine.rebalance(portfolio)
io.write_result(result, "risultato_ribilanciamento.xlsx")
```

## 📚 Documentazione

- [ALGORITHM.md](docs/ALGORITHM.md) - Algoritmo dettagliato con tutte le formule
- [VARIABLES.md](docs/VARIABLES.md) - Definizioni formali di tutte le variabili
- [DESIGN.md](docs/DESIGN.md) - Scelte progettuali e motivazioni

## 🧪 Testing

```bash
# Esegui tutti i test
pytest

# Con coverage
pytest --cov=portfolio_rebalancer --cov-report=html

# Test specifico
pytest tests/test_engine.py::test_cash_flow_closure
```

## 🤝 Contribuire

Contribuzioni benvenute! Questo progetto è open source proprio per permettere:

- Review del codice e dell'algoritmo
- Segnalazione di bug
- Miglioramenti alla documentazione
- Nuove funzionalità (purché rispettino la filosofia del progetto)

Per contribuire:

1. Fai un fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/nome-feature`)
3. Commit delle modifiche (`git commit -am 'Aggiunta nuova feature'`)
4. Push del branch (`git push origin feature/nome-feature`)
5. Apri una Pull Request

### Linee guida

- Il core engine deve rimanere **deterministico**
- Nessuna ottimizzazione numerica complessa (no solver, no ML)
- Codice ben documentato e testato
- Rispetta la filosofia di trasparenza e spiegabilità

## 📄 Licenza

MIT License - vedi [LICENSE](LICENSE) per dettagli.

## 🙏 Riconoscimenti

Questo progetto è ispirato dalla necessità di avere un tool di ribilanciamento:
- Completamente trasparente
- Matematicamente semplice
- Verificabile da chiunque
- Senza "magie" algoritmiche

## 📧 Contatti

Per domande, suggerimenti o segnalazioni: [apri una issue](https://github.com/jacopo-monti/portfolio-rebalancer/issues)

---

**Ricorda**: Questo software è un tool di calcolo, non un consulente finanziario. Le decisioni di investimento sono sempre e solo tue.
