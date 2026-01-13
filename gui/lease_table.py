"""Lease table view widget for displaying Wyoming state leases."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional, Dict, Any
from datetime import date

from models.lease import Lease, LeaseStatus, STATUS_COLORS
from models.commodity import CommodityType, COMMODITY_COLORS


class LeaseTableView(ttk.Frame):
    """
    A table view for displaying lease data with sorting and selection.

    Features:
    - Sortable columns
    - Color-coded commodity and status
    - Row selection
    - Double-click for details
    - Export functionality
    """

    COLUMNS = [
        ('lease_number', 'Lease #', 100),
        ('commodity', 'Commodity', 100),
        ('status', 'Status', 90),
        ('county', 'County', 90),
        ('acres', 'Acres', 70),
        ('lessee', 'Lessee', 150),
        ('effective', 'Effective', 90),
        ('expiration', 'Expiration', 90),
        ('location', 'Location', 120),
    ]

    def __init__(
        self,
        parent: tk.Widget,
        on_selection_change: Optional[Callable[[List[Lease]], None]] = None,
        on_double_click: Optional[Callable[[Lease], None]] = None,
        **kwargs
    ):
        """
        Initialize the lease table view.

        Args:
            parent: Parent widget
            on_selection_change: Callback when selection changes
            on_double_click: Callback when row is double-clicked
            **kwargs: Additional frame arguments
        """
        super().__init__(parent, **kwargs)

        self.on_selection_change = on_selection_change
        self.on_double_click = on_double_click
        self.leases: List[Lease] = []
        self.filtered_leases: List[Lease] = []
        self.sort_column: str = 'lease_number'
        self.sort_reverse: bool = False
        self.lease_map: Dict[str, Lease] = {}  # Map tree item id to lease

        self._setup_ui()
        self._setup_tags()

    def _setup_ui(self):
        """Set up the table user interface."""
        # Create treeview with scrollbars
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # Vertical scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Horizontal scrollbar
        hsb = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # Create treeview
        columns = [col[0] for col in self.COLUMNS]
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            selectmode='extended',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        vsb.configure(command=self.tree.yview)
        hsb.configure(command=self.tree.xview)

        # Configure columns
        for col_id, col_name, col_width in self.COLUMNS:
            self.tree.heading(
                col_id,
                text=col_name,
                command=lambda c=col_id: self._sort_by_column(c)
            )
            self.tree.column(col_id, width=col_width, minwidth=50)

        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind events
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._on_double_click)

        # Status bar
        self.status_frame = ttk.Frame(self)
        self.status_frame.pack(fill=tk.X, pady=2)

        self.status_label = ttk.Label(
            self.status_frame,
            text="0 leases"
        )
        self.status_label.pack(side=tk.LEFT, padx=5)

        self.selection_label = ttk.Label(
            self.status_frame,
            text=""
        )
        self.selection_label.pack(side=tk.RIGHT, padx=5)

    def _setup_tags(self):
        """Set up row tags for color coding."""
        # Create tags for each commodity type
        for commodity in CommodityType:
            color = COMMODITY_COLORS.get(commodity, "#FFFFFF")
            # Use lighter version for row background
            light_color = self._lighten_color(color, 0.85)
            self.tree.tag_configure(
                f'commodity_{commodity.name}',
                background=light_color
            )

        # Create tags for status
        for status in LeaseStatus:
            color = STATUS_COLORS.get(status, "#FFFFFF")
            light_color = self._lighten_color(color, 0.9)
            self.tree.tag_configure(
                f'status_{status.name}',
                background=light_color
            )

        # Special tag for expiring soon
        self.tree.tag_configure('expiring_soon', foreground='#E74C3C')

        # Alternating row colors
        self.tree.tag_configure('oddrow', background='#F8F8F8')
        self.tree.tag_configure('evenrow', background='#FFFFFF')

    def _lighten_color(self, hex_color: str, factor: float) -> str:
        """Lighten a hex color by blending with white."""
        # Remove # if present
        hex_color = hex_color.lstrip('#')

        # Parse RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)

        # Blend with white
        r = int(r + (255 - r) * factor)
        g = int(g + (255 - g) * factor)
        b = int(b + (255 - b) * factor)

        return f'#{r:02x}{g:02x}{b:02x}'

    def set_leases(self, leases: List[Lease]):
        """Set the lease data to display."""
        self.leases = leases
        self.filtered_leases = leases.copy()
        self._refresh_display()

    def filter_leases(
        self,
        commodities: Optional[set] = None,
        statuses: Optional[set] = None,
        county: Optional[str] = None,
        search_text: Optional[str] = None,
        min_acres: Optional[float] = None,
        max_acres: Optional[float] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
    ):
        """
        Filter the displayed leases based on criteria.

        Args:
            commodities: Set of CommodityTypes to include (None = all)
            statuses: Set of LeaseStatuses to include (None = all)
            county: County name filter (partial match)
            search_text: General text search across fields
            min_acres: Minimum acreage
            max_acres: Maximum acreage
            date_from: Minimum effective date
            date_to: Maximum effective date
        """
        self.filtered_leases = []

        for lease in self.leases:
            # Commodity filter
            if commodities is not None and lease.commodity_type not in commodities:
                continue

            # Status filter
            if statuses is not None and lease.status not in statuses:
                continue

            # County filter
            if county and county.lower() not in lease.county.lower():
                continue

            # Text search
            if search_text:
                search_lower = search_text.lower()
                searchable = f"{lease.lease_number} {lease.lessee_name} {lease.county} {lease.legal_description}".lower()
                if search_lower not in searchable:
                    continue

            # Acreage filter
            if min_acres is not None and lease.acres < min_acres:
                continue
            if max_acres is not None and lease.acres > max_acres:
                continue

            # Date filter
            if date_from and lease.effective_date and lease.effective_date < date_from:
                continue
            if date_to and lease.effective_date and lease.effective_date > date_to:
                continue

            self.filtered_leases.append(lease)

        self._refresh_display()

    def _refresh_display(self):
        """Refresh the treeview display with current filtered data."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.lease_map.clear()

        # Sort data
        sorted_leases = self._sort_leases(self.filtered_leases)

        # Insert rows
        for i, lease in enumerate(sorted_leases):
            values = self._lease_to_values(lease)
            tags = self._get_tags_for_lease(lease, i)

            item_id = self.tree.insert('', tk.END, values=values, tags=tags)
            self.lease_map[item_id] = lease

        # Update status
        total = len(self.leases)
        filtered = len(self.filtered_leases)
        if total == filtered:
            self.status_label.configure(text=f"{total} leases")
        else:
            self.status_label.configure(text=f"Showing {filtered} of {total} leases")

    def _lease_to_values(self, lease: Lease) -> tuple:
        """Convert a lease to treeview values."""
        return (
            lease.lease_number,
            lease.commodity_type.value,
            lease.status.value,
            lease.county,
            f"{lease.acres:,.1f}",
            lease.lessee_name,
            lease.effective_date.strftime('%Y-%m-%d') if lease.effective_date else '',
            lease.expiration_date.strftime('%Y-%m-%d') if lease.expiration_date else '',
            lease.location_str,
        )

    def _get_tags_for_lease(self, lease: Lease, index: int) -> tuple:
        """Get the tags to apply to a lease row."""
        tags = []

        # Commodity color
        tags.append(f'commodity_{lease.commodity_type.name}')

        # Expiring soon highlight
        if lease.is_expiring_soon:
            tags.append('expiring_soon')

        return tuple(tags)

    def _sort_leases(self, leases: List[Lease]) -> List[Lease]:
        """Sort leases by the current sort column."""
        def get_sort_key(lease: Lease):
            if self.sort_column == 'lease_number':
                return lease.lease_number
            elif self.sort_column == 'commodity':
                return lease.commodity_type.value
            elif self.sort_column == 'status':
                return lease.status.value
            elif self.sort_column == 'county':
                return lease.county
            elif self.sort_column == 'acres':
                return lease.acres
            elif self.sort_column == 'lessee':
                return lease.lessee_name
            elif self.sort_column == 'effective':
                return lease.effective_date or date.min
            elif self.sort_column == 'expiration':
                return lease.expiration_date or date.min
            elif self.sort_column == 'location':
                return lease.location_str
            return ''

        return sorted(leases, key=get_sort_key, reverse=self.sort_reverse)

    def _sort_by_column(self, column: str):
        """Sort by the specified column."""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False

        self._refresh_display()

        # Update column headers to show sort indicator
        for col_id, col_name, _ in self.COLUMNS:
            indicator = ''
            if col_id == self.sort_column:
                indicator = ' ▼' if self.sort_reverse else ' ▲'
            self.tree.heading(col_id, text=col_name + indicator)

    def _on_select(self, event):
        """Handle selection change."""
        selected_items = self.tree.selection()
        selected_leases = [self.lease_map[item] for item in selected_items if item in self.lease_map]

        # Update selection label
        count = len(selected_leases)
        if count == 0:
            self.selection_label.configure(text="")
        elif count == 1:
            self.selection_label.configure(text=f"1 lease selected")
        else:
            self.selection_label.configure(text=f"{count} leases selected")

        if self.on_selection_change:
            self.on_selection_change(selected_leases)

    def _on_double_click(self, event):
        """Handle double-click on a row."""
        item = self.tree.identify_row(event.y)
        if item and item in self.lease_map:
            lease = self.lease_map[item]
            if self.on_double_click:
                self.on_double_click(lease)

    def get_selected_leases(self) -> List[Lease]:
        """Get the currently selected leases."""
        selected_items = self.tree.selection()
        return [self.lease_map[item] for item in selected_items if item in self.lease_map]

    def select_all(self):
        """Select all visible rows."""
        self.tree.selection_set(self.tree.get_children())

    def clear_selection(self):
        """Clear the current selection."""
        self.tree.selection_remove(self.tree.selection())

    def export_to_csv(self, filepath: str):
        """Export the current filtered view to CSV."""
        import csv

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header row
            writer.writerow([col[1] for col in self.COLUMNS])

            # Data rows
            for lease in self.filtered_leases:
                writer.writerow(self._lease_to_values(lease))

    def get_commodity_counts(self) -> Dict[CommodityType, int]:
        """Get counts of leases by commodity type in the filtered view."""
        counts: Dict[CommodityType, int] = {}
        for lease in self.filtered_leases:
            counts[lease.commodity_type] = counts.get(lease.commodity_type, 0) + 1
        return counts
