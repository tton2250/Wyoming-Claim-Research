"""Filter panel widget for Wyoming Claim Research GUI."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Set
from datetime import date, datetime

from models.lease import LeaseStatus, WYOMING_COUNTIES
from models.commodity import CommodityType, get_all_commodities


class FilterPanel(ttk.LabelFrame):
    """
    A panel with various filter controls for lease data.

    Features:
    - Status filter checkboxes
    - County dropdown
    - Acreage range sliders
    - Date range pickers
    - Text search
    - Clear all button
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_filter_change: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """
        Initialize the filter panel.

        Args:
            parent: Parent widget
            on_filter_change: Callback when any filter changes
            **kwargs: Additional LabelFrame arguments
        """
        super().__init__(parent, text="Filters", **kwargs)

        self.on_filter_change = on_filter_change
        self.status_vars: dict = {}
        self._debounce_id = None

        self._setup_ui()

    def _setup_ui(self):
        """Set up the filter panel UI."""
        # Main container with padding
        container = ttk.Frame(self)
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Row 1: Search box
        search_frame = ttk.Frame(container)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self._on_filter_changed_debounced)
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        clear_search_btn = ttk.Button(
            search_frame,
            text="X",
            width=3,
            command=lambda: self.search_var.set('')
        )
        clear_search_btn.pack(side=tk.LEFT)

        # Row 2: Status filters
        status_frame = ttk.LabelFrame(container, text="Status")
        status_frame.pack(fill=tk.X, pady=5)

        status_inner = ttk.Frame(status_frame)
        status_inner.pack(fill=tk.X, padx=5, pady=5)

        # Create checkboxes for main statuses (2 columns)
        main_statuses = [
            LeaseStatus.ACTIVE,
            LeaseStatus.PRODUCING,
            LeaseStatus.HELD_BY_PRODUCTION,
            LeaseStatus.PENDING,
            LeaseStatus.EXPIRED,
            LeaseStatus.TERMINATED,
        ]

        for i, status in enumerate(main_statuses):
            var = tk.BooleanVar(value=True)
            self.status_vars[status] = var
            cb = ttk.Checkbutton(
                status_inner,
                text=status.value,
                variable=var,
                command=self._on_filter_changed
            )
            row = i // 2
            col = i % 2
            cb.grid(row=row, column=col, sticky=tk.W, padx=5)

        # Row 3: County filter
        county_frame = ttk.Frame(container)
        county_frame.pack(fill=tk.X, pady=5)

        ttk.Label(county_frame, text="County:").pack(side=tk.LEFT)
        self.county_var = tk.StringVar(value="All Counties")
        county_values = ["All Counties"] + sorted(WYOMING_COUNTIES)
        self.county_combo = ttk.Combobox(
            county_frame,
            textvariable=self.county_var,
            values=county_values,
            state='readonly',
            width=20
        )
        self.county_combo.pack(side=tk.LEFT, padx=5)
        self.county_combo.bind('<<ComboboxSelected>>', self._on_filter_changed)

        # Row 4: Acreage range
        acres_frame = ttk.LabelFrame(container, text="Acreage Range")
        acres_frame.pack(fill=tk.X, pady=5)

        acres_inner = ttk.Frame(acres_frame)
        acres_inner.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(acres_inner, text="Min:").pack(side=tk.LEFT)
        self.min_acres_var = tk.StringVar()
        self.min_acres_var.trace_add('write', self._on_filter_changed_debounced)
        min_acres_entry = ttk.Entry(acres_inner, textvariable=self.min_acres_var, width=10)
        min_acres_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(acres_inner, text="Max:").pack(side=tk.LEFT, padx=(10, 0))
        self.max_acres_var = tk.StringVar()
        self.max_acres_var.trace_add('write', self._on_filter_changed_debounced)
        max_acres_entry = ttk.Entry(acres_inner, textvariable=self.max_acres_var, width=10)
        max_acres_entry.pack(side=tk.LEFT, padx=5)

        # Row 5: Date range
        date_frame = ttk.LabelFrame(container, text="Effective Date Range")
        date_frame.pack(fill=tk.X, pady=5)

        date_inner = ttk.Frame(date_frame)
        date_inner.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(date_inner, text="From:").pack(side=tk.LEFT)
        self.date_from_var = tk.StringVar()
        self.date_from_var.trace_add('write', self._on_filter_changed_debounced)
        date_from_entry = ttk.Entry(date_inner, textvariable=self.date_from_var, width=12)
        date_from_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(date_inner, text="To:").pack(side=tk.LEFT, padx=(10, 0))
        self.date_to_var = tk.StringVar()
        self.date_to_var.trace_add('write', self._on_filter_changed_debounced)
        date_to_entry = ttk.Entry(date_inner, textvariable=self.date_to_var, width=12)
        date_to_entry.pack(side=tk.LEFT, padx=5)

        ttk.Label(date_inner, text="(YYYY-MM-DD)", foreground='gray').pack(side=tk.LEFT, padx=5)

        # Row 6: Buttons
        button_frame = ttk.Frame(container)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(
            button_frame,
            text="Clear All Filters",
            command=self.clear_all
        ).pack(side=tk.LEFT)

        ttk.Button(
            button_frame,
            text="Apply",
            command=self._on_filter_changed
        ).pack(side=tk.RIGHT)

    def _on_filter_changed(self, *args):
        """Notify that filters have changed."""
        if self.on_filter_change:
            self.on_filter_change()

    def _on_filter_changed_debounced(self, *args):
        """Debounced filter change notification for text input."""
        if self._debounce_id:
            self.after_cancel(self._debounce_id)
        self._debounce_id = self.after(300, self._on_filter_changed)

    def get_filter_values(self) -> dict:
        """
        Get the current filter values.

        Returns:
            Dictionary with filter values
        """
        # Get selected statuses
        statuses = {status for status, var in self.status_vars.items() if var.get()}

        # Get county
        county = self.county_var.get()
        if county == "All Counties":
            county = None

        # Get acreage range
        min_acres = None
        max_acres = None
        try:
            if self.min_acres_var.get():
                min_acres = float(self.min_acres_var.get())
        except ValueError:
            pass
        try:
            if self.max_acres_var.get():
                max_acres = float(self.max_acres_var.get())
        except ValueError:
            pass

        # Get date range
        date_from = None
        date_to = None
        try:
            if self.date_from_var.get():
                date_from = datetime.strptime(self.date_from_var.get(), '%Y-%m-%d').date()
        except ValueError:
            pass
        try:
            if self.date_to_var.get():
                date_to = datetime.strptime(self.date_to_var.get(), '%Y-%m-%d').date()
        except ValueError:
            pass

        return {
            'search_text': self.search_var.get() or None,
            'statuses': statuses if statuses else None,
            'county': county,
            'min_acres': min_acres,
            'max_acres': max_acres,
            'date_from': date_from,
            'date_to': date_to,
        }

    def clear_all(self):
        """Clear all filter values."""
        self.search_var.set('')
        self.county_var.set("All Counties")
        self.min_acres_var.set('')
        self.max_acres_var.set('')
        self.date_from_var.set('')
        self.date_to_var.set('')

        for var in self.status_vars.values():
            var.set(True)

        self._on_filter_changed()


class QuickFilterBar(ttk.Frame):
    """
    A compact horizontal filter bar for common quick filters.

    Features:
    - Quick commodity buttons
    - Status dropdown
    - Search box
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_filter_change: Optional[Callable[[], None]] = None,
        **kwargs
    ):
        """Initialize the quick filter bar."""
        super().__init__(parent, **kwargs)

        self.on_filter_change = on_filter_change
        self.commodity_vars: dict = {}

        self._setup_ui()

    def _setup_ui(self):
        """Set up the quick filter bar UI."""
        # Search
        ttk.Label(self, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add('write', self._on_change)
        search_entry = ttk.Entry(self, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(0, 10))

        # Separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Quick commodity toggles for main types
        ttk.Label(self, text="Commodities:").pack(side=tk.LEFT, padx=(0, 5))

        main_commodities = [
            CommodityType.OIL,
            CommodityType.GAS,
            CommodityType.OIL_AND_GAS,
            CommodityType.COAL,
            CommodityType.TRONA,
        ]

        for commodity in main_commodities:
            var = tk.BooleanVar(value=True)
            self.commodity_vars[commodity] = var
            cb = ttk.Checkbutton(
                self,
                text=commodity.value,
                variable=var,
                command=self._on_change
            )
            cb.pack(side=tk.LEFT, padx=2)

        # Status dropdown
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        ttk.Label(self, text="Status:").pack(side=tk.LEFT, padx=(0, 5))

        self.status_var = tk.StringVar(value="All")
        status_values = ["All", "Active", "Producing", "Expired", "Pending"]
        status_combo = ttk.Combobox(
            self,
            textvariable=self.status_var,
            values=status_values,
            state='readonly',
            width=12
        )
        status_combo.pack(side=tk.LEFT)
        status_combo.bind('<<ComboboxSelected>>', self._on_change)

    def _on_change(self, *args):
        """Handle filter change."""
        if self.on_filter_change:
            self.on_filter_change()

    def get_selected_commodities(self) -> Set[CommodityType]:
        """Get the selected commodity types."""
        return {c for c, var in self.commodity_vars.items() if var.get()}

    def get_search_text(self) -> Optional[str]:
        """Get the search text."""
        text = self.search_var.get()
        return text if text else None

    def get_status_filter(self) -> Optional[LeaseStatus]:
        """Get the selected status filter."""
        status_str = self.status_var.get()
        if status_str == "All":
            return None
        return LeaseStatus.from_string(status_str)
