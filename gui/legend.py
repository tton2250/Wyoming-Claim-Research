"""Commodity type legend widget for the Wyoming Claim Research GUI."""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Optional, Set

from models.commodity import (
    CommodityType,
    COMMODITY_COLORS,
    COMMODITY_TEXT_COLORS,
    get_all_commodities,
)


class CommodityLegend(ttk.LabelFrame):
    """
    A legend widget displaying commodity types with their associated colors.

    Features:
    - Color-coded boxes for each commodity type
    - Click to toggle visibility/filter
    - Counts of leases per commodity type
    - Collapsible sections
    """

    def __init__(
        self,
        parent: tk.Widget,
        on_filter_change: Optional[Callable[[Set[CommodityType]], None]] = None,
        **kwargs
    ):
        """
        Initialize the commodity legend.

        Args:
            parent: Parent widget
            on_filter_change: Callback when filter selection changes
            **kwargs: Additional arguments passed to LabelFrame
        """
        super().__init__(parent, text="Commodity Legend", **kwargs)

        self.on_filter_change = on_filter_change
        self.commodity_counts: Dict[CommodityType, int] = {}
        self.selected_commodities: Set[CommodityType] = set(get_all_commodities())
        self.legend_items: Dict[CommodityType, Dict[str, tk.Widget]] = {}

        self._setup_ui()

    def _setup_ui(self):
        """Set up the legend user interface."""
        # Header with select all/none buttons
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=5, pady=(5, 2))

        ttk.Button(
            header_frame,
            text="All",
            width=5,
            command=self._select_all
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            header_frame,
            text="None",
            width=5,
            command=self._select_none
        ).pack(side=tk.LEFT, padx=2)

        # Separator
        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=5, pady=5)

        # Scrollable frame for legend items
        self.canvas = tk.Canvas(self, highlightthickness=0, width=200)
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.canvas.yview)

        self.scrollable_frame = ttk.Frame(self.canvas)
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

        # Create legend items for each commodity
        self._create_legend_items()

    def _create_legend_items(self):
        """Create legend entry for each commodity type."""
        for commodity in get_all_commodities():
            self._create_legend_item(commodity)

    def _create_legend_item(self, commodity: CommodityType):
        """Create a single legend item for a commodity type."""
        bg_color = COMMODITY_COLORS.get(commodity, "#95A5A6")
        text_color = COMMODITY_TEXT_COLORS.get(commodity, "#FFFFFF")

        # Container frame for the legend item
        item_frame = ttk.Frame(self.scrollable_frame)
        item_frame.pack(fill=tk.X, pady=2)

        # Checkbox for filtering
        var = tk.BooleanVar(value=True)
        checkbox = ttk.Checkbutton(
            item_frame,
            variable=var,
            command=lambda c=commodity, v=var: self._on_commodity_toggle(c, v)
        )
        checkbox.pack(side=tk.LEFT)

        # Color box
        color_box = tk.Canvas(
            item_frame,
            width=20,
            height=20,
            bg=bg_color,
            highlightthickness=1,
            highlightbackground="#333333"
        )
        color_box.pack(side=tk.LEFT, padx=(2, 5))

        # Commodity name label
        name_label = ttk.Label(
            item_frame,
            text=commodity.value,
            width=15,
            anchor=tk.W
        )
        name_label.pack(side=tk.LEFT)

        # Count label
        count_label = ttk.Label(
            item_frame,
            text="(0)",
            width=8,
            anchor=tk.E,
            foreground="#666666"
        )
        count_label.pack(side=tk.RIGHT, padx=5)

        # Store references for updates
        self.legend_items[commodity] = {
            'frame': item_frame,
            'checkbox': checkbox,
            'var': var,
            'color_box': color_box,
            'name_label': name_label,
            'count_label': count_label,
        }

        # Bind click on entire row to toggle
        for widget in [color_box, name_label]:
            widget.bind("<Button-1>", lambda e, c=commodity, v=var: self._toggle_checkbox(c, v))

    def _toggle_checkbox(self, commodity: CommodityType, var: tk.BooleanVar):
        """Toggle the checkbox for a commodity when clicking on the row."""
        var.set(not var.get())
        self._on_commodity_toggle(commodity, var)

    def _on_commodity_toggle(self, commodity: CommodityType, var: tk.BooleanVar):
        """Handle commodity filter toggle."""
        if var.get():
            self.selected_commodities.add(commodity)
        else:
            self.selected_commodities.discard(commodity)

        self._update_visual_state()
        self._notify_filter_change()

    def _update_visual_state(self):
        """Update visual appearance based on selection state."""
        for commodity, widgets in self.legend_items.items():
            if commodity in self.selected_commodities:
                widgets['name_label'].configure(foreground='')
                widgets['color_box'].configure(state=tk.NORMAL)
            else:
                widgets['name_label'].configure(foreground='#999999')
                # Dim the color box for deselected items
                widgets['color_box'].configure(state=tk.DISABLED)

    def _select_all(self):
        """Select all commodity types."""
        self.selected_commodities = set(get_all_commodities())
        for commodity, widgets in self.legend_items.items():
            widgets['var'].set(True)
        self._update_visual_state()
        self._notify_filter_change()

    def _select_none(self):
        """Deselect all commodity types."""
        self.selected_commodities.clear()
        for commodity, widgets in self.legend_items.items():
            widgets['var'].set(False)
        self._update_visual_state()
        self._notify_filter_change()

    def _notify_filter_change(self):
        """Notify callback of filter change."""
        if self.on_filter_change:
            self.on_filter_change(self.selected_commodities.copy())

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def update_counts(self, counts: Dict[CommodityType, int]):
        """
        Update the lease counts for each commodity type.

        Args:
            counts: Dictionary mapping commodity types to counts
        """
        self.commodity_counts = counts
        for commodity, widgets in self.legend_items.items():
            count = counts.get(commodity, 0)
            widgets['count_label'].configure(text=f"({count})")

    def get_selected_commodities(self) -> Set[CommodityType]:
        """Return the set of currently selected commodity types."""
        return self.selected_commodities.copy()

    def set_selected_commodities(self, commodities: Set[CommodityType]):
        """Set which commodity types are selected."""
        self.selected_commodities = commodities.copy()
        for commodity, widgets in self.legend_items.items():
            widgets['var'].set(commodity in commodities)
        self._update_visual_state()


class CompactLegend(ttk.Frame):
    """
    A compact, horizontal legend for display in toolbars or status bars.

    Shows color swatches with commodity abbreviations.
    """

    ABBREVIATIONS = {
        CommodityType.OIL: "Oil",
        CommodityType.GAS: "Gas",
        CommodityType.OIL_AND_GAS: "O&G",
        CommodityType.COAL: "Coal",
        CommodityType.TRONA: "Trona",
        CommodityType.URANIUM: "U",
        CommodityType.BENTONITE: "Bent",
        CommodityType.SAND_GRAVEL: "S&G",
        CommodityType.LIMESTONE: "Lime",
        CommodityType.GYPSUM: "Gyp",
        CommodityType.OTHER_MINERALS: "Other",
        CommodityType.GEOTHERMAL: "Geo",
        CommodityType.HELIUM: "He",
        CommodityType.UNKNOWN: "?",
    }

    def __init__(self, parent: tk.Widget, **kwargs):
        """Initialize the compact legend."""
        super().__init__(parent, **kwargs)
        self._setup_ui()

    def _setup_ui(self):
        """Set up the compact legend UI."""
        for commodity in get_all_commodities():
            bg_color = COMMODITY_COLORS.get(commodity, "#95A5A6")
            text_color = COMMODITY_TEXT_COLORS.get(commodity, "#FFFFFF")
            abbrev = self.ABBREVIATIONS.get(commodity, commodity.value[:3])

            # Create a small colored label
            label = tk.Label(
                self,
                text=abbrev,
                bg=bg_color,
                fg=text_color,
                padx=4,
                pady=1,
                font=('TkDefaultFont', 8),
                relief=tk.RAISED,
                borderwidth=1
            )
            label.pack(side=tk.LEFT, padx=1)

            # Add tooltip with full name
            self._create_tooltip(label, commodity.value)

    def _create_tooltip(self, widget: tk.Widget, text: str):
        """Create a simple tooltip for a widget."""
        def show_tooltip(event):
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")

            label = tk.Label(
                tooltip,
                text=text,
                background="#ffffe0",
                relief=tk.SOLID,
                borderwidth=1,
                padx=5,
                pady=2
            )
            label.pack()

            widget._tooltip = tooltip

        def hide_tooltip(event):
            if hasattr(widget, '_tooltip') and widget._tooltip:
                widget._tooltip.destroy()
                widget._tooltip = None

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
