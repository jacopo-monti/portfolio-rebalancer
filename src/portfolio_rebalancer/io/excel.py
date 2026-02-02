"""Excel I/O handler for portfolio data."""

from __future__ import annotations

from typing import List

try:
    import openpyxl
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
except ImportError:
    raise ImportError(
        "openpyxl is required for Excel support. Install with: pip install openpyxl"
    )

from portfolio_rebalancer.models.asset import Asset
from portfolio_rebalancer.models.portfolio import Portfolio
from portfolio_rebalancer.models.result import RebalancingResult


class ExcelIO:
    """Handler for reading and writing portfolio data from/to Excel files.
    
    Excel file format for input:
    - Column A: Symbol (ticker)
    - Column B: Quantity (shares owned)
    - Column C: Price (current price)
    - Column D: Avg Cost (average purchase price)
    - Column E: Tax Rate (decimal, e.g., 0.26)
    - Column F: Target Weight (decimal, e.g., 0.60)
    
    First row should contain headers.
    """
    
    def read_portfolio(self, filepath: str, sheet_name: str = None) -> Portfolio:
        """Read portfolio from Excel file.
        
        Args:
            filepath: Path to Excel file
            sheet_name: Name of sheet to read (uses active sheet if None)
            
        Returns:
            Portfolio object with assets from Excel
            
        Raises:
            ValueError: If Excel file is invalid or data is malformed
        """
        try:
            workbook = openpyxl.load_workbook(filepath)
        except Exception as e:
            raise ValueError(f"Failed to load Excel file: {e}")
        
        if sheet_name:
            if sheet_name not in workbook.sheetnames:
                raise ValueError(f"Sheet '{sheet_name}' not found in workbook")
            sheet = workbook[sheet_name]
        else:
            sheet = workbook.active
        
        assets = []
        
        # Skip header row (row 1)
        for row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
            # Skip empty rows
            if not any(row):
                continue
            
            if len(row) < 6:
                raise ValueError(
                    f"Row {row_idx} has insufficient columns. Expected 6 columns: "
                    "Symbol, Quantity, Price, Avg Cost, Tax Rate, Target Weight"
                )
            
            symbol, quantity, price, avg_cost, tax_rate, target_weight = row[:6]
            
            # Validate data
            try:
                symbol = str(symbol).strip()
                quantity = float(quantity)
                price = float(price)
                avg_cost = float(avg_cost)
                tax_rate = float(tax_rate)
                target_weight = float(target_weight)
            except (ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid data in row {row_idx}: {e}. "
                    "Ensure all numeric columns contain valid numbers."
                )
            
            asset = Asset(
                symbol=symbol,
                quantity=quantity,
                price=price,
                avg_cost=avg_cost,
                tax_rate=tax_rate,
                target_weight=target_weight,
            )
            assets.append(asset)
        
        if not assets:
            raise ValueError("No assets found in Excel file")
        
        portfolio = Portfolio(assets=assets)
        return portfolio
    
    def _adjust_column_widths(self, sheet) -> None:
        """Adjust column widths based on content.
        
        Args:
            sheet: openpyxl worksheet
        """
        for column_cells in sheet.columns:
            max_length = 0
            # Get column letter from first non-merged cell
            column_letter = None
            for cell in column_cells:
                # Skip merged cells
                if hasattr(cell, 'column_letter'):
                    if column_letter is None:
                        column_letter = cell.column_letter
                    try:
                        cell_value = str(cell.value) if cell.value is not None else ""
                        if len(cell_value) > max_length:
                            max_length = len(cell_value)
                    except:
                        pass
            
            if column_letter:
                adjusted_width = min(max_length + 2, 50)
                sheet.column_dimensions[column_letter].width = max(adjusted_width, 10)
    
    def write_result(
        self, result: RebalancingResult, filepath: str, sheet_name: str = "Rebalancing"
    ) -> None:
        """Write rebalancing results to Excel file.
        
        Args:
            result: RebalancingResult to write
            filepath: Path to output Excel file
            sheet_name: Name of sheet to create
        """
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = sheet_name
        
        # Styles
        header_font = Font(bold=True, size=12, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        title_font = Font(bold=True, size=14)
        section_font = Font(bold=True, size=12)
        
        # Title
        sheet["A1"] = "Portfolio Rebalancing Results"
        sheet["A1"].font = title_font
        sheet.merge_cells("A1:H1")
        
        # Summary section
        row = 3
        sheet[f"A{row}"] = "Summary"
        sheet[f"A{row}"].font = section_font
        
        row += 1
        sheet[f"A{row}"] = "Total Portfolio Value Before:"
        sheet[f"B{row}"] = result.total_value_before
        sheet[f"B{row}"].number_format = '€#,##0.00'
        
        row += 1
        sheet[f"A{row}"] = "Total Portfolio Value After:"
        sheet[f"B{row}"] = result.total_value_after
        sheet[f"B{row}"].number_format = '€#,##0.00'
        
        row += 1
        sheet[f"A{row}"] = "Cash Flow:"
        sheet[f"B{row}"] = result.cash_flow
        sheet[f"B{row}"].number_format = '€#,##0.00'
        
        row += 1
        sheet[f"A{row}"] = "Total Cash In:"
        sheet[f"B{row}"] = result.total_cash_in
        sheet[f"B{row}"].number_format = '€#,##0.00'
        
        row += 1
        sheet[f"A{row}"] = "Total Cash Out:"
        sheet[f"B{row}"] = result.total_cash_out
        sheet[f"B{row}"].number_format = '€#,##0.00'
        
        row += 1
        sheet[f"A{row}"] = "Total Tax Paid:"
        sheet[f"B{row}"] = result.total_tax_paid
        sheet[f"B{row}"].number_format = '€#,##0.00'
        
        row += 1
        sheet[f"A{row}"] = "Max Deviation from Target:"
        sheet[f"B{row}"] = result.max_deviation
        sheet[f"B{row}"].number_format = '0.00%'
        
        row += 1
        sheet[f"A{row}"] = "Number of Operations:"
        sheet[f"B{row}"] = result.num_operations
        
        # Operations section
        row += 3
        sheet[f"A{row}"] = "Operations Needed"
        sheet[f"A{row}"].font = section_font
        
        row += 1
        headers = [
            "Symbol",
            "Action",
            "Quantity Change",
            "Value Change (€)",
            "Current Qty",
            "New Qty",
            "Current Weight",
            "Target Weight",
        ]
        
        for col_idx, header in enumerate(headers, start=1):
            cell = sheet.cell(row=row, column=col_idx)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Asset rows
        for asset in result.assets:
            row += 1
            action = "BUY" if asset.delta_quantity > 0 else ("SELL" if asset.delta_quantity < 0 else "HOLD")
            new_qty = asset.quantity + asset.delta_quantity
            new_value = new_qty * asset.price
            new_weight = new_value / result.total_value_after if result.total_value_after > 0 else 0
            
            sheet[f"A{row}"] = asset.symbol
            sheet[f"B{row}"] = action
            sheet[f"C{row}"] = asset.delta_quantity
            sheet[f"C{row}"].number_format = '0.00'
            sheet[f"D{row}"] = asset.delta_value
            sheet[f"D{row}"].number_format = '€#,##0.00'
            sheet[f"E{row}"] = asset.quantity
            sheet[f"E{row}"].number_format = '0.00'
            sheet[f"F{row}"] = new_qty
            sheet[f"F{row}"].number_format = '0.00'
            sheet[f"G{row}"] = asset.current_weight
            sheet[f"G{row}"].number_format = '0.00%'
            sheet[f"H{row}"] = asset.target_weight
            sheet[f"H{row}"].number_format = '0.00%'
        
        # Final Portfolio section
        row += 3
        sheet[f"A{row}"] = "Final Portfolio Weights"
        sheet[f"A{row}"].font = section_font
        
        row += 1
        final_headers = [
            "Symbol",
            "Final Quantity",
            "Price",
            "Final Value (€)",
            "Final Weight",
            "Target Weight",
            "Deviation",
        ]
        
        for col_idx, header in enumerate(final_headers, start=1):
            cell = sheet.cell(row=row, column=col_idx)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Final portfolio rows
        for asset in result.assets:
            row += 1
            final_qty = asset.quantity + asset.delta_quantity
            final_value = final_qty * asset.price
            final_weight = final_value / result.total_value_after if result.total_value_after > 0 else 0
            deviation = final_weight - asset.target_weight
            
            sheet[f"A{row}"] = asset.symbol
            sheet[f"B{row}"] = final_qty
            sheet[f"B{row}"].number_format = '0.00'
            sheet[f"C{row}"] = asset.price
            sheet[f"C{row}"].number_format = '€#,##0.00'
            sheet[f"D{row}"] = final_value
            sheet[f"D{row}"].number_format = '€#,##0.00'
            sheet[f"E{row}"] = final_weight
            sheet[f"E{row}"].number_format = '0.00%'
            sheet[f"F{row}"] = asset.target_weight
            sheet[f"F{row}"].number_format = '0.00%'
            sheet[f"G{row}"] = deviation
            sheet[f"G{row}"].number_format = '0.00%'
            
            # Color code deviation (green if close to target, yellow/red if far)
            if abs(deviation) < 0.001:  # Within 0.1%
                sheet[f"G{row}"].font = Font(color="006100", bold=True)  # Dark green
            elif abs(deviation) < 0.01:  # Within 1%
                sheet[f"G{row}"].font = Font(color="9C6500")  # Dark yellow
            else:
                sheet[f"G{row}"].font = Font(color="9C0006")  # Dark red
        
        # Total row
        row += 1
        sheet[f"A{row}"] = "TOTAL"
        sheet[f"A{row}"].font = Font(bold=True)
        sheet[f"D{row}"] = result.total_value_after
        sheet[f"D{row}"].number_format = '€#,##0.00'
        sheet[f"D{row}"].font = Font(bold=True)
        
        # Sum of final weights (should be 100%)
        total_weight = sum(
            (asset.quantity + asset.delta_quantity) * asset.price / result.total_value_after
            for asset in result.assets
        ) if result.total_value_after > 0 else 0
        sheet[f"E{row}"] = total_weight
        sheet[f"E{row}"].number_format = '0.00%'
        sheet[f"E{row}"].font = Font(bold=True)
        
        # Adjust column widths
        self._adjust_column_widths(sheet)
        
        # Save workbook
        try:
            workbook.save(filepath)
        except Exception as e:
            raise IOError(f"Failed to save Excel file: {e}")
    
    def write_portfolio(
        self, portfolio: Portfolio, filepath: str, sheet_name: str = "Portfolio"
    ) -> None:
        """Write portfolio to Excel file (template format).
        
        Args:
            portfolio: Portfolio to write
            filepath: Path to output Excel file
            sheet_name: Name of sheet to create
        """
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = sheet_name
        
        # Styles
        header_font = Font(bold=True, size=11, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        header_alignment = Alignment(horizontal="center", vertical="center")
        
        # Headers
        headers = ["Symbol", "Quantity", "Price", "Avg Cost", "Tax Rate", "Target Weight"]
        for col_idx, header in enumerate(headers, start=1):
            cell = sheet.cell(row=1, column=col_idx)
            cell.value = header
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
        
        # Asset rows
        for row_idx, asset in enumerate(portfolio.assets, start=2):
            sheet[f"A{row_idx}"] = asset.symbol
            sheet[f"B{row_idx}"] = asset.quantity
            sheet[f"B{row_idx}"].number_format = '0.00'
            sheet[f"C{row_idx}"] = asset.price
            sheet[f"C{row_idx}"].number_format = '€#,##0.00'
            sheet[f"D{row_idx}"] = asset.avg_purchase_price
            sheet[f"D{row_idx}"].number_format = '€#,##0.00'
            sheet[f"E{row_idx}"] = asset.tax_rate
            sheet[f"E{row_idx}"].number_format = '0.00%'
            sheet[f"F{row_idx}"] = asset.target_weight
            sheet[f"F{row_idx}"].number_format = '0.00%'
        
        # Adjust column widths
        self._adjust_column_widths(sheet)
        
        # Save workbook
        try:
            workbook.save(filepath)
        except Exception as e:
            raise IOError(f"Failed to save Excel file: {e}")
