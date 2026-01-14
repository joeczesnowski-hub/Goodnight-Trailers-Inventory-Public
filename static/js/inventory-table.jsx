const InventoryTable = ({ category, userPermissions }) => {
  // Get current view from URL
  const urlParams = new URLSearchParams(window.location.search);
  const currentView = urlParams.get('view') || 'unsold';
  const [items, setItems] = React.useState([]);
  const [filteredItems, setFilteredItems] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [selectedIds, setSelectedIds] = React.useState(new Set());
  const [showMultiEditModal, setShowMultiEditModal] = React.useState(false);
  const [summary, setSummary] = React.useState(null);
  const [sortBy, setSortBy] = React.useState(null);
  const [sortOrder, setSortOrder] = React.useState('desc'); // 'asc' or 'desc'
  
  // Filter states
  const [searchText, setSearchText] = React.useState('');
  const [makeFilter, setMakeFilter] = React.useState('');
  const [conditionFilter, setConditionFilter] = React.useState('');
  const [soldFilter, setSoldFilter] = React.useState('');
  const [minPrice, setMinPrice] = React.useState('');
  const [maxPrice, setMaxPrice] = React.useState('');
  const [minYear, setMinYear] = React.useState('');
  const [maxYear, setMaxYear] = React.useState('');

  // Color map for makes
  const [colorMap, setColorMap] = React.useState({});

  // Fetch inventory data
  React.useEffect(() => {
    fetchInventory();
    if (userPermissions.hasSummary) {
      fetchSummary();
    }
  }, [category]);

  // Apply filters whenever filter states change
  React.useEffect(() => {
    applyFilters();
   }, [items, searchText, makeFilter, conditionFilter, soldFilter, minPrice, maxPrice, minYear, maxYear, sortBy, sortOrder]);

  // Expose selectedIds to window for export functionality
React.useEffect(() => {
  window.selectedItemIds = selectedIds;
}, [selectedIds]);

  const fetchInventory = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/inventory/${category}`);
      const data = await response.json();
      setItems(data);
      generateColorMap(data);
    } catch (error) {
      console.error('Error fetching inventory:', error);
    } finally {
      setLoading(false);
    }
  };

 // Check if Facebook post is expired (7+ days old)
  const isExpiredPost = (postedDate) => {
    if (!postedDate) return false;
    const posted = new Date(postedDate);
    const now = new Date();
    const daysDiff = Math.floor((now - posted) / (1000 * 60 * 60 * 24));
    return daysDiff >= 7;
  }; 

  const fetchSummary = async () => {
    try {
      const response = await fetch(`/api/inventory/summary/${category}`);
      const data = await response.json();
      setSummary(data);
    } catch (error) {
      console.error('Error fetching summary:', error);
    }
  };

const generateColorMap = (data) => {
const READABLE_COLORS = [
  '#FFFF00',    // Yellow (TOP HAT)
  '#FF6B6B',    // Coral Red
  '#4ECDC4',    // Turquoise
  '#95E1D3',    // Mint
  '#C7CEEA',    // Periwinkle
  '#FFB6C1',    // Light Pink
  '#FFA500',    // Orange
  '#E6E6FA',    // Lavender
  '#9370DB',    // Medium Purple
  '#87CEEB',    // Sky Blue
  '#98FB98',    // Pale Green
  '#87CEFA',    // Light Sky Blue
  '#DDA0DD',    // Plum
  '#B0E0E6',    // Powder Blue
  '#ADD8E6',    // Light Blue
  '#FFA07A',    // Light Salmon
  '#20B2AA',    // Light Sea Green
  '#AFEEEE',    // Pale Turquoise
  '#F08080',    // Light Coral
  '#32CD32',    // Lime Green
  '#FFD700',    // Gold
  '#40E0D0',    // Turquoise Blue
  '#DA70D6',    // Orchid
  '#F0E68C',    // Khaki
  '#FF99CC',    // Rose Pink
  '#99CCFF',    // Light Periwinkle
  '#CCFF99',    // Light Lime
  '#FFCC99',    // Peach
  '#CC99FF',    // Lilac
  '#99FFCC',    // Aquamarine
  '#FFB6B9',    // Pink
  '#BAE1FF',    // Baby Blue
  '#C3F0CA',    // Mint Green
  '#FFE5B4',    // Peach Puff
  '#E0BBE4',    // Mauve
  '#FFDAB9',    // Peach
  '#B0E57C',    // Yellow Green
  '#FFE4E1',    // Misty Rose
  '#D8BFD8',    // Thistle
  '#F5DEB3',    // Wheat
  '#FAFAD2',    // Light Goldenrod
  '#E0FFFF',    // Light Cyan
  '#FFE4B5',    // Moccasin
  '#FFF0F5',    // Lavender Blush
  '#F0FFF0',    // Honeydew
  '#FDF5E6',    // Old Lace
  '#FAF0E6',    // Linen
  '#FFFACD',    // Lemon Chiffon
  '#F5F5DC',    // Beige
  '#FFEFD5'     // Papaya Whip
];

  const makes = [...new Set(data.map(item => item.make).filter(Boolean))].sort();
  const colors = {};
  
  // TOP HAT always gets yellow (matching production)
  if (makes.includes('TOP HAT')) {
    colors['TOP HAT'] = '#FFFF00';
  }
  
  // Assign colors in order, skipping TOP HAT and starting from index 1
  let colorIndex = 1;  // Start at 1 to skip yellow
  makes.forEach(make => {
    if (!colors[make]) {
      colors[make] = READABLE_COLORS[colorIndex % READABLE_COLORS.length];
      colorIndex++;
    }
  });
  
  console.log('Color map generated:', colors);
  console.log('Makes found:', makes);
  
  setColorMap(colors);
};

  const applyFilters = () => {
    let filtered = [...items];

    // Make filter
    if (makeFilter) {
      filtered = filtered.filter(item => item.make === makeFilter);
    }

    // Condition filter
    if (conditionFilter) {
      filtered = filtered.filter(item => item.condition === conditionFilter);
    }

    // Sold filter
    if (soldFilter === 'unsold') {
      filtered = filtered.filter(item => item.sold?.toUpperCase() !== 'YES');
    } else if (soldFilter === 'sold') {
      filtered = filtered.filter(item => item.sold?.toUpperCase() === 'YES');
    }

    // Price range
    if (minPrice) {
      filtered = filtered.filter(item => (item.sell_price || 0) >= parseFloat(minPrice));
    }
    if (maxPrice) {
      filtered = filtered.filter(item => (item.sell_price || 0) <= parseFloat(maxPrice));
    }

    // Year range
    if (minYear) {
      filtered = filtered.filter(item => (item.year || 0) >= parseInt(minYear));
    }
    if (maxYear) {
      filtered = filtered.filter(item => (item.year || 0) <= parseInt(maxYear));
    }

    // Text search
    if (searchText) {
      const search = searchText.toLowerCase();
      filtered = filtered.filter(item => {
        const searchableText = Object.values(item).join(' ').toLowerCase();
        return searchableText.includes(search);
      });
    }

    // Sort with TOP HAT always first, then alphabetically by Make, then by Year
    filtered.sort((a, b) => {
      // If sorting by sold date is active and we're on sold view, sort by that first
      if (sortBy === 'sold_date' && currentView === 'sold') {
        const dateA = a.sold_date ? new Date(a.sold_date) : new Date(0);
        const dateB = b.sold_date ? new Date(b.sold_date) : new Date(0);
        const dateSort = sortOrder === 'asc' ? dateA - dateB : dateB - dateA;
        if (dateSort !== 0) return dateSort;
      }
      
      const makeA = (a.make || '').toUpperCase();
      const makeB = (b.make || '').toUpperCase();
      
      // TOP HAT always comes first
      if (makeA === 'TOP HAT' && makeB !== 'TOP HAT') return -1;
      if (makeB === 'TOP HAT' && makeA !== 'TOP HAT') return 1;
      
      // Otherwise sort alphabetically by make
      if (makeA < makeB) return -1;
      if (makeA > makeB) return 1;

      // Same make - sort by length ascending (smallest first)
      const lengthA = parseFloat(a.length) || 0;
      const lengthB = parseFloat(b.length) || 0;
      if (lengthA !== lengthB) return lengthA - lengthB;
      
      // Same length - sort by year descending (newest first)
      return (b.year || 0) - (a.year || 0);
    });

    setFilteredItems(filtered);
  };

  const clearFilters = () => {
    setSearchText('');
    setMakeFilter('');
    setConditionFilter('');
    setSoldFilter('');
    setMinPrice('');
    setMaxPrice('');
    setMinYear('');
    setMaxYear('');
  };

  const handleSelectAll = (isSold) => {
    const itemsToSelect = filteredItems.filter(item => 
      (item.sold?.toUpperCase() === 'YES') === isSold
    );
    
    if (itemsToSelect.every(item => selectedIds.has(item.id))) {
      // Deselect all
      const newSelected = new Set(selectedIds);
      itemsToSelect.forEach(item => newSelected.delete(item.id));
      setSelectedIds(newSelected);
    } else {
      // Select all
      const newSelected = new Set(selectedIds);
      itemsToSelect.forEach(item => newSelected.add(item.id));
      setSelectedIds(newSelected);
    }
  };

  const handleSortBySoldDate = () => {
    if (sortBy === 'sold_date') {
      // Toggle sort order if already sorting by sold date
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      // Start sorting by sold date (newest first)
      setSortBy('sold_date');
      setSortOrder('desc');
    }
  };

  const handleRowClick = (itemId) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(itemId)) {
      newSelected.delete(itemId);
    } else {
      newSelected.add(itemId);
    }
    setSelectedIds(newSelected);
  };

  const handleEditSelected = () => {
    if (selectedIds.size === 0) {
      alert('Please select at least one item to edit.');
      return;
    }
    
    if (selectedIds.size === 1) {
      // Single item - full edit
      const itemId = Array.from(selectedIds)[0];
      window.location.href = `/edit/${itemId}?category=${category}`;
    } else {
      // Multiple items - show multi-edit modal
      setShowMultiEditModal(true);
    }
  };

  const handleMultiEdit = async (editData) => {
    try {
      const response = await fetch('/api/inventory/bulk-edit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ids: Array.from(selectedIds),
          category,
          updates: editData
        })
      });
      
      if (response.ok) {
        await fetchInventory();
        setSelectedIds(new Set());
        setShowMultiEditModal(false);
      } else {
        alert('Error updating items');
      }
    } catch (error) {
      console.error('Error updating items:', error);
      alert('Error updating items');
    }
  };
  
  const handleBulkDelete = async () => {
    if (!window.confirm(`Delete ${selectedIds.size} selected items?`)) return;
    
    try {
      const response = await fetch('/api/inventory/bulk-delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ids: Array.from(selectedIds),
          category
        })
      });
      
      if (response.ok) {
        await fetchInventory();
        setSelectedIds(new Set());
      }
    } catch (error) {
      console.error('Error deleting items:', error);
    }
  };

  const handleBulkMarkSold = async () => {
    if (!window.confirm(`Mark ${selectedIds.size} items as sold?`)) return;
    
    const soldDate = new Date().toISOString().split('T')[0];
    
    try {
      const response = await fetch('/api/inventory/bulk-mark-sold', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ids: Array.from(selectedIds),
          category,
          sold_date: soldDate
        })
      });
      
      if (response.ok) {
        await fetchInventory();
        setSelectedIds(new Set());
      }
    } catch (error) {
      console.error('Error marking sold:', error);
    }
  };

  const handleBulkMarkUnsold = async () => {
    if (!window.confirm(`Mark ${selectedIds.size} items as unsold?`)) return;
    
    try {
      const response = await fetch('/api/inventory/bulk-mark-unsold', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ids: Array.from(selectedIds),
          category
        })
      });
      
      if (response.ok) {
        await fetchInventory();
        setSelectedIds(new Set());
      }
    } catch (error) {
      console.error('Error marking unsold:', error);
    }
  };

  const formatCurrency = (value) => {
    if (value == null) return '';
    return `$${Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };

  const getColumnHeaders = () => {
    const commonHeaders = ['List Price'];
    if (userPermissions.hasFinancial) {
      commonHeaders.push('Purchase Price', 'Profit');
    }

    if (category === 'trailers') {
      return ['Length', 'Year', 'Make', 'Type', 'Hitch', 'Width', 'Capacity', 'Description', 'Condition', 'VIN', 'Color', 
              ...(userPermissions.isAuthenticated ? ['Pictures'] : []),
              ...commonHeaders];
    } else if (category === 'trucks') {
      return ['Length', 'Year', 'Make', 'Type', 'Hitch', 'Width', 'Capacity', 'Description', 'Condition', 'VIN', 'Color', 
              ...(userPermissions.isAuthenticated ? ['Pictures'] : []),
              ...commonHeaders];
    } else if (category === 'classic_cars') {
      return ['Length', 'Year', 'Make', 'Type', 'Hitch', 'Width', 'Capacity', 'Description', 'Condition', 'VIN', 'Color', 
              ...(userPermissions.isAuthenticated ? ['Pictures'] : []),
              ...commonHeaders];
    }
    return commonHeaders;
  };

const renderTableCell = (item, header) => {
  if (header === 'Length') return item.length ? Math.floor(item.length) + ' FT' : '';
  if (header === 'List Price') return formatCurrency(item.sell_price);
  if (header === 'Purchase Price') return formatCurrency(item.purchase_price);
  if (header === 'Profit') return formatCurrency(item.profit);
  
  // Pictures - Camera icon linking to Google Drive
  if (header === 'Pictures') {
    if (item.google_drive_folder_id) {
      const folderLink = `https://drive.google.com/drive/folders/${item.google_drive_folder_id}`;
      return (
        <a 
          href={folderLink} 
          target="_blank" 
          rel="noopener noreferrer"
          onClick={(e) => e.stopPropagation()}
          title="View photos in Google Drive"
          style={{ fontSize: '1.2rem' }}
        >
          <i className="fa-solid fa-camera text-primary"></i>
        </a>
      );
    }
    return item.pictures_taken === 'Yes' ? '✓' : '';
  }
  
  // Special handling for VIN - show last 7 when printing
  if (header === 'VIN') {
    const vin = item.vin || '';
    return (
      <>
        <span className="no-print">{vin}</span>
        <span className="print-only">{vin.slice(-7)}</span>
      </>
    );
  }

  // Special handling for Hitch - show BP/GN when printing
  if (header === 'Hitch') {  // Changed from 'Hitch Type'
    const hitchType = item.hitch_type || '';
    let shortForm = '';
    if (hitchType.toLowerCase().includes('bumper')) {
      shortForm = 'BP';
    } else if (hitchType.toLowerCase().includes('gooseneck')) {
      shortForm = 'GN';
    }
    return (
      <>
        <span className="no-print">{hitchType}</span>
        <span className="print-only">{shortForm}</span>
      </>
    );
  }
  
  // Map headers to item properties
  const fieldMap = {
    'Year': 'year',
    'Make': 'make',
    'Type': 'type',
    'Model': 'model',
    'Hitch': 'hitch_type',
    'Width': 'dimensions',
    'Capacity': 'capacity',
    'Description': 'description',
    'Condition': 'condition',
    'VIN': 'vin',
    'Color': 'color',
    'Truck Type': 'truck_type',
    'Mileage': 'mileage',
    'Engine Type': 'engine_type',
    'Hours': 'hours',
    'Mileage': 'mileage',
    'Engine': 'engine_specs',
    'Transmission': 'transmission',
    'Restoration': 'restoration_status'
  };
  
  return item[fieldMap[header]] || '';
};

// Filter based on current view
const unsoldItems = filteredItems.filter(item => item.sold?.toUpperCase() !== 'YES');
const soldItems = filteredItems.filter(item => item.sold?.toUpperCase() === 'YES');

// Show only items for current view
const itemsToShow = currentView === 'sold' ? soldItems : unsoldItems;

const makes = [...new Set(items.map(item => item.make).filter(Boolean))].sort();
const conditions = [...new Set(items.map(item => item.condition).filter(Boolean))].sort();

  if (loading) {
    return (
      <div className="text-center p-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

return (
  <div>
    {/* Search and Filters */}
    <div className="mb-3 no-print">
      <button 
        className="btn btn-primary btn-lg" 
        type="button" 
        data-bs-toggle="collapse" 
        data-bs-target="#searchFiltersPanel"
      >
        <i className="bi bi-funnel-fill"></i> Search & Filters
      </button>
    </div>

    <div className="collapse no-print" id="searchFiltersPanel">
      <div className="search-container">
        <h5 className="mb-3"><i className="bi bi-search"></i> Search & Filters</h5>
        <div className="row g-3">
          <div className="col-md-3">
            <label className="form-label">Search All Fields</label>
            <input 
              type="text" 
              className="form-control" 
              placeholder="Type to search..." 
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
            />
          </div>
          <div className="col-md-2">
            <label className="form-label">Make</label>
            <select className="form-select" value={makeFilter} onChange={(e) => setMakeFilter(e.target.value)}>
              <option value="">All</option>
              {makes.map(make => <option key={make} value={make}>{make}</option>)}
            </select>
          </div>
          <div className="col-md-2">
            <label className="form-label">Condition</label>
            <select className="form-select" value={conditionFilter} onChange={(e) => setConditionFilter(e.target.value)}>
              <option value="">All</option>
              {conditions.map(cond => <option key={cond} value={cond}>{cond}</option>)}
            </select>
          </div>
          <div className="col-md-2">
            <label className="form-label">Status</label>
            <select className="form-select" value={soldFilter} onChange={(e) => setSoldFilter(e.target.value)}>
              <option value="">All</option>
              <option value="unsold">Unsold Only</option>
              <option value="sold">Sold Only</option>
            </select>
          </div>
        </div>
        <div className="row g-3 mt-2">
          <div className="col-md-2">
            <label className="form-label">Min Price</label>
            <input 
              type="number" 
              className="form-control" 
              placeholder="$0" 
              value={minPrice}
              onChange={(e) => setMinPrice(e.target.value)}
            />
          </div>
          <div className="col-md-2">
            <label className="form-label">Max Price</label>
            <input 
              type="number" 
              className="form-control" 
              placeholder="No limit" 
              value={maxPrice}
              onChange={(e) => setMaxPrice(e.target.value)}
            />
          </div>
          <div className="col-md-2">
            <label className="form-label">Min Year</label>
            <input 
              type="number" 
              className="form-control" 
              placeholder="Any" 
              value={minYear}
              onChange={(e) => setMinYear(e.target.value)}
            />
          </div>
          <div className="col-md-2">
            <label className="form-label">Max Year</label>
            <input 
              type="number" 
              className="form-control" 
              placeholder="Any" 
              value={maxYear}
              onChange={(e) => setMaxYear(e.target.value)}
            />
          </div>
          <div className="col-md-2 d-flex align-items-end">
            <button className="btn btn-danger w-100" onClick={clearFilters}>
              <i className="bi bi-x-circle"></i> Clear Filters
            </button>
          </div>
        </div>
      </div>
    </div>

    {/* Summary Stats */}
    {userPermissions.hasSummary && summary && (
      <div className="stats-card no-print">
        <h5>{currentView === 'sold' ? 'Sold' : 'Unsold'} Items Summary</h5>
        <div className="row">
          <div className="col-md-4">
            <strong>Total {currentView === 'sold' ? 'Revenue' : 'List Price'}:</strong> {formatCurrency(currentView === 'sold' ? summary.sold.sell_total : summary.unsold.sell_total)}
          </div>
          <div className="col-md-4">
            <strong>Total {currentView === 'sold' ? 'Cost' : 'Purchase Price'}:</strong> {formatCurrency(currentView === 'sold' ? summary.sold.purchase_total : summary.unsold.purchase_total)}
          </div>
          <div className="col-md-4">
            <strong>Total Profit:</strong> <span className="text-success">{formatCurrency(currentView === 'sold' ? summary.sold.profit_total : summary.unsold.profit_total)}</span>
          </div>
        </div>
      </div>
    )}

    {/* Items Table */}
    <div className="table-container">
      <h4 className="section-header no-print">
        <i className={`bi bi-${currentView === 'sold' ? 'check2-square' : 'box-seam'}`}></i> {currentView === 'sold' ? 'Sold' : 'Unsold'} Items
      </h4>
      <p className="text-muted no-print">Showing {itemsToShow.length} {currentView === 'sold' ? 'sold' : 'unsold'} item(s)</p>
      
      {userPermissions.isAuthenticated && (
        <div className="mb-3 no-print">
          <div className="form-check form-check-inline">
            <input 
              type="checkbox" 
              className="form-check-input" 
              id="selectAll"
              onChange={() => handleSelectAll(currentView === 'sold')}
              checked={itemsToShow.length > 0 && itemsToShow.every(item => selectedIds.has(item.id))}
            />
            <label className="form-check-label" htmlFor="selectAll">Select All</label>
          </div>
          {userPermissions.hasDelete && (
            <button 
              className="btn btn-danger btn-sm" 
              onClick={handleBulkDelete}
              disabled={selectedIds.size === 0}
            >
              <i className="bi bi-trash"></i> Delete Selected
            </button>
          )}
          <button 
            className="btn btn-warning btn-sm ms-2" 
            onClick={handleEditSelected}
            disabled={selectedIds.size == 0}
          >
            <i className="bi bi-pencil"></i> Edit Selected
          </button>
          {currentView === 'sold' ? (
            <button 
              className="btn btn-info btn-sm ms-2" 
              onClick={handleBulkMarkUnsold}
              disabled={selectedIds.size === 0}
            >
              <i className="bi bi-arrow-counterclockwise"></i> Mark as Unsold
            </button>
          ) : (
            <button 
              className="btn btn-success btn-sm ms-2" 
              onClick={handleBulkMarkSold}
              disabled={selectedIds.size === 0}
            >
              <i className="bi bi-check-circle"></i> Mark Sold
            </button>
          )}
        </div>
      )}

      <div className="table-responsive">
        <table className="table table-hover table-sm">
          <thead>
            <tr>
              {userPermissions.isAuthenticated && <th>Select</th>}
              <th>FB</th>
              <th>#</th>
              {getColumnHeaders().map(header => (
                <th key={header} className={(header === 'Purchase Price' || header === 'Profit') ? 'financial-column' : ''}>
                  {header}
                </th>
              ))}
              {currentView === 'sold' && (
                <th 
                  style={{ cursor: 'pointer', userSelect: 'none' }}
                  onClick={handleSortBySoldDate}
                  title="Click to sort by date"
                >
                  Sold Date {sortBy === 'sold_date' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
              )}
            </tr>
          </thead>
          <tbody>
            {itemsToShow.map((item, index) => (
              <tr 
                key={item.id}
                style={{ cursor: 'pointer' }}
                onClick={() => userPermissions.isAuthenticated && handleRowClick(item.id)}
                onDoubleClick={() => window.location.href = `/edit/${item.id}?category=${category}`}
              >
                {userPermissions.isAuthenticated && (
                  <td className="text-center" style={{ backgroundColor: colorMap[item.make] || '#ffffff' }}>
                    <input 
                      type="checkbox" 
                      className="form-check-input"
                      checked={selectedIds.has(item.id)}
                      onChange={() => {}}
                      onClick={(e) => e.stopPropagation()}
                    />
                  </td>
                )}
                {/* Facebook Icon - visible to everyone */}
                <td 
                  className="text-center" 
                  style={{ backgroundColor: colorMap[item.make] || '#ffffff' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  {item.facebook_url ? (
                    <a 
                      href={item.facebook_url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      title={`Posted: ${item.facebook_posted_date || 'Unknown date'}`}
                      style={{ fontSize: '1.2rem' }}
                    >
                      <i className={`bi bi-facebook text-primary ${isExpiredPost(item.facebook_posted_date) ? 'opacity-50' : ''}`}></i>
                    </a>
                  ) : (
                    <span className="text-muted">-</span>
                  )}
                </td>
                <td className="row-number-cell" style={{ backgroundColor: colorMap[item.make] || '#ffffff' }}>{index + 1}</td>
                {getColumnHeaders().map(header => (
                  <td 
                    key={header}
                    className={(header === 'Purchase Price' || header === 'Profit') && userPermissions.hasFinancial ? 'financial-cell' : ''}
                    style={{ backgroundColor: (header === 'Purchase Price' || header === 'Profit') && userPermissions.hasFinancial ? 'white' : (colorMap[item.make] || '#ffffff') }}
                  >
                    {renderTableCell(item, header)}
                  </td>
                ))}
                {currentView === 'sold' && <td style={{ backgroundColor: 'white' }}>{item.sold_date || ''}</td>}
              </tr>
            ))}
          </tbody>
        </table>
</div>
    </div>

    {/* Multi-Edit Modal */}
    {showMultiEditModal && (
      <MultiEditModal 
        onClose={() => setShowMultiEditModal(false)}
        onSave={handleMultiEdit}
        itemCount={selectedIds.size}
        userPermissions={userPermissions}
      />
    )}
  </div>
);
};

const MultiEditModal = ({ onClose, onSave, itemCount, userPermissions }) => {
  const [formData, setFormData] = React.useState({
    sold: '',
    sold_date: '',
    pictures_taken: '',
    facebook_posted_date: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Only include fields that have values
    const updates = {};
    if (formData.sold) updates.sold = formData.sold;
    if (formData.sold_date) updates.sold_date = formData.sold_date;
    if (formData.pictures_taken) updates.pictures_taken = formData.pictures_taken;
    if (formData.facebook_posted_date) updates.facebook_posted_date = formData.facebook_posted_date;
    
    if (Object.keys(updates).length === 0) {
      alert('Please select at least one field to update');
      return;
    }
    
    onSave(updates);
  };

  return (
    <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Edit {itemCount} Selected Items</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <form onSubmit={handleSubmit}>
            <div className="modal-body">
              <p className="text-muted">Only fields with values will be updated. Leave blank to keep current values.</p>
              
              <div className="mb-3">
                <label className="form-label">Sold Status</label>
                <select 
                  className="form-select"
                  value={formData.sold}
                  onChange={(e) => setFormData({...formData, sold: e.target.value})}
                >
                  <option value="">-- No Change --</option>
                  <option value="No">Not Sold</option>
                  <option value="Yes">Sold</option>
                </select>
              </div>
              
              <div className="mb-3">
                <label className="form-label">Sold Date</label>
                <input 
                  type="date"
                  className="form-control"
                  value={formData.sold_date}
                  onChange={(e) => setFormData({...formData, sold_date: e.target.value})}
                />
              </div>
              
              {userPermissions.isAdmin && (
                <>
                  <div className="mb-3">
                    <label className="form-label">Pictures Taken</label>
                    <select 
                      className="form-select"
                      value={formData.pictures_taken}
                      onChange={(e) => setFormData({...formData, pictures_taken: e.target.value})}
                    >
                      <option value="">-- No Change --</option>
                      <option value="No">No</option>
                      <option value="Yes">Yes</option>
                    </select>
                  </div>
                  
                  <div className="mb-3">
                    <label className="form-label">Facebook Posted Date</label>
                    <input 
                      type="date"
                      className="form-control"
                      value={formData.facebook_posted_date}
                      onChange={(e) => setFormData({...formData, facebook_posted_date: e.target.value})}
                    />
                  </div>
                </>
              )}
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
              <button type="submit" className="btn btn-primary">Update {itemCount} Items</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

window.InventoryTable = InventoryTable;