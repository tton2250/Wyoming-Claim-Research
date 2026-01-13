#!/usr/bin/env python3
"""
Wyoming Claim Research - Web Interface

A web-based GUI for viewing Wyoming state mineral leases with commodity type legend.
"""

from flask import Flask, render_template_string, jsonify, request
import json
from pathlib import Path
from datetime import date

app = Flask(__name__)

# Commodity colors
COMMODITY_COLORS = {
    "Oil": "#2E4057",
    "Gas": "#FF6B35",
    "Oil & Gas": "#048A81",
    "Coal": "#1C1C1C",
    "Trona": "#9B59B6",
    "Uranium": "#F1C40F",
    "Bentonite": "#A0522D",
    "Sand & Gravel": "#D4AC6E",
    "Limestone": "#BDC3C7",
    "Gypsum": "#ECF0F1",
    "Other Minerals": "#7F8C8D",
    "Geothermal": "#E74C3C",
    "Helium": "#85C1E9",
    "Unknown": "#95A5A6",
}

COMMODITY_TEXT_COLORS = {
    "Oil": "#FFFFFF",
    "Gas": "#FFFFFF",
    "Oil & Gas": "#FFFFFF",
    "Coal": "#FFFFFF",
    "Trona": "#FFFFFF",
    "Uranium": "#000000",
    "Bentonite": "#FFFFFF",
    "Sand & Gravel": "#000000",
    "Limestone": "#000000",
    "Gypsum": "#000000",
    "Other Minerals": "#FFFFFF",
    "Geothermal": "#FFFFFF",
    "Helium": "#000000",
    "Unknown": "#FFFFFF",
}

# Load sample data
def load_leases():
    data_path = Path(__file__).parent / 'data' / 'sample_leases.json'
    if data_path.exists():
        with open(data_path) as f:
            return json.load(f)
    return []

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wyoming Claim Research</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: #f5f5f5;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #2E4057 0%, #048A81 100%);
            color: white;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        .header p {
            opacity: 0.8;
            font-size: 14px;
        }
        .container {
            display: flex;
            gap: 20px;
            padding: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        .sidebar {
            width: 280px;
            flex-shrink: 0;
        }
        .main-content {
            flex: 1;
            min-width: 0;
        }
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            padding: 20px;
            margin-bottom: 20px;
        }
        .card h2 {
            font-size: 16px;
            color: #2E4057;
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #eee;
        }

        /* Legend Styles */
        .legend-item {
            display: flex;
            align-items: center;
            padding: 8px;
            margin: 4px 0;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .legend-item:hover {
            background: #f0f0f0;
        }
        .legend-item.disabled {
            opacity: 0.4;
        }
        .legend-checkbox {
            margin-right: 10px;
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        .legend-color {
            width: 24px;
            height: 24px;
            border-radius: 4px;
            margin-right: 10px;
            border: 1px solid rgba(0,0,0,0.1);
        }
        .legend-name {
            flex: 1;
            font-size: 14px;
        }
        .legend-count {
            color: #888;
            font-size: 12px;
        }
        .legend-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }
        .legend-buttons button {
            flex: 1;
            padding: 8px;
            border: 1px solid #ddd;
            background: #f8f8f8;
            border-radius: 4px;
            cursor: pointer;
            font-size: 13px;
        }
        .legend-buttons button:hover {
            background: #eee;
        }

        /* Filter Styles */
        .filter-group {
            margin-bottom: 15px;
        }
        .filter-group label {
            display: block;
            font-size: 13px;
            color: #666;
            margin-bottom: 5px;
        }
        .filter-group input, .filter-group select {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
        }
        .filter-group input:focus, .filter-group select:focus {
            outline: none;
            border-color: #048A81;
        }

        /* Table Styles */
        .table-container {
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }
        th {
            background: #f8f8f8;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            color: #2E4057;
            border-bottom: 2px solid #eee;
            cursor: pointer;
            white-space: nowrap;
        }
        th:hover {
            background: #f0f0f0;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        tr:hover {
            background: #f8f8f8;
        }
        .commodity-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 500;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
        }
        .status-Active { background: #d4edda; color: #155724; }
        .status-Producing { background: #c3e6cb; color: #155724; }
        .status-Pending { background: #fff3cd; color: #856404; }
        .status-Expired { background: #e2e3e5; color: #383d41; }
        .status-Terminated { background: #f8d7da; color: #721c24; }

        /* Stats */
        .stats {
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }
        .stat {
            flex: 1;
            background: #f8f8f8;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 28px;
            font-weight: 700;
            color: #2E4057;
        }
        .stat-label {
            font-size: 12px;
            color: #888;
            margin-top: 5px;
        }

        /* Compact legend in header */
        .compact-legend {
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-top: 15px;
        }
        .compact-legend-item {
            padding: 3px 8px;
            border-radius: 3px;
            font-size: 11px;
            font-weight: 500;
        }

        @media (max-width: 900px) {
            .container {
                flex-direction: column;
            }
            .sidebar {
                width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Wyoming Claim Research</h1>
        <p>State Mineral Lease Viewer with Commodity Type Legend</p>
        <div class="compact-legend" id="compactLegend"></div>
    </div>

    <div class="container">
        <div class="sidebar">
            <div class="card">
                <h2>Commodity Legend</h2>
                <div class="legend-buttons">
                    <button onclick="selectAllCommodities()">All</button>
                    <button onclick="selectNoneCommodities()">None</button>
                </div>
                <div id="legend"></div>
            </div>

            <div class="card">
                <h2>Filters</h2>
                <div class="filter-group">
                    <label>Search</label>
                    <input type="text" id="searchInput" placeholder="Lease #, Lessee, County..." oninput="applyFilters()">
                </div>
                <div class="filter-group">
                    <label>Status</label>
                    <select id="statusFilter" onchange="applyFilters()">
                        <option value="">All Statuses</option>
                        <option value="Active">Active</option>
                        <option value="Producing">Producing</option>
                        <option value="Held by Production">Held by Production</option>
                        <option value="Pending">Pending</option>
                        <option value="Expired">Expired</option>
                        <option value="Terminated">Terminated</option>
                    </select>
                </div>
                <div class="filter-group">
                    <label>County</label>
                    <select id="countyFilter" onchange="applyFilters()">
                        <option value="">All Counties</option>
                    </select>
                </div>
            </div>
        </div>

        <div class="main-content">
            <div class="card">
                <div class="stats">
                    <div class="stat">
                        <div class="stat-value" id="totalLeases">0</div>
                        <div class="stat-label">Total Leases</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="totalAcres">0</div>
                        <div class="stat-label">Total Acres</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value" id="activeLeases">0</div>
                        <div class="stat-label">Active Leases</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>State Leases</h2>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th onclick="sortTable('lease_number')">Lease #</th>
                                <th onclick="sortTable('commodity_type')">Commodity</th>
                                <th onclick="sortTable('status')">Status</th>
                                <th onclick="sortTable('county')">County</th>
                                <th onclick="sortTable('acres')">Acres</th>
                                <th onclick="sortTable('lessee_name')">Lessee</th>
                                <th onclick="sortTable('effective_date')">Effective</th>
                                <th onclick="sortTable('expiration_date')">Expiration</th>
                            </tr>
                        </thead>
                        <tbody id="leaseTable"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <script>
        const commodityColors = {{ commodity_colors | tojson }};
        const commodityTextColors = {{ commodity_text_colors | tojson }};
        let leases = {{ leases | tojson }};
        let selectedCommodities = new Set(Object.keys(commodityColors));
        let sortColumn = 'lease_number';
        let sortAsc = true;

        function init() {
            renderLegend();
            renderCompactLegend();
            populateCountyFilter();
            applyFilters();
        }

        function renderLegend() {
            const container = document.getElementById('legend');
            container.innerHTML = '';

            // Get counts
            const counts = {};
            leases.forEach(l => {
                counts[l.commodity_type] = (counts[l.commodity_type] || 0) + 1;
            });

            Object.keys(commodityColors).forEach(commodity => {
                const div = document.createElement('div');
                div.className = 'legend-item' + (selectedCommodities.has(commodity) ? '' : ' disabled');
                div.innerHTML = `
                    <input type="checkbox" class="legend-checkbox"
                           ${selectedCommodities.has(commodity) ? 'checked' : ''}
                           onchange="toggleCommodity('${commodity}')">
                    <div class="legend-color" style="background: ${commodityColors[commodity]}"></div>
                    <span class="legend-name">${commodity}</span>
                    <span class="legend-count">(${counts[commodity] || 0})</span>
                `;
                div.onclick = (e) => {
                    if (e.target.type !== 'checkbox') {
                        toggleCommodity(commodity);
                    }
                };
                container.appendChild(div);
            });
        }

        function renderCompactLegend() {
            const container = document.getElementById('compactLegend');
            container.innerHTML = '';
            Object.keys(commodityColors).forEach(commodity => {
                const span = document.createElement('span');
                span.className = 'compact-legend-item';
                span.style.background = commodityColors[commodity];
                span.style.color = commodityTextColors[commodity];
                span.textContent = commodity;
                container.appendChild(span);
            });
        }

        function toggleCommodity(commodity) {
            if (selectedCommodities.has(commodity)) {
                selectedCommodities.delete(commodity);
            } else {
                selectedCommodities.add(commodity);
            }
            renderLegend();
            applyFilters();
        }

        function selectAllCommodities() {
            selectedCommodities = new Set(Object.keys(commodityColors));
            renderLegend();
            applyFilters();
        }

        function selectNoneCommodities() {
            selectedCommodities.clear();
            renderLegend();
            applyFilters();
        }

        function populateCountyFilter() {
            const counties = [...new Set(leases.map(l => l.county))].sort();
            const select = document.getElementById('countyFilter');
            counties.forEach(county => {
                const opt = document.createElement('option');
                opt.value = county;
                opt.textContent = county;
                select.appendChild(opt);
            });
        }

        function applyFilters() {
            const search = document.getElementById('searchInput').value.toLowerCase();
            const status = document.getElementById('statusFilter').value;
            const county = document.getElementById('countyFilter').value;

            let filtered = leases.filter(l => {
                if (!selectedCommodities.has(l.commodity_type)) return false;
                if (status && l.status !== status) return false;
                if (county && l.county !== county) return false;
                if (search) {
                    const searchable = `${l.lease_number} ${l.lessee_name} ${l.county}`.toLowerCase();
                    if (!searchable.includes(search)) return false;
                }
                return true;
            });

            // Sort
            filtered.sort((a, b) => {
                let aVal = a[sortColumn] || '';
                let bVal = b[sortColumn] || '';
                if (sortColumn === 'acres') {
                    aVal = parseFloat(aVal) || 0;
                    bVal = parseFloat(bVal) || 0;
                }
                if (aVal < bVal) return sortAsc ? -1 : 1;
                if (aVal > bVal) return sortAsc ? 1 : -1;
                return 0;
            });

            renderTable(filtered);
            updateStats(filtered);
        }

        function sortTable(column) {
            if (sortColumn === column) {
                sortAsc = !sortAsc;
            } else {
                sortColumn = column;
                sortAsc = true;
            }
            applyFilters();
        }

        function renderTable(data) {
            const tbody = document.getElementById('leaseTable');
            tbody.innerHTML = '';

            data.forEach(lease => {
                const tr = document.createElement('tr');
                const bgColor = commodityColors[lease.commodity_type] || '#95A5A6';
                const textColor = commodityTextColors[lease.commodity_type] || '#FFFFFF';

                tr.innerHTML = `
                    <td><strong>${lease.lease_number}</strong></td>
                    <td><span class="commodity-badge" style="background: ${bgColor}; color: ${textColor}">${lease.commodity_type}</span></td>
                    <td><span class="status-badge status-${lease.status.replace(/ /g, '')}">${lease.status}</span></td>
                    <td>${lease.county}</td>
                    <td>${lease.acres.toLocaleString()}</td>
                    <td>${lease.lessee_name}</td>
                    <td>${lease.effective_date || '-'}</td>
                    <td>${lease.expiration_date || '-'}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        function updateStats(filtered) {
            document.getElementById('totalLeases').textContent = filtered.length;
            const totalAcres = filtered.reduce((sum, l) => sum + (l.acres || 0), 0);
            document.getElementById('totalAcres').textContent = totalAcres.toLocaleString();
            const active = filtered.filter(l => ['Active', 'Producing', 'Held by Production'].includes(l.status)).length;
            document.getElementById('activeLeases').textContent = active;
        }

        init();
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    leases = load_leases()
    return render_template_string(
        HTML_TEMPLATE,
        leases=leases,
        commodity_colors=COMMODITY_COLORS,
        commodity_text_colors=COMMODITY_TEXT_COLORS
    )

@app.route('/api/leases')
def api_leases():
    return jsonify(load_leases())

if __name__ == '__main__':
    print("Starting Wyoming Claim Research Web Interface...")
    print("Open http://localhost:5000 in your browser")
    app.run(host='0.0.0.0', port=5000, debug=False)
