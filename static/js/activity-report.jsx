const ActivityReport = () => {
  const [newItems, setNewItems] = React.useState([]);
  const [deletedItems, setDeletedItems] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState('');
  const [soldItems, setSoldItems] = React.useState([]);

  React.useEffect(() => {
    fetchReport();
  }, []);

  const fetchReport = async () => {
  try {
    setLoading(true);
    const response = await fetch('/admin/api/activity-report');
    const data = await response.json();
    setNewItems(data.new_items || []);
    setDeletedItems(data.deleted_items || []);
    setSoldItems(data.sold_items || []);  // ADD THIS
  } catch (err) {
    setError('Error loading report');
    console.error(err);
  } finally {
    setLoading(false);
  }
};

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleString();
  };

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
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #4a5568 0%, #2d3748 100%)',
      padding: '20px'
    }}>
      {/* Header */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '10px',
        padding: '20px',
        marginBottom: '20px',
        color: 'white',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h2 style={{ margin: 0 }}><i className="bi bi-clock-history"></i> Activity Report</h2>
          <p style={{ margin: '5px 0 0 0', opacity: 0.9 }}>Last 7 Days - New and Deleted Items</p>
        </div>
        <div>
          <a href="/" className="btn btn-light me-2">
            <i className="bi bi-arrow-left"></i> Back to Inventory
          </a>
          <button className="btn btn-success" onClick={() => window.print()}>
            <i className="bi bi-printer"></i> Print Report
          </button>
        </div>
      </div>

      {error && (
        <div className="alert alert-danger">{error}</div>
      )}

      <div className="row">
        {/* New Items */}
        <div className="col-md-4 mb-4">
          <div style={{
            background: 'white',
            borderRadius: '10px',
            padding: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <h4 className="mb-3" style={{ color: '#28a745' }}>
              <i className="bi bi-plus-circle"></i> New Items ({newItems.length})
            </h4>
            {newItems.length === 0 ? (
              <p className="text-muted">No new items in the last 7 days</p>
            ) : (
              <div className="table-responsive">
                <table className="table table-sm table-hover">
                  <thead className="table-success">
                    <tr>
                      <th>Date Added</th>
                      <th>Year</th>
                      <th>Make</th>
                      <th>Type</th>
                      <th>VIN</th>
                    </tr>
                  </thead>
                  <tbody>
                    {newItems.map((item, index) => (
                      <tr key={index}>
                        <td>{formatDate(item.created_at)}</td>
                        <td>{item.year}</td>
                        <td>{item.make}</td>
                        <td>{item.type}</td>
                        <td>{item.vin}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Sold Items */}
        <div className="col-md-4 mb-4">
          <div style={{
            background: 'white',
            borderRadius: '10px',
            padding: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <h4 className="mb-3" style={{ color: '#28a745' }}>
              <i className="bi bi-check-circle"></i> Sold Items ({soldItems.length})
            </h4>
            {soldItems.length === 0 ? (
              <p className="text-muted">No items sold in the last 7 days</p>
            ) : (
              <div className="table-responsive">
                <table className="table table-sm table-hover">
                  <thead className="table-success">
                    <tr>
                      <th>Date Sold</th>
                      <th>Year</th>
                      <th>Make</th>
                      <th>Type</th>
                      <th>VIN</th>
                    </tr>
                  </thead>
                  <tbody>
                    {soldItems.map((item, index) => (
                      <tr key={index}>
                        <td>{formatDate(item.sold_date)}</td>
                        <td>{item.year}</td>
                        <td>{item.make}</td>
                        <td>{item.type}</td>
                        <td>{item.vin}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
        
        {/* Deleted Items */}
        <div className="col-md-4 mb-4">
          <div style={{
            background: 'white',
            borderRadius: '10px',
            padding: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <h4 className="mb-3" style={{ color: '#dc3545' }}>
              <i className="bi bi-trash"></i> Deleted Items ({deletedItems.length})
            </h4>
            {deletedItems.length === 0 ? (
              <p className="text-muted">No deleted items in the last 7 days</p>
            ) : (
              <div className="table-responsive">
                <table className="table table-sm table-hover">
                  <thead className="table-danger">
                    <tr>
                      <th>Date Deleted</th>
                      <th>Year</th>
                      <th>Make</th>
                      <th>Type</th>
                      <th>VIN</th>
                    </tr>
                  </thead>
                  <tbody>
                    {deletedItems.map((item, index) => (
                      <tr key={index}>
                        <td>{formatDate(item.deleted_at)}</td>
                        <td>{item.year}</td>
                        <td>{item.make}</td>
                        <td>{item.type}</td>
                        <td>{item.vin}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

window.ActivityReport = ActivityReport;