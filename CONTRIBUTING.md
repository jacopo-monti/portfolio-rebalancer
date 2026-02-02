# Contribuire al Progetto

Grazie per l'interesse nel contribuire a Portfolio Rebalancer!

## Filosofia del Progetto

Prima di contribuire, è importante comprendere e rispettare la filosofia del progetto:

1. **Determinismo**: Il codice deve produrre sempre lo stesso output per lo stesso input
2. **Trasparenza**: Ogni decisione deve essere spiegabile e tracciabile
3. **Semplicità**: Preferiamo codice semplice e chiaro a soluzioni "ottimali" ma complesse
4. **Nessuna ottimizzazione numerica complessa**: No solver, no ML, no black box

## Come Contribuire

### Segnalazione di Bug

1. Verifica che il bug non sia già stato segnalato nelle [Issues](https://github.com/jacopo-monti/portfolio-rebalancer/issues)
2. Apri una nuova issue con:
   - Descrizione chiara del problema
   - Passi per riprodurlo
   - Comportamento atteso vs comportamento effettivo
   - Versione Python e sistema operativo

### Proposta di Nuove Funzionalità

1. Apri una issue per discutere la funzionalità prima di implementarla
2. Assicurati che sia in linea con la filosofia del progetto
3. Descrivi:
   - Caso d'uso
   - Come si integra con il codice esistente
   - Possibili implicazioni

### Pull Request

1. **Fork** il repository
2. Crea un **branch** per la tua modifica:
   ```bash
   git checkout -b feature/nome-feature
   ```
3. Implementa le modifiche seguendo lo stile del codice esistente
4. **Aggiungi test** per le nuove funzionalità
5. **Documenta** il codice con docstring
6. Verifica che i test passino:
   ```bash
   pytest
   ```
7. Verifica lo stile del codice:
   ```bash
   black src/ tests/
   flake8 src/ tests/
   mypy src/
   ```
8. Commit con messaggi descrittivi:
   ```bash
   git commit -m "Aggiunta feature X che fa Y"
   ```
9. Push del branch:
   ```bash
   git push origin feature/nome-feature
   ```
10. Apri una **Pull Request** su GitHub

## Linee Guida per il Codice

### Stile

- Usa **Black** per il formatting (line length: 100)
- Segui **PEP 8**
- Usa **type hints** per tutti i parametri e return values
- Docstring in stile **Google**

### Testing

- Ogni nuova funzione deve avere test unitari
- Usa **pytest** per i test
- Obiettivo: 100% coverage del core engine
- Test devono essere deterministici

### Documentazione

- Ogni funzione pubblica deve avere docstring
- Documenta **perché** hai fatto una scelta, non solo **cosa** fa il codice
- Aggiorna `README.md` se necessario
- Aggiorna `docs/` per modifiche algoritmiche

## Cosa NON Contribuire

Per mantenere il progetto focalizzato, **non** accettiamo contributi che:

- Aggiungono dipendenze da solver numerici pesanti (SciPy, CVXPY, ecc.)
- Introducono comportamenti non deterministici
- Aggiungono ottimizzazione/ML senza forte motivazione
- Violano la filosofia di trasparenza e semplicità
- Aggiungono funzionalità fuori scope (asset selection, previsioni, ecc.)

## Domande?

Se hai domande, apri una [Discussion](https://github.com/jacopo-monti/portfolio-rebalancer/discussions) su GitHub.

Grazie per il tuo contributo! 🚀
