"""Multi-language translation support for the Portfolio Rebalancer web application.

This module provides a centralized translation system that allows the UI to display
text in multiple languages. The architecture is designed to be extensible, making it
easy to add new languages in the future.

Supported Languages:
    - English (en) - Default
    - Italian (it)

Usage:
    from webapp.translations import get_text
    
    # Get translated text using the current language from session state
    title = get_text('app_title')
"""

from typing import Dict, Any
import streamlit as st


# ============================================================================
# TRANSLATION DICTIONARIES
# ============================================================================

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        # App title and header
        "app_title": "Portfolio Rebalancing Tool",
        "app_subtitle": "A deterministic, tax-aware portfolio rebalancing calculator",
        "language_selector_label": "Language",
        
        # Sidebar
        "sidebar_title": "Portfolio Rebalancer",
        "sidebar_about_title": "About",
        "sidebar_about_text": """This is a **deterministic** portfolio rebalancing tool that:
- Calculates optimal buy/sell operations
- Considers capital gains tax
- Handles broker commissions
- Maintains cash flow neutrality""",
        "sidebar_how_to_title": "How to Use",
        "sidebar_how_to_text": """1. **Target & Portfolio**: Add assets and define targets
2. **Analysis**: Run rebalancing and view results
3. **Settings**: Configure algorithm parameters""",
        "sidebar_note_title": "Note",
        "sidebar_note_text": """This tool is for **calculation purposes only**, not financial advice.
All data is stored in-memory and lost when you close the browser.""",
        
        # Tab names
        "tab_portfolio": "🎯 Target & Portfolio",
        "tab_analysis": "📈 Analysis",
        "tab_settings": "⚙️ Settings",
        
        # Tab 1: Portfolio Configuration
        "portfolio_config_title": "Portfolio Configuration",
        "portfolio_config_description": "Build your portfolio by adding assets one at a time. Define each asset's current holdings and target allocation.",
        "portfolio_name_label": "Portfolio Name",
        "portfolio_name_help": "Give your portfolio a name for identification",
        "cash_available_label": "Available Cash to Deploy (€)",
        "cash_available_help": "Additional cash you want to invest. Set to 0 for cash-neutral rebalancing.",
        
        # Asset form
        "add_asset_title": "Add Asset",
        "edit_asset_title": "Edit Asset",
        "basic_info_section": "Basic Information",
        "asset_symbol_label": "Asset Symbol/Name *",
        "asset_symbol_help": "e.g., VWCE, AAPL, BTC",
        "quantity_label": "Quantity (shares) *",
        "quantity_help": "Number of shares you currently own",
        "current_price_label": "Current Price (€) *",
        "current_price_help": "Current market price per share",
        "avg_cost_label": "Average Cost (€) *",
        "avg_cost_help": "Your average purchase price (for tax calculation)",
        "tax_rate_label": "Tax Rate (%) *",
        "tax_rate_help": "Capital gains tax rate",
        "target_weight_label": "Target Weight (%) *",
        "target_weight_help": "Desired portfolio allocation",
        
        # Commission settings
        "commission_section": "📋 Commission Settings (Optional)",
        "buy_commissions_title": "Buy Commissions",
        "sell_commissions_title": "Sell Commissions",
        "fixed_fee_label": "Fixed Fee (€)",
        "pct_fee_label": "% Fee",
        "min_fee_label": "Min Fee (€)",
        "max_fee_label": "Max Fee (€)",
        
        # Form buttons
        "update_asset_button": "✅ Update Asset",
        "add_asset_button": "➕ Add Asset to Portfolio",
        "cancel_button": "❌ Cancel",
        
        # Validation messages
        "error_empty_symbol": "Asset name/symbol cannot be empty",
        "error_negative_quantity": "Quantity must be ≥ 0",
        "error_invalid_price": "Price must be > 0",
        "error_negative_avg_cost": "Average cost must be ≥ 0",
        "error_invalid_tax_rate": "Tax rate must be between 0% and 100%",
        "error_invalid_target_weight": "Target weight must be between 0% and 100%",
        "error_negative_commission": "{} must be ≥ 0",
        "error_invalid_pct_commission": "{} must be ≤ 100%",
        "error_duplicate_symbol": "Asset '{}' already exists in portfolio",
        "success_asset_updated": "Asset '{}' updated successfully!",
        "success_asset_added": "Asset '{}' added to portfolio!",
        
        # Portfolio display
        "current_portfolio_title": "Current Portfolio Assets",
        "no_assets_message": "📝 No assets in portfolio. Add your first asset using the form above.",
        "value_label": "Value",
        "target_label": "Target",
        "quantity_short_label": "Quantity",
        "details_expander": "📊 Details",
        "holdings_section": "Holdings",
        "tax_target_section": "Tax & Target",
        "commissions_section": "Commissions",
        "buy_label": "Buy",
        "sell_label": "Sell",
        "none_label": "None",
        "edit_button": "✏️ Edit",
        "delete_button": "🗑️ Delete",
        
        # Portfolio summary
        "portfolio_summary_title": "Portfolio Summary",
        "portfolio_valid_message": "✅ Portfolio is valid and ready for analysis",
        "portfolio_error_message": "❌ Portfolio Validation Error: {}",
        "fix_error_warning": "Fix the issue before running analysis.",
        "total_value_metric": "Total Portfolio Value",
        "num_assets_metric": "Number of Assets",
        "target_sum_metric": "Target Weights Sum",
        "reset_button": "🔄 Reset to Example",
        "reset_button_help": "Reset to default 3-asset example portfolio",
        
        # Tab 2: Analysis
        "analysis_title": "Rebalancing Analysis",
        "analysis_description": "Run the rebalancing algorithm to see what operations are needed. Results mirror the structure of the Excel output file.",
        "cannot_run_warning": "⚠️ Cannot run analysis: {}",
        "fix_portfolio_info": "👉 Please go to the **Target & Portfolio** tab to fix the portfolio configuration.",
        "run_analysis_button": "▶️ Run Rebalancing Analysis",
        "calculating_message": "Calculating optimal rebalancing operations...",
        "calculation_complete": "✅ Rebalancing calculation complete!",
        "calculation_error": "Error during rebalancing: {}",
        
        # Analysis results
        "current_state_title": "📊 Current Portfolio State",
        "current_state_description": "Your portfolio before rebalancing:",
        "total_value_before_metric": "Total Value (Before)",
        "available_cash_metric": "Available Cash",
        "operations_title": "🔄 Required Operations",
        "operations_description": "Buy and sell operations needed to reach target allocation:",
        "cash_flow_title": "💰 Cash Flow Summary",
        "cash_flow_description": "Financial impact of the rebalancing operations:",
        "cash_from_sales_metric": "Cash from Sales",
        "cash_from_sales_help": "Total cash generated from selling assets (after tax and commissions)",
        "cash_for_purchases_metric": "Cash for Purchases",
        "cash_for_purchases_help": "Total cash needed for buying assets (including commissions)",
        "net_cash_flow_metric": "Net Cash Flow",
        "net_cash_flow_help": "Positive = surplus, Negative = you need to add cash, ~0 = balanced",
        "cash_balanced_message": "✅ Cash flow is balanced (no external funds needed)",
        "cash_needed_warning": "⚠️ You'll need to add {} to complete purchases",
        "cash_leftover_info": "ℹ️ You'll have {} left over after rebalancing",
        
        # Cost breakdown
        "cost_breakdown_title": "💳 Rebalancing Cost Breakdown",
        "cost_breakdown_description": "Total cost to execute the rebalancing operations:",
        "total_cost_metric": "💸 Total Cost to Rebalance",
        "total_cost_help": "Sum of all taxes and transaction fees",
        "cost_components_title": "Cost Components:",
        "transaction_fees_section": "Transaction Fees (Commissions)",
        "buy_commissions_metric": "Buy Commissions",
        "sell_commissions_metric": "Sell Commissions",
        "total_commissions_metric": "Total Commissions",
        "capital_gains_section": "Capital Gains Tax",
        "total_tax_metric": "Total Tax Paid",
        "tax_note_with_tax": "*Tax applies only to profitable sales*",
        "tax_note_no_tax": "*No capital gains tax (no profitable sales)*",
        "cost_note": """**Note on costs:**
- **Commissions** are charged by your broker on each transaction
- **Capital gains tax** applies only when selling assets at a profit
- These costs are already reflected in the cash flow calculations above
- The total cost reduces the effective return of your rebalancing""",
        
        # Post-rebalancing
        "post_rebalancing_title": "🎯 Post-Rebalancing Portfolio",
        "post_rebalancing_description": "Your portfolio after executing the operations:",
        "total_value_after_metric": "Total Value (After)",
        "max_deviation_metric": "Max Weight Deviation",
        "deviation_excellent": "✅ Excellent: All weights within 1% of target",
        "deviation_good": "ℹ️ Good: All weights within 5% of target",
        "deviation_warning": "⚠️ Large deviations remain (consider adjusting parameters)",
        "disclaimer_note": "**Note:** This is a calculation tool, not financial advice. Always verify calculations and consult a financial advisor if needed.",
        "click_to_run_info": "👆 Click 'Run Rebalancing Analysis' above to calculate operations.",
        
        # Error messages for invalid portfolio after results
        "portfolio_changed_error": "⚠️ Portfolio configuration has changed and is no longer valid: {}",
        "portfolio_changed_warning": "👉 Please go to the **Target & Portfolio** tab to fix the issues, then run the analysis again.",
        "results_invalid_info": "The previous results are no longer accurate and cannot be displayed.",
        "display_error": "⚠️ An error occurred while displaying the results.",
        "verify_settings_warning": "👉 The portfolio configuration may have changed. Please go to the **Target & Portfolio** tab to verify your settings, then run the analysis again.",
        "technical_details_expander": "🔧 Technical Details (for debugging)",
        
        # Table column headers - Current Portfolio State
        "table_symbol": "Symbol",
        "table_quantity": "Quantity",
        "table_price": "Price",
        "table_value": "Value",
        "table_current_weight": "Current Weight",
        "table_target_weight": "Target Weight",
        "table_deviation": "Deviation",
        
        # Table column headers - Required Operations
        "table_action": "Action",
        "table_tax_if_selling": "Tax (if selling)",
        
        # Table column headers - Post-Rebalancing
        "table_new_quantity": "New Quantity",
        "table_new_value": "New Value",
        "table_new_weight": "New Weight",
        
        # Tab 3: Settings
        "settings_title": "Algorithm Settings",
        "settings_description": "Configure how the rebalancing algorithm behaves. These settings affect the calculation in the Analysis tab.",
        "rounding_section_title": "Share Rounding",
        "rounding_section_description": "Some assets require whole shares. Enable rounding to convert fractional share calculations to integers.",
        "apply_rounding_checkbox": "Apply rounding to share quantities",
        "apply_rounding_help": "Round calculated share quantities to whole numbers",
        "rounding_method_label": "Rounding method:",
        "rounding_method_help": "FLOOR: Round down, ROUND: Round to nearest, CEIL: Round up",
        "rounding_floor_info": "🔽 **FLOOR**: Always rounds down. Conservative, may leave cash unallocated.",
        "rounding_round_info": "🎯 **ROUND**: Rounds to nearest integer. Balanced approach (recommended).",
        "rounding_ceil_info": "🔼 **CEIL**: Always rounds up. May require slightly more cash.",
        "rounding_warning": "**Note:** Rounding will cause the final weights to deviate slightly from targets and the cash flow may not be exactly zero. These deviations are reported in the Analysis.",
        
        # Algorithm information
        "algorithm_info_title": "Algorithm Information",
        "algorithm_info_text": """This tool uses a **deterministic 8-step algorithm**:
1. Compute current portfolio state
2. Calculate deviations from target weights
3. Compute target value changes
4. Convert to share quantities
5. Calculate cash flow (with tax and commissions)
6. Close cash flow (proportional scaling)
7. Simulate post-rebalancing state
8. Apply rounding (optional)

**Key Features:**
- ✅ Deterministic (same input → same output)
- ✅ No complex optimization (simple, transparent math)
- ✅ Tax-aware (capital gains tax included)
- ✅ Commission-aware (broker fees included)
- ✅ Cash-neutral or cash-deployment capable

For more details, see the documentation in the `docs/` folder.""",
        "assumptions_expander": "📋 Assumptions & Limitations",
        "assumptions_text": """**Assumptions:**
- Prices remain constant during execution
- Infinite liquidity (can buy/sell any quantity)
- All operations execute simultaneously
- Average cost basis is known

**Limitations:**
- Single currency only
- Linear capital gains tax
- No tax loss harvesting
- No lot size constraints (unless rounding is enabled)

**Not Included:**
- Market predictions or forecasts
- Risk/return optimization
- Asset selection or recommendations
- Automatic order execution""",
        
        # Footer
        "footer_text": "Portfolio Rebalancer v0.1.1 | <a href='https://github.com/jacopo-monti/portfolio-rebalancer' target='_blank'>GitHub</a> | Local demo - no data is stored or transmitted",
    },
    
    "it": {
        # App title and header
        "app_title": "Strumento di Ribilanciamento Portfolio",
        "app_subtitle": "Un calcolatore deterministico e fiscalmente consapevole per il ribilanciamento del portfolio",
        "language_selector_label": "Lingua",
        
        # Sidebar
        "sidebar_title": "Ribilanciatore Portfolio",
        "sidebar_about_title": "Informazioni",
        "sidebar_about_text": """Questo è uno strumento di ribilanciamento portfolio **deterministico** che:
- Calcola le operazioni di acquisto/vendita ottimali
- Considera le imposte sulle plusvalenze
- Gestisce le commissioni del broker
- Mantiene la neutralità del flusso di cassa""",
        "sidebar_how_to_title": "Come Usarlo",
        "sidebar_how_to_text": """1. **Target & Portfolio**: Aggiungi asset e definisci gli obiettivi
2. **Analisi**: Esegui il ribilanciamento e visualizza i risultati
3. **Impostazioni**: Configura i parametri dell'algoritmo""",
        "sidebar_note_title": "Nota",
        "sidebar_note_text": """Questo strumento è **solo per scopi di calcolo**, non è consulenza finanziaria.
Tutti i dati sono memorizzati in memoria e vengono persi quando chiudi il browser.""",
        
        # Tab names
        "tab_portfolio": "🎯 Target & Portfolio",
        "tab_analysis": "📈 Analisi",
        "tab_settings": "⚙️ Impostazioni",
        
        # Tab 1: Portfolio Configuration
        "portfolio_config_title": "Configurazione Portfolio",
        "portfolio_config_description": "Costruisci il tuo portfolio aggiungendo gli asset uno alla volta. Definisci le partecipazioni attuali e l'allocazione target per ciascun asset.",
        "portfolio_name_label": "Nome Portfolio",
        "portfolio_name_help": "Dai un nome al tuo portfolio per identificarlo",
        "cash_available_label": "Liquidità Disponibile da Investire (€)",
        "cash_available_help": "Liquidità aggiuntiva che vuoi investire. Imposta a 0 per un ribilanciamento neutrale rispetto alla liquidità.",
        
        # Asset form
        "add_asset_title": "Aggiungi Asset",
        "edit_asset_title": "Modifica Asset",
        "basic_info_section": "Informazioni di Base",
        "asset_symbol_label": "Simbolo/Nome Asset *",
        "asset_symbol_help": "es., VWCE, AAPL, BTC",
        "quantity_label": "Quantità (azioni) *",
        "quantity_help": "Numero di azioni che possiedi attualmente",
        "current_price_label": "Prezzo Attuale (€) *",
        "current_price_help": "Prezzo di mercato attuale per azione",
        "avg_cost_label": "Costo Medio (€) *",
        "avg_cost_help": "Il tuo prezzo medio di acquisto (per il calcolo fiscale)",
        "tax_rate_label": "Aliquota Fiscale (%) *",
        "tax_rate_help": "Aliquota fiscale sulle plusvalenze",
        "target_weight_label": "Peso Target (%) *",
        "target_weight_help": "Allocazione desiderata nel portfolio",
        
        # Commission settings
        "commission_section": "📋 Impostazioni Commissioni (Opzionale)",
        "buy_commissions_title": "Commissioni di Acquisto",
        "sell_commissions_title": "Commissioni di Vendita",
        "fixed_fee_label": "Commissione Fissa (€)",
        "pct_fee_label": "Commissione %",
        "min_fee_label": "Commissione Min (€)",
        "max_fee_label": "Commissione Max (€)",
        
        # Form buttons
        "update_asset_button": "✅ Aggiorna Asset",
        "add_asset_button": "➕ Aggiungi Asset al Portfolio",
        "cancel_button": "❌ Annulla",
        
        # Validation messages
        "error_empty_symbol": "Nome/simbolo asset non può essere vuoto",
        "error_negative_quantity": "La quantità deve essere ≥ 0",
        "error_invalid_price": "Il prezzo deve essere > 0",
        "error_negative_avg_cost": "Il costo medio deve essere ≥ 0",
        "error_invalid_tax_rate": "L'aliquota fiscale deve essere tra 0% e 100%",
        "error_invalid_target_weight": "Il peso target deve essere tra 0% e 100%",
        "error_negative_commission": "{} deve essere ≥ 0",
        "error_invalid_pct_commission": "{} deve essere ≤ 100%",
        "error_duplicate_symbol": "L'asset '{}' esiste già nel portfolio",
        "success_asset_updated": "Asset '{}' aggiornato con successo!",
        "success_asset_added": "Asset '{}' aggiunto al portfolio!",
        
        # Portfolio display
        "current_portfolio_title": "Asset del Portfolio Corrente",
        "no_assets_message": "📝 Nessun asset nel portfolio. Aggiungi il tuo primo asset usando il modulo sopra.",
        "value_label": "Valore",
        "target_label": "Target",
        "quantity_short_label": "Quantità",
        "details_expander": "📊 Dettagli",
        "holdings_section": "Partecipazioni",
        "tax_target_section": "Fiscalità & Target",
        "commissions_section": "Commissioni",
        "buy_label": "Acquisto",
        "sell_label": "Vendita",
        "none_label": "Nessuna",
        "edit_button": "✏️ Modifica",
        "delete_button": "🗑️ Elimina",
        
        # Portfolio summary
        "portfolio_summary_title": "Riepilogo Portfolio",
        "portfolio_valid_message": "✅ Il portfolio è valido e pronto per l'analisi",
        "portfolio_error_message": "❌ Errore di Validazione Portfolio: {}",
        "fix_error_warning": "Risolvi il problema prima di eseguire l'analisi.",
        "total_value_metric": "Valore Totale Portfolio",
        "num_assets_metric": "Numero di Asset",
        "target_sum_metric": "Somma Pesi Target",
        "reset_button": "🔄 Ripristina Esempio",
        "reset_button_help": "Ripristina il portfolio di esempio predefinito con 3 asset",
        
        # Tab 2: Analysis
        "analysis_title": "Analisi di Ribilanciamento",
        "analysis_description": "Esegui l'algoritmo di ribilanciamento per vedere quali operazioni sono necessarie. I risultati rispecchiano la struttura del file Excel di output.",
        "cannot_run_warning": "⚠️ Impossibile eseguire l'analisi: {}",
        "fix_portfolio_info": "👉 Vai alla scheda **Target & Portfolio** per correggere la configurazione del portfolio.",
        "run_analysis_button": "▶️ Esegui Analisi di Ribilanciamento",
        "calculating_message": "Calcolo delle operazioni di ribilanciamento ottimali...",
        "calculation_complete": "✅ Calcolo del ribilanciamento completato!",
        "calculation_error": "Errore durante il ribilanciamento: {}",
        
        # Analysis results
        "current_state_title": "📊 Stato Corrente del Portfolio",
        "current_state_description": "Il tuo portfolio prima del ribilanciamento:",
        "total_value_before_metric": "Valore Totale (Prima)",
        "available_cash_metric": "Liquidità Disponibile",
        "operations_title": "🔄 Operazioni Necessarie",
        "operations_description": "Operazioni di acquisto e vendita necessarie per raggiungere l'allocazione target:",
        "cash_flow_title": "💰 Riepilogo Flusso di Cassa",
        "cash_flow_description": "Impatto finanziario delle operazioni di ribilanciamento:",
        "cash_from_sales_metric": "Liquidità da Vendite",
        "cash_from_sales_help": "Liquidità totale generata dalla vendita di asset (al netto di tasse e commissioni)",
        "cash_for_purchases_metric": "Liquidità per Acquisti",
        "cash_for_purchases_help": "Liquidità totale necessaria per l'acquisto di asset (incluse commissioni)",
        "net_cash_flow_metric": "Flusso di Cassa Netto",
        "net_cash_flow_help": "Positivo = surplus, Negativo = devi aggiungere liquidità, ~0 = bilanciato",
        "cash_balanced_message": "✅ Il flusso di cassa è bilanciato (non servono fondi esterni)",
        "cash_needed_warning": "⚠️ Dovrai aggiungere {} per completare gli acquisti",
        "cash_leftover_info": "ℹ️ Avrai {} residui dopo il ribilanciamento",
        
        # Cost breakdown
        "cost_breakdown_title": "💳 Dettaglio Costi di Ribilanciamento",
        "cost_breakdown_description": "Costo totale per eseguire le operazioni di ribilanciamento:",
        "total_cost_metric": "💸 Costo Totale per Ribilanciare",
        "total_cost_help": "Somma di tutte le tasse e commissioni di transazione",
        "cost_components_title": "Componenti del Costo:",
        "transaction_fees_section": "Commissioni di Transazione",
        "buy_commissions_metric": "Commissioni di Acquisto",
        "sell_commissions_metric": "Commissioni di Vendita",
        "total_commissions_metric": "Commissioni Totali",
        "capital_gains_section": "Imposte sulle Plusvalenze",
        "total_tax_metric": "Imposte Totali Pagate",
        "tax_note_with_tax": "*Le imposte si applicano solo alle vendite con plusvalenza*",
        "tax_note_no_tax": "*Nessuna imposta sulle plusvalenze (nessuna vendita con profitto)*",
        "cost_note": """**Nota sui costi:**
- Le **commissioni** sono addebitate dal tuo broker su ogni transazione
- Le **imposte sulle plusvalenze** si applicano solo quando si vendono asset con profitto
- Questi costi sono già riflessi nei calcoli del flusso di cassa sopra
- Il costo totale riduce il rendimento effettivo del tuo ribilanciamento""",
        
        # Post-rebalancing
        "post_rebalancing_title": "🎯 Portfolio Post-Ribilanciamento",
        "post_rebalancing_description": "Il tuo portfolio dopo l'esecuzione delle operazioni:",
        "total_value_after_metric": "Valore Totale (Dopo)",
        "max_deviation_metric": "Deviazione Massima Peso",
        "deviation_excellent": "✅ Eccellente: Tutti i pesi entro l'1% del target",
        "deviation_good": "ℹ️ Buono: Tutti i pesi entro il 5% del target",
        "deviation_warning": "⚠️ Rimangono grandi deviazioni (considera di modificare i parametri)",
        "disclaimer_note": "**Nota:** Questo è uno strumento di calcolo, non una consulenza finanziaria. Verifica sempre i calcoli e consulta un consulente finanziario se necessario.",
        "click_to_run_info": "👆 Clicca su 'Esegui Analisi di Ribilanciamento' sopra per calcolare le operazioni.",
        
        # Error messages for invalid portfolio after results
        "portfolio_changed_error": "⚠️ La configurazione del portfolio è cambiata e non è più valida: {}",
        "portfolio_changed_warning": "👉 Vai alla scheda **Target & Portfolio** per correggere i problemi, poi esegui nuovamente l'analisi.",
        "results_invalid_info": "I risultati precedenti non sono più accurati e non possono essere visualizzati.",
        "display_error": "⚠️ Si è verificato un errore durante la visualizzazione dei risultati.",
        "verify_settings_warning": "👉 La configurazione del portfolio potrebbe essere cambiata. Vai alla scheda **Target & Portfolio** per verificare le impostazioni, poi esegui nuovamente l'analisi.",
        "technical_details_expander": "🔧 Dettagli Tecnici (per il debug)",
        
        # Table column headers - Current Portfolio State
        "table_symbol": "Simbolo",
        "table_quantity": "Quantità",
        "table_price": "Prezzo",
        "table_value": "Valore",
        "table_current_weight": "Peso Attuale",
        "table_target_weight": "Peso Target",
        "table_deviation": "Deviazione",
        
        # Table column headers - Required Operations
        "table_action": "Azione",
        "table_tax_if_selling": "Tassa (in caso di vendita)",
        
        # Table column headers - Post-Rebalancing
        "table_new_quantity": "Nuova Quantità",
        "table_new_value": "Nuovo Valore",
        "table_new_weight": "Nuovo Peso",
        
        # Tab 3: Settings
        "settings_title": "Impostazioni Algoritmo",
        "settings_description": "Configura il comportamento dell'algoritmo di ribilanciamento. Queste impostazioni influenzano il calcolo nella scheda Analisi.",
        "rounding_section_title": "Arrotondamento Azioni",
        "rounding_section_description": "Alcuni asset richiedono azioni intere. Abilita l'arrotondamento per convertire i calcoli delle azioni frazionarie in numeri interi.",
        "apply_rounding_checkbox": "Applica arrotondamento alle quantità di azioni",
        "apply_rounding_help": "Arrotonda le quantità di azioni calcolate a numeri interi",
        "rounding_method_label": "Metodo di arrotondamento:",
        "rounding_method_help": "FLOOR: Arrotonda per difetto, ROUND: Arrotonda al più vicino, CEIL: Arrotonda per eccesso",
        "rounding_floor_info": "🔽 **FLOOR**: Arrotonda sempre per difetto. Conservativo, può lasciare liquidità non allocata.",
        "rounding_round_info": "🎯 **ROUND**: Arrotonda al numero intero più vicino. Approccio bilanciato (consigliato).",
        "rounding_ceil_info": "🔼 **CEIL**: Arrotonda sempre per eccesso. Potrebbe richiedere leggermente più liquidità.",
        "rounding_warning": "**Nota:** L'arrotondamento causerà una leggera deviazione dei pesi finali dai target e il flusso di cassa potrebbe non essere esattamente zero. Queste deviazioni sono riportate nell'Analisi.",
        
        # Algorithm information
        "algorithm_info_title": "Informazioni sull'Algoritmo",
        "algorithm_info_text": """Questo strumento utilizza un **algoritmo deterministico in 8 passi**:
1. Calcola lo stato corrente del portfolio
2. Calcola le deviazioni dai pesi target
3. Calcola le variazioni di valore target
4. Converte in quantità di azioni
5. Calcola il flusso di cassa (con tasse e commissioni)
6. Chiude il flusso di cassa (scaling proporzionale)
7. Simula lo stato post-ribilanciamento
8. Applica l'arrotondamento (opzionale)

**Caratteristiche Principali:**
- ✅ Deterministico (stesso input → stesso output)
- ✅ Nessuna ottimizzazione complessa (matematica semplice e trasparente)
- ✅ Fiscalmente consapevole (imposte sulle plusvalenze incluse)
- ✅ Consapevole delle commissioni (commissioni del broker incluse)
- ✅ Neutrale rispetto alla liquidità o capace di deployare liquidità

Per maggiori dettagli, consulta la documentazione nella cartella `docs/`.""",
        "assumptions_expander": "📋 Assunzioni & Limitazioni",
        "assumptions_text": """**Assunzioni:**
- I prezzi rimangono costanti durante l'esecuzione
- Liquidità infinita (possibilità di comprare/vendere qualsiasi quantità)
- Tutte le operazioni vengono eseguite simultaneamente
- La base di costo medio è nota

**Limitazioni:**
- Solo una valuta
- Imposta lineare sulle plusvalenze
- Nessuna compensazione delle perdite fiscali
- Nessun vincolo di lotto minimo (a meno che l'arrotondamento non sia abilitato)

**Non Incluso:**
- Previsioni o forecast di mercato
- Ottimizzazione rischio/rendimento
- Selezione degli asset o raccomandazioni
- Esecuzione automatica degli ordini""",
        
        # Footer
        "footer_text": "Ribilanciatore Portfolio v0.1.1 | <a href='https://github.com/jacopo-monti/portfolio-rebalancer' target='_blank'>GitHub</a> | Demo locale - nessun dato viene memorizzato o trasmesso",
    },
}


# ============================================================================
# TRANSLATION FUNCTIONS
# ============================================================================

def get_text(key: str, lang: str = None, **kwargs) -> str:
    """Get translated text for a given key.
    
    Args:
        key: The translation key to lookup
        lang: Language code (if None, uses session state language)
        **kwargs: Format arguments for string formatting
        
    Returns:
        Translated text string
        
    Examples:
        >>> get_text('app_title')
        'Portfolio Rebalancing Tool'
        
        >>> get_text('error_duplicate_symbol', symbol='AAPL')
        "Asset 'AAPL' already exists in portfolio"
    """
    # Get language from session state if not provided
    if lang is None:
        lang = st.session_state.get('language', 'en')
    
    # Fallback to English if language not found
    if lang not in TRANSLATIONS:
        lang = 'en'
    
    # Get the translation
    text = TRANSLATIONS[lang].get(key, key)
    
    # Apply formatting if kwargs provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            # If formatting fails, return unformatted text
            pass
    
    return text


def get_available_languages() -> Dict[str, str]:
    """Get dictionary of available languages.
    
    Returns:
        Dictionary mapping language codes to display names
    """
    return {
        'en': 'English',
        'it': 'Italiano',
    }
