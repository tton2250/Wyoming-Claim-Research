"""Main application window for Wyoming Claim Research."""

import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional, Set
from pathlib import Path

from models.commodity import CommodityType, get_all_commodities
from models.lease import Lease, LeaseStatus
from .legend import CommodityLegend, CompactLegend
from .lease_table import LeaseTableView
from .filters import FilterPanel


class WyomingClaimApp(tk.Tk):
    """
    Main application window for Wyoming Claim Research.

    Features:
    - Lease table view with sorting and filtering
    - Commodity type legend with color coding
    - Filter panel for advanced filtering
    - Data import/export functionality
    - Lease detail view
    """

    def __init__(self):
        """Initialize the application."""
        super().__init__()

        self.title("Wyoming Claim Research")
        self.geometry("1400x800")
        self.minsize(1000, 600)

        # Data
        self.leases: List[Lease] = []
        self.selected_commodities: Set[CommodityType] = set(get_all_commodities())

        # Set up the UI
        self._setup_styles()
        self._setup_menu()
        self._setup_ui()

        # Load sample data if available
        self._load_sample_data()

    def _setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()

        # Use a modern theme if available
        available_themes = style.theme_names()
        if 'clam' in available_themes:
            style.theme_use('clam')
        elif 'vista' in available_themes:
            style.theme_use('vista')

        # Custom styles
        style.configure('Title.TLabel', font=('Helvetica', 14, 'bold'))
        style.configure('Header.TLabel', font=('Helvetica', 11, 'bold'))
        style.configure('Status.TLabel', foreground='gray')

    def _setup_menu(self):
        """Set up the application menu bar."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Data File...", command=self._open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save Data...", command=self._save_file, accelerator="Ctrl+S")
        file_menu.add_separator()
        file_menu.add_command(label="Export to CSV...", command=self._export_csv)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit, accelerator="Ctrl+Q")

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Select All", command=self._select_all, accelerator="Ctrl+A")
        edit_menu.add_command(label="Clear Selection", command=self._clear_selection)

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Show All Commodities", command=self._show_all_commodities)
        view_menu.add_command(label="Reset Filters", command=self._reset_filters)
        view_menu.add_separator()
        view_menu.add_command(label="Refresh", command=self._refresh_data, accelerator="F5")

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

        # Keyboard bindings
        self.bind('<Control-o>', lambda e: self._open_file())
        self.bind('<Control-s>', lambda e: self._save_file())
        self.bind('<Control-q>', lambda e: self.quit())
        self.bind('<Control-a>', lambda e: self._select_all())
        self.bind('<F5>', lambda e: self._refresh_data())

    def _setup_ui(self):
        """Set up the main user interface."""
        # Main container with paned windows
        main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel - Filters and Legend
        left_frame = ttk.Frame(main_paned, width=280)
        main_paned.add(left_frame, weight=0)

        # Filter panel
        self.filter_panel = FilterPanel(
            left_frame,
            on_filter_change=self._apply_filters
        )
        self.filter_panel.pack(fill=tk.X, padx=5, pady=5)

        # Commodity legend
        self.legend = CommodityLegend(
            left_frame,
            on_filter_change=self._on_commodity_filter_change
        )
        self.legend.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Right panel - Main content
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame, weight=1)

        # Header with title and compact legend
        header_frame = ttk.Frame(right_frame)
        header_frame.pack(fill=tk.X, pady=(0, 5))

        title_label = ttk.Label(
            header_frame,
            text="Wyoming State Mineral Leases",
            style='Title.TLabel'
        )
        title_label.pack(side=tk.LEFT)

        # Compact legend in header
        self.compact_legend = CompactLegend(header_frame)
        self.compact_legend.pack(side=tk.RIGHT)

        # Lease table
        self.lease_table = LeaseTableView(
            right_frame,
            on_selection_change=self._on_selection_change,
            on_double_click=self._on_lease_double_click
        )
        self.lease_table.pack(fill=tk.BOTH, expand=True)

        # Status bar
        self.status_bar = ttk.Frame(self)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_text = ttk.Label(
            self.status_bar,
            text="Ready",
            style='Status.TLabel'
        )
        self.status_text.pack(side=tk.LEFT, padx=10, pady=5)

        # Progress bar (hidden by default)
        self.progress = ttk.Progressbar(
            self.status_bar,
            mode='indeterminate',
            length=100
        )

    def _load_sample_data(self):
        """Load sample data if available."""
        sample_path = Path(__file__).parent.parent / 'data' / 'sample_leases.json'
        if sample_path.exists():
            try:
                self._load_data_from_file(str(sample_path))
            except Exception as e:
                print(f"Could not load sample data: {e}")
        else:
            # Generate some sample data for demonstration
            self._generate_sample_data()

    def _generate_sample_data(self):
        """Generate sample lease data for demonstration."""
        from datetime import date, timedelta
        import random

        counties = ['Campbell', 'Converse', 'Natrona', 'Sweetwater', 'Carbon',
                    'Fremont', 'Sublette', 'Uinta', 'Lincoln', 'Hot Springs']

        commodities = [
            CommodityType.OIL,
            CommodityType.GAS,
            CommodityType.OIL_AND_GAS,
            CommodityType.COAL,
            CommodityType.TRONA,
            CommodityType.URANIUM,
            CommodityType.BENTONITE,
        ]

        statuses = [
            LeaseStatus.ACTIVE,
            LeaseStatus.PRODUCING,
            LeaseStatus.HELD_BY_PRODUCTION,
            LeaseStatus.EXPIRED,
            LeaseStatus.PENDING,
        ]

        lessees = [
            "Petroleum Development Corp",
            "Wyoming Energy Partners LLC",
            "Rocky Mountain Resources Inc",
            "High Plains Oil & Gas",
            "Frontier Minerals LLC",
            "Basin Energy Group",
            "Continental Mining Co",
            "Prairie States Petroleum",
            "Thunder Basin Resources",
            "Powder River Energy",
        ]

        sample_leases = []
        for i in range(150):
            lease_num = f"WY-{random.randint(1000, 9999)}-{random.randint(100, 999)}"
            commodity = random.choice(commodities)
            status = random.choice(statuses)
            county = random.choice(counties)
            acres = random.uniform(40, 2560)

            # Generate dates
            effective = date.today() - timedelta(days=random.randint(30, 3650))
            expiration = effective + timedelta(days=random.randint(365, 3650))

            # Wyoming coordinates (approximate)
            lat = random.uniform(41.0, 45.0)
            lon = random.uniform(-111.0, -104.0)

            lease = Lease(
                lease_number=lease_num,
                commodity_type=commodity,
                status=status,
                county=county,
                acres=round(acres, 1),
                effective_date=effective,
                expiration_date=expiration,
                lessee_name=random.choice(lessees),
                township=str(random.randint(10, 55)) + random.choice(['N', 'S']),
                range_str=str(random.randint(60, 110)) + random.choice(['E', 'W']),
                section=str(random.randint(1, 36)),
                annual_rental=acres * random.uniform(1.0, 5.0),
                royalty_rate=random.choice([0.125, 0.1667, 0.20]),
                latitude=lat,
                longitude=lon,
            )
            sample_leases.append(lease)

        self.leases = sample_leases
        self._refresh_data()
        self._update_status(f"Loaded {len(sample_leases)} sample leases")

    def _load_data_from_file(self, filepath: str):
        """Load lease data from a JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, list):
            self.leases = [Lease.from_dict(item) for item in data]
        elif isinstance(data, dict) and 'leases' in data:
            self.leases = [Lease.from_dict(item) for item in data['leases']]
        else:
            raise ValueError("Invalid data format")

        self._refresh_data()
        self._update_status(f"Loaded {len(self.leases)} leases from {Path(filepath).name}")

    def _refresh_data(self):
        """Refresh the displayed data."""
        self.lease_table.set_leases(self.leases)
        self._apply_filters()
        self._update_legend_counts()

    def _apply_filters(self):
        """Apply all current filters to the lease table."""
        filter_values = self.filter_panel.get_filter_values()

        self.lease_table.filter_leases(
            commodities=self.selected_commodities,
            statuses=filter_values.get('statuses'),
            county=filter_values.get('county'),
            search_text=filter_values.get('search_text'),
            min_acres=filter_values.get('min_acres'),
            max_acres=filter_values.get('max_acres'),
            date_from=filter_values.get('date_from'),
            date_to=filter_values.get('date_to'),
        )

        self._update_legend_counts()

    def _on_commodity_filter_change(self, selected: Set[CommodityType]):
        """Handle commodity filter change from legend."""
        self.selected_commodities = selected
        self._apply_filters()

    def _update_legend_counts(self):
        """Update the commodity counts in the legend."""
        counts = self.lease_table.get_commodity_counts()
        self.legend.update_counts(counts)

    def _on_selection_change(self, selected_leases: List[Lease]):
        """Handle selection change in the table."""
        count = len(selected_leases)
        if count == 0:
            self._update_status("Ready")
        elif count == 1:
            lease = selected_leases[0]
            self._update_status(f"Selected: {lease.lease_number} - {lease.commodity_type.value}")
        else:
            total_acres = sum(l.acres for l in selected_leases)
            self._update_status(f"Selected {count} leases ({total_acres:,.1f} total acres)")

    def _on_lease_double_click(self, lease: Lease):
        """Handle double-click on a lease to show details."""
        self._show_lease_details(lease)

    def _show_lease_details(self, lease: Lease):
        """Show a detail dialog for a lease."""
        dialog = tk.Toplevel(self)
        dialog.title(f"Lease Details - {lease.lease_number}")
        dialog.geometry("500x600")
        dialog.transient(self)
        dialog.grab_set()

        # Details frame
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)

        # Title
        ttk.Label(
            frame,
            text=lease.lease_number,
            style='Title.TLabel'
        ).pack(anchor=tk.W)

        ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Details grid
        details_frame = ttk.Frame(frame)
        details_frame.pack(fill=tk.BOTH, expand=True)

        details = [
            ("Commodity Type:", lease.commodity_type.value),
            ("Status:", lease.status.value),
            ("County:", lease.county),
            ("Acres:", f"{lease.acres:,.1f}"),
            ("Lessee:", lease.lessee_name),
            ("Effective Date:", lease.effective_date.strftime('%Y-%m-%d') if lease.effective_date else 'N/A'),
            ("Expiration Date:", lease.expiration_date.strftime('%Y-%m-%d') if lease.expiration_date else 'N/A'),
            ("Location:", lease.location_str),
            ("Annual Rental:", f"${lease.annual_rental:,.2f}"),
            ("Royalty Rate:", f"{lease.royalty_rate * 100:.2f}%"),
        ]

        if lease.has_coordinates:
            details.append(("Coordinates:", f"{lease.latitude:.4f}, {lease.longitude:.4f}"))

        for i, (label, value) in enumerate(details):
            ttk.Label(
                details_frame,
                text=label,
                style='Header.TLabel'
            ).grid(row=i, column=0, sticky=tk.E, padx=(0, 10), pady=3)

            ttk.Label(
                details_frame,
                text=value
            ).grid(row=i, column=1, sticky=tk.W, pady=3)

        # Notes section
        if lease.notes:
            ttk.Separator(frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
            ttk.Label(frame, text="Notes:", style='Header.TLabel').pack(anchor=tk.W)
            notes_text = tk.Text(frame, height=4, wrap=tk.WORD)
            notes_text.insert('1.0', lease.notes)
            notes_text.configure(state='disabled')
            notes_text.pack(fill=tk.X, pady=5)

        # Close button
        ttk.Button(
            frame,
            text="Close",
            command=dialog.destroy
        ).pack(pady=20)

    def _open_file(self):
        """Open a data file."""
        filepath = filedialog.askopenfilename(
            title="Open Lease Data",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            try:
                self._load_data_from_file(filepath)
            except Exception as e:
                messagebox.showerror("Error", f"Could not load file:\n{e}")

    def _save_file(self):
        """Save data to a file."""
        filepath = filedialog.asksaveasfilename(
            title="Save Lease Data",
            defaultextension=".json",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            try:
                data = [lease.to_dict() for lease in self.leases]
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                self._update_status(f"Saved {len(self.leases)} leases to {Path(filepath).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not save file:\n{e}")

    def _export_csv(self):
        """Export filtered data to CSV."""
        filepath = filedialog.asksaveasfilename(
            title="Export to CSV",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        if filepath:
            try:
                self.lease_table.export_to_csv(filepath)
                count = len(self.lease_table.filtered_leases)
                self._update_status(f"Exported {count} leases to {Path(filepath).name}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export file:\n{e}")

    def _select_all(self):
        """Select all visible leases."""
        self.lease_table.select_all()

    def _clear_selection(self):
        """Clear the current selection."""
        self.lease_table.clear_selection()

    def _show_all_commodities(self):
        """Show all commodity types in the legend."""
        self.legend.set_selected_commodities(set(get_all_commodities()))
        self.selected_commodities = set(get_all_commodities())
        self._apply_filters()

    def _reset_filters(self):
        """Reset all filters to defaults."""
        self.filter_panel.clear_all()
        self._show_all_commodities()

    def _update_status(self, text: str):
        """Update the status bar text."""
        self.status_text.configure(text=text)

    def _show_about(self):
        """Show the about dialog."""
        messagebox.showinfo(
            "About Wyoming Claim Research",
            "Wyoming Claim Research\n"
            "Version 1.0\n\n"
            "A tool for researching and visualizing\n"
            "Wyoming state mineral leases.\n\n"
            "Features:\n"
            "- Commodity-based color coding\n"
            "- Advanced filtering\n"
            "- Data import/export\n"
        )


def main():
    """Main entry point for the application."""
    app = WyomingClaimApp()
    app.mainloop()


if __name__ == '__main__':
    main()
