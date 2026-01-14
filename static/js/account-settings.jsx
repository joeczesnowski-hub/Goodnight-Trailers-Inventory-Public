const AccountSettings = () => {
  const [activeTab, setActiveTab] = React.useState('password');
  const [loading, setLoading] = React.useState(false);
  const [message, setMessage] = React.useState({ type: '', text: '' });
  
  // Password form state
  const [passwordForm, setPasswordForm] = React.useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });

  // Notification preferences state
  const [email, setEmail] = React.useState('');
  const [notifications, setNotifications] = React.useState({
    receive_new_item_emails: false,
    receive_sold_item_emails: false
  });

  React.useEffect(() => {
    fetchUserSettings();
  }, []);

  const fetchUserSettings = async () => {
    try {
      const response = await fetch('/admin/api/account/settings');
      const data = await response.json();
      setEmail(data.email || '');
      setNotifications({
        receive_new_item_emails: data.receive_new_item_emails === 1,
        receive_sold_item_emails: data.receive_sold_item_emails === 1
      });
    } catch (err) {
      console.error('Error fetching settings:', err);
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setMessage({ type: 'danger', text: 'New passwords do not match' });
      return;
    }

    setLoading(true);
    try {
      const formData = new URLSearchParams({
        action: 'change_password',
        current_password: passwordForm.current_password,
        new_password: passwordForm.new_password,
        confirm_password: passwordForm.confirm_password
      });

      const response = await fetch('/admin/account-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Password changed successfully!' });
        setPasswordForm({ current_password: '', new_password: '', confirm_password: '' });
        setTimeout(() => window.location.href = '/', 2000);
      } else {
        const text = await response.text();
        setMessage({ type: 'danger', text: text || 'Error changing password' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleNotificationsUpdate = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });
    setLoading(true);

    try {
      const formData = new URLSearchParams({
        action: 'update_notifications',
        ...(notifications.receive_new_item_emails && { receive_new_item_emails: '1' }),
        ...(notifications.receive_sold_item_emails && { receive_sold_item_emails: '1' })
      });

      const response = await fetch('/admin/account-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      if (response.ok) {
        setMessage({ type: 'success', text: 'Notification preferences updated!' });
      } else {
        setMessage({ type: 'danger', text: 'Error updating preferences' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

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
          <h2 style={{ margin: 0 }}><i className="bi bi-person-circle"></i> Account Settings</h2>
          <p style={{ margin: '5px 0 0 0', opacity: 0.9 }}>Manage your password and notification preferences</p>
        </div>
        <a href="/" className="btn btn-light">
          <i className="bi bi-arrow-left"></i> Back to Inventory
        </a>
      </div>

      {/* Message Alert */}
      {message.text && (
        <div className={`alert alert-${message.type} alert-dismissible fade show`} role="alert">
          {message.text}
          <button type="button" className="btn-close" onClick={() => setMessage({ type: '', text: '' })}></button>
        </div>
      )}

      {/* Tabs */}
      <div className="row">
        <div className="col-12">
          <ul className="nav nav-tabs mb-3">
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'password' ? 'active' : ''}`}
                onClick={() => setActiveTab('password')}
              >
                <i className="bi bi-key"></i> Change Password
              </button>
            </li>
            <li className="nav-item">
              <button 
                className={`nav-link ${activeTab === 'notifications' ? 'active' : ''}`}
                onClick={() => setActiveTab('notifications')}
              >
                <i className="bi bi-envelope"></i> Email Notifications
              </button>
            </li>
          </ul>
        </div>
      </div>

      <div className="row">
        {/* Password Tab */}
        {activeTab === 'password' && (
          <div className="col-md-6">
            <div className="card">
              <div className="card-header bg-primary text-white">
                <h5 className="mb-0"><i className="bi bi-key"></i> Change Password</h5>
              </div>
              <div className="card-body">
                <form onSubmit={handlePasswordChange}>
                  <div className="mb-3">
                    <label className="form-label">Current Password</label>
                    <input 
                      type="password" 
                      className="form-control"
                      value={passwordForm.current_password}
                      onChange={(e) => setPasswordForm({...passwordForm, current_password: e.target.value})}
                      required
                      disabled={loading}
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">New Password</label>
                    <input 
                      type="password" 
                      className="form-control"
                      value={passwordForm.new_password}
                      onChange={(e) => setPasswordForm({...passwordForm, new_password: e.target.value})}
                      required
                      disabled={loading}
                    />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Confirm New Password</label>
                    <input 
                      type="password" 
                      className="form-control"
                      value={passwordForm.confirm_password}
                      onChange={(e) => setPasswordForm({...passwordForm, confirm_password: e.target.value})}
                      required
                      disabled={loading}
                    />
                  </div>
                  <button type="submit" className="btn btn-primary" disabled={loading}>
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2"></span>
                        Changing...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-circle"></i> Change Password
                      </>
                    )}
                  </button>
                </form>
              </div>
            </div>
          </div>
        )}

        {/* Notifications Tab */}
        {activeTab === 'notifications' && (
          <div className="col-md-6">
            <div className="card">
              <div className="card-header bg-success text-white">
                <h5 className="mb-0"><i className="bi bi-envelope"></i> Email Notifications</h5>
              </div>
              <div className="card-body">
                {email ? (
                  <>
                    <p className="text-muted">Notifications will be sent to: <strong>{email}</strong></p>
                    <form onSubmit={handleNotificationsUpdate}>
                      <div className="form-check mb-3">
                        <input 
                          className="form-check-input" 
                          type="checkbox"
                          id="receiveNewItem"
                          checked={notifications.receive_new_item_emails}
                          onChange={(e) => setNotifications({...notifications, receive_new_item_emails: e.target.checked})}
                          disabled={loading}
                        />
                        <label className="form-check-label" htmlFor="receiveNewItem">
                          <i className="bi bi-envelope-plus"></i> <strong>New Item Alerts</strong><br />
                          <small className="text-muted">Receive email when new inventory is added</small>
                        </label>
                      </div>
                      <div className="form-check mb-3">
                        <input 
                          className="form-check-input" 
                          type="checkbox"
                          id="receiveSoldItem"
                          checked={notifications.receive_sold_item_emails}
                          onChange={(e) => setNotifications({...notifications, receive_sold_item_emails: e.target.checked})}
                          disabled={loading}
                        />
                        <label className="form-check-label" htmlFor="receiveSoldItem">
                          <i className="bi bi-envelope-check"></i> <strong>Sold Item Alerts</strong><br />
                          <small className="text-muted">Receive email when items are marked as sold</small>
                        </label>
                      </div>
                      <button type="submit" className="btn btn-success" disabled={loading}>
                        {loading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2"></span>
                            Saving...
                          </>
                        ) : (
                          <>
                            <i className="bi bi-check-circle"></i> Save Preferences
                          </>
                        )}
                      </button>
                    </form>
                  </>
                ) : (
                  <div className="alert alert-warning">
                    <i className="bi bi-exclamation-triangle"></i> You don't have an email address set. Contact an administrator to add your email address before enabling notifications.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

window.AccountSettings = AccountSettings;