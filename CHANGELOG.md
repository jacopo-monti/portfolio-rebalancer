# Changelog

Tutte le modifiche significative al progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/it/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/lang/it/).

## [Unreleased]

### In sviluppo
- Modulo I/O per Excel
- Web interface (pianificata per v0.2.0)
- Supporto multi-valuta (pianificato per v0.3.0)

## [0.1.0] - 2026-02-02

### Aggiunto
- Core engine di ribilanciamento deterministico (8 step)
- Modelli dati: `Asset`, `Portfolio`, `RebalancingResult`
- Policy di arrotondamento: `RoundingPolicy` (FLOOR, ROUND, CEIL)
- Calcolo tassazione capital gain
- Chiusura automatica del cash flow con scalatura proporzionale
- Test unitari per core engine e models
- Esempio base di utilizzo
- Documentazione completa:
  - `README.md` - Panoramica e guida rapida
  - `docs/ALGORITHM.md` - Algoritmo dettagliato
  - `docs/VARIABLES.md` - Definizioni formali
  - `docs/DESIGN.md` - Scelte progettuali
- Configurazione CI/CD con GitHub Actions
- Licenza MIT

### Caratteristiche
- ✅ Determinismo: stesso input → stesso output
- ✅ Trasparenza: ogni calcolo ispezionabile
- ✅ Tax-aware: gestione capital gain tax
- ✅ Cash-flow neutral: minimizza apporti/prelievi esterni
- ✅ Nessuna ottimizzazione numerica complessa
- ✅ Type hints completi
- ✅ Documentazione esaustiva

### Note
- Questa è la prima release alpha del progetto
- Il core engine è stabile e testato
- L'API potrebbe subire modifiche nelle versioni successive

[Unreleased]: https://github.com/jacopo-monti/portfolio-rebalancer/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jacopo-monti/portfolio-rebalancer/releases/tag/v0.1.0
