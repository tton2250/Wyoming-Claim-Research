# Wyoming Claim Research

A GUI application for researching and visualizing Wyoming state mineral leases with commodity type categorization.

## Features

- **State Lease Display**: View Wyoming state mineral leases in a sortable table
- **Commodity Type Legend**: Color-coded legend for different commodity types (Oil, Gas, Coal, Minerals, etc.)
- **Filtering**: Filter leases by commodity type, status, county, and date range
- **Data Export**: Export filtered data to CSV format
- **Interactive Map View**: Visualize lease locations (when coordinates available)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

## Commodity Types

The application supports the following commodity types:
- **Oil** - Petroleum/crude oil leases
- **Gas** - Natural gas leases
- **Coal** - Coal mining leases
- **Trona** - Trona (sodium carbonate) mining leases
- **Uranium** - Uranium mining leases
- **Bentonite** - Bentonite clay mining leases
- **Other Minerals** - Other mineral extraction leases

## Project Structure

```
Wyoming-Claim-Research/
├── main.py              # Application entry point
├── models/
│   ├── __init__.py
│   ├── lease.py         # Lease data model
│   └── commodity.py     # Commodity type definitions
├── gui/
│   ├── __init__.py
│   ├── app.py           # Main application window
│   ├── legend.py        # Commodity type legend widget
│   ├── lease_table.py   # Lease table view
│   └── filters.py       # Filter panel
├── data/
│   └── sample_leases.json  # Sample lease data
└── requirements.txt
```

## License

MIT License
