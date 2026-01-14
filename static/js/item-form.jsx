const ItemForm = ({ itemId, mode }) => {
  const [loading, setLoading] = React.useState(true);
  const [saving, setSaving] = React.useState(false);
  const [message, setMessage] = React.useState({ type: '', text: '' });
  const [category, setCategory] = React.useState('trailers');
  const [options, setOptions] = React.useState({});
  const [formData, setFormData] = React.useState({});
  const [customFields, setCustomFields] = React.useState({});

  React.useEffect(() => {
    fetchFormData();
  }, [itemId]);

const fetchFormData = async () => {
    try {
      setLoading(true);
      
      let cat = 'trailers';
      
      // Get category from URL first (for both add and edit)
      const urlParams = new URLSearchParams(window.location.search);
      cat = urlParams.get('category') || 'trailers';
      setCategory(cat);
      
      // Fetch form options for the correct category
      const optionsRes = await fetch(`/api/form-options/${cat}`);
      const optionsData = await optionsRes.json();
      setOptions(optionsData);
      
      // If editing, fetch item data
      if (mode === 'edit' && itemId) {
        const itemRes = await fetch(`/api/item/${itemId}?category=${cat}`);
        const itemData = await itemRes.json();
        setFormData(itemData);
      } else {
        // Initialize empty form for add mode
        setFormData(getEmptyForm(cat));
      }
      
      setLoading(false);
    } catch (err) {
      console.error('Error loading form:', err);
      setMessage({ type: 'danger', text: 'Error loading form data' });
      setLoading(false);
    }
  };

  const getEmptyForm = (cat) => {
    if (cat === 'trailers') {
      return {
        length: '', year: '', make: '', type: '', dimensions: '', capacity: '',
        description: '', condition: '', vin: '', color: '', hitch_type: '',
        sell_price: '', sold: 'No', purchase_price: '', sold_date: '',
        pictures_taken: 'No', facebook_url: '', facebook_posted_date: ''
      };
    } else if (cat === 'trucks') {
      return {
        year: '', make: '', model: '', boom_height: '', weight_capacity: '',
        engine_type: '', hours: '', vin: '', condition: '', description: '',
        sell_price: '', sold: 'No', purchase_price: '', sold_date: '',
        pictures_taken: 'No', facebook_url: '', facebook_posted_date: ''
      };
    } else if (cat === 'classic_cars') {
      return {
        year: '', make: '', model: '', mileage: '', engine_specs: '', transmission: '',
        vin: '', restoration_status: '', condition: '', color: '', description: '',
        sell_price: '', sold: 'No', purchase_price: '', sold_date: '',
        pictures_taken: 'No', facebook_url: '', facebook_posted_date: ''
      };
    }
  };

  const handleChange = (field, value) => {
    setFormData({ ...formData, [field]: value });
  };

  const handleSelectChange = (field, value) => {
    if (value === 'custom') {
      setCustomFields({ ...customFields, [field]: true });
      handleChange(field, '');
    } else {
      handleChange(field, value);
    }
  };

  const handlePhotoUpload = async (e) => {
    const files = e.target.files;
    if (files.length === 0) return;
    
    // Check if VIN is provided
    if (!formData.vin) {
      alert('Please enter a VIN before uploading photos');
      e.target.value = ''; // Clear the file input
      return;
    }
    
    setMessage({ type: 'info', text: `Uploading ${files.length} photo(s)...` });
    
    const formDataToSend = new FormData();
    formDataToSend.append('vin', formData.vin);
    
    for (let i = 0; i < files.length; i++) {
      formDataToSend.append('photos', files[i]);
    }
    
    try {
      const response = await fetch('/api/upload-photos', {
        method: 'POST',
        body: formDataToSend
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setMessage({ type: 'success', text: `Successfully uploaded ${files.length} photo(s) to Google Drive!` });
        // Store the Drive folder ID
        handleChange('google_drive_folder_id', data.folder_id);
        e.target.value = ''; // Clear the file input
      } else {
        setMessage({ type: 'danger', text: data.error || 'Error uploading photos' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Error uploading photos. Please try again.' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });
    setSaving(true);

    try {
      const url = mode === 'edit' ? `/api/item/${itemId}` : '/api/item/add';
      const method = mode === 'edit' ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: mode === 'edit' ? 'Item updated successfully!' : 'Item added successfully!' 
        });
        setTimeout(() => window.location.href = '/', 1500);
      } else {
        setMessage({ type: 'danger', text: data.error || 'Error saving item' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Network error. Please try again.' });
    } finally {
      setSaving(false);
    }
  };

  const calculateProfit = () => {
    const sell = parseFloat(formData.sell_price) || 0;
    const purchase = parseFloat(formData.purchase_price) || 0;
    return sell - purchase;
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
      padding: '40px 20px'
    }}>
      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        background: 'white',
        borderRadius: '12px',
        boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
        overflow: 'hidden'
      }}>
        {/* Header */}
        <div style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white',
          padding: '30px'
        }}>
          <h1 style={{ margin: 0 }}>
            {mode === 'edit' ? 'Edit' : 'Add'} Item - {category.replace('_', ' ').toUpperCase()}
          </h1>
        </div>

        {/* Message Alert */}
        {message.text && (
          <div className="m-4">
            <div className={`alert alert-${message.type} alert-dismissible fade show`} role="alert">
              {message.text}
              <button type="button" className="btn-close" onClick={() => setMessage({ type: '', text: '' })}></button>
            </div>
          </div>
        )}

        {/* Form */}
        <div style={{ padding: '40px' }}>
          <form onSubmit={handleSubmit}>
            {category === 'trailers' && (
              <TrailersForm 
                formData={formData}
                options={options}
                customFields={customFields}
                handleChange={handleChange}
                handleSelectChange={handleSelectChange}
              />
            )}
            
            {category === 'trucks' && (
              <TrucksForm 
                formData={formData}
                options={options}
                customFields={customFields}
                handleChange={handleChange}
                handleSelectChange={handleSelectChange}
              />
            )}
            
            {category === 'classic_cars' && (
              <ClassicCarsForm 
                formData={formData}
                options={options}
                customFields={customFields}
                handleChange={handleChange}
                handleSelectChange={handleSelectChange}
              />
            )}

            {/* Common Fields - Pricing and Status */}
            <div className="row g-3 mt-4">
            <div className="col-12">
                <hr />
                <h5>Pricing & Status</h5>
            </div>
            
            <div className="col-md-4">
                <label className="form-label fw-bold">List Price <span className="text-danger">*</span></label>
                <input 
                type="number" 
                step="0.01"
                className="form-control"
                value={formData.sell_price || ''}
                onChange={(e) => handleChange('sell_price', e.target.value)}
                required
                />
            </div>
            
            <div className="col-md-4">
                <label className="form-label fw-bold">Purchase Price</label>
                <input 
                type="number" 
                step="0.01"
                className="form-control"
                value={formData.purchase_price || ''}
                onChange={(e) => handleChange('purchase_price', e.target.value)}
                />
            </div>
            
            <div className="col-md-4">
                <label className="form-label fw-bold">Estimated Profit</label>
                <input 
                type="text" 
                className="form-control bg-light"
                value={`$${calculateProfit().toFixed(2)}`}
                disabled
                />
            </div>
            
            <div className="col-md-6">
              <label className="form-label fw-bold">Sold Status</label>
              <select 
                className="form-select"
                value={formData.sold || 'No'}
                onChange={(e) => handleChange('sold', e.target.value)}
              >
                <option value="No">Not Sold</option>
                <option value="Yes">Sold</option>
              </select>
            </div>

            <div className="col-md-6">
              <label className="form-label fw-bold">Sold Date</label>
              <input 
                type="date"
                className="form-control"
                value={formData.sold_date || ''}
                onChange={(e) => handleChange('sold_date', e.target.value)}
              />
            </div>

            {/* Pictures Taken - Admin Only */}
            {window.userPermissions?.isAdmin && (
              <div className="col-md-6">
                <label className="form-label fw-bold">Pictures Taken</label>
                <select 
                  className="form-select"
                  value={formData.pictures_taken || 'No'}
                  onChange={(e) => handleChange('pictures_taken', e.target.value)}
                >
                  <option value="No">No</option>
                  <option value="Yes">Yes</option>
                </select>
              </div>
            )}
            {/* Facebook Tracking & Photo Upload - Admin and Marketing */}
            {(window.userPermissions?.isAdmin || window.userPermissions?.isMarketing) && (
              <>
                <div className="col-md-6">
                  <label className="form-label fw-bold">
                    <i className="bi bi-facebook text-primary"></i> Facebook Post URL
                  </label>
                  <input
                    type="url"
                    className="form-control"
                    value={formData.facebook_url || ''}
                    onChange={(e) => handleChange('facebook_url', e.target.value)}
                    placeholder="https://facebook.com/marketplace/item/..."
                  />
                  <small className="text-muted d-block">Paste the Facebook Marketplace post URL</small>
                </div>
                <div className="col-md-6">
                  <label className="form-label fw-bold">
                    <i className="bi bi-calendar-check text-primary"></i> Facebook Posted Date
                  </label>
                  <input
                    type="date"
                    className="form-control"
                    value={formData.facebook_posted_date || ''}
                    onChange={(e) => handleChange('facebook_posted_date', e.target.value)}
                  />
                  <small className="text-muted d-block">When was this posted to Facebook?</small>
                </div>
                <div className="col-12">
                  <label className="form-label fw-bold">
                    <i className="bi bi-camera text-primary"></i> Upload Photos
                  </label>
                  <input
                    type="file"
                    className="form-control"
                    multiple
                    accept="image/*"
                    id="photoUpload"
                    onChange={(e) => handlePhotoUpload(e)}
                  />
                  <small className="text-muted d-block">Select one or more photos to upload to Google Drive</small>
                </div>
              </>
            )}
            </div>

            {/* Submit Buttons */}
            <div className="mt-4 d-flex gap-2">
              <button 
                type="submit" 
                className="btn btn-primary btn-lg"
                disabled={saving}
              >
                {saving ? (
                  <>
                    <span className="spinner-border spinner-border-sm me-2"></span>
                    Saving...
                  </>
                ) : (
                  <>
                    <i className="bi bi-check-circle"></i> {mode === 'edit' ? 'Update' : 'Add'} Item
                  </>
                )}
              </button>
              
              <a href="/" className="btn btn-secondary btn-lg">
                <i className="bi bi-x-circle"></i> Cancel
              </a>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

window.ItemForm = ItemForm;