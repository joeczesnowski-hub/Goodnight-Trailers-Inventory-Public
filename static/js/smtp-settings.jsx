const SMTPSettings = () => {
  const [loading, setLoading] = React.useState(false);
  const [message, setMessage] = React.useState({ type: '', text: '' });
  const [testEmailSending, setTestEmailSending] = React.useState(false);
  
  const [settings, setSettings] = React.useState({
    mail_server: '',
    mail_port: '',
    mail_use_tls: true,
    mail_username: '',
    mail_password: '',
    mail_default_sender: ''
  });

  React.useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await fetch('/admin/api/smtp-settings');
      const data = await response.json();
      setSettings({
        mail_server: data.mail_server || 'smtp.gmail.com',
        mail_port: data.mail_port || '587',
        mail_use_tls: data.mail_use_tls !== false,
        mail_username: data.mail_username || '',
        mail_password: '', // Never show password
        mail_default_sender: data.mail_default_sender || ''
      });
    } catch (err) {
      console.error('Error fetching settings:', err);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setMessage({ type: '', text: '' });
    setLoading(true);

    try {
      const response = await fetch('/admin/smtp-settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage({ type: 'success', text: 'SMTP settings saved successfully!' });
      } else {
        setMessage({ type: 'danger', text: data.error || 'Error saving settings' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Network error. Please try again.' });
    } finally {
      setLoading(false);
    }
  };

  const handleTestEmail = async () => {
    setMessage({ type: '', text: '' });
    setTestEmailSending(true);

    try {
      const response = await fetch('/admin/test-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();
      
      if (response.ok) {
        setMessage({ type: 'success', text: 'Test email sent successfully! Check your inbox.' });
      } else {
        setMessage({ type: 'danger', text: data.error || 'Failed to send test email' });
      }
    } catch (err) {
      setMessage({ type: 'danger', text: 'Network error. Please try again.' });
    } finally {
      setTestEmailSending(false);
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
          <h2 style={{ margin: 0 }}><i className="bi bi-envelope-gear"></i> SMTP Settings</h2>
          <p style={{ margin: '5px 0 0 0', opacity: 0.9 }}>Configure email server for sending notifications</p>
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

      <div className="row">
        <div className="col-lg-8 mx-auto">
          <div style={{
            background: 'white',
            borderRadius: '10px',
            padding: '30px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <form onSubmit={handleSave}>
              <div className="alert alert-info">
                <i className="bi bi-info-circle"></i> <strong>Gmail Users:</strong> Use an{' '}
                <a href="https://support.google.com/accounts/answer/185833" target="_blank" rel="noopener">App Password</a>
                {' '}instead of your regular password for better security.
              </div>

              <h5 className="mb-4"><i className="bi bi-server"></i> SMTP Server Configuration</h5>
              
              <div className="row mb-3">
                <div className="col-md-8">
                  <label className="form-label">SMTP Server</label>
                  <input 
                    type="text" 
                    className="form-control"
                    value={settings.mail_server}
                    onChange={(e) => setSettings({...settings, mail_server: e.target.value})}
                    placeholder="smtp.gmail.com"
                    required
                  />
                  <small className="text-muted">
                    Common: smtp.gmail.com, smtp.office365.com, smtp.mail.yahoo.com
                  </small>
                </div>
                <div className="col-md-4">
                  <label className="form-label">Port</label>
                  <input 
                    type="number" 
                    className="form-control"
                    value={settings.mail_port}
                    onChange={(e) => setSettings({...settings, mail_port: e.target.value})}
                    placeholder="587"
                    required
                  />
                  <small className="text-muted">Usually 587</small>
                </div>
              </div>

              <div className="mb-4">
                <div className="form-check">
                  <input 
                    className="form-check-input" 
                    type="checkbox"
                    id="useTLS"
                    checked={settings.mail_use_tls}
                    onChange={(e) => setSettings({...settings, mail_use_tls: e.target.checked})}
                  />
                  <label className="form-check-label" htmlFor="useTLS">
                    <strong>Use TLS/STARTTLS</strong> (Recommended for port 587)
                  </label>
                </div>
              </div>

              <hr className="my-4" />

              <h5 className="mb-4"><i className="bi bi-person-badge"></i> Email Account Credentials</h5>

              <div className="mb-3">
                <label className="form-label">Email Address / Username</label>
                <input 
                  type="email" 
                  className="form-control"
                  value={settings.mail_username}
                  onChange={(e) => setSettings({...settings, mail_username: e.target.value})}
                  placeholder="your-email@gmail.com"
                  required
                />
              </div>

              <div className="mb-3">
                <label className="form-label">Password / App Password</label>
                <input 
                  type="password" 
                  className="form-control"
                  value={settings.mail_password}
                  onChange={(e) => setSettings({...settings, mail_password: e.target.value})}
                  placeholder="Enter password or leave blank to keep current"
                  autoComplete="new-password"
                />
                <small className="text-muted">
                  Leave blank to keep the existing password
                </small>
              </div>

              <div className="mb-4">
                <label className="form-label">Sender Email (From Address)</label>
                <input 
                  type="email" 
                  className="form-control"
                  value={settings.mail_default_sender}
                  onChange={(e) => setSettings({...settings, mail_default_sender: e.target.value})}
                  placeholder="noreply@goodnighttrailers.com"
                  required
                />
                <small className="text-muted">
                  This email will appear in the "From" field of sent emails
                </small>
              </div>

              <div className="d-flex gap-2">
                <button 
                  type="submit" 
                  className="btn btn-primary btn-lg"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Saving...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-check-circle"></i> Save Settings
                    </>
                  )}
                </button>

                <button 
                  type="button" 
                  className="btn btn-success btn-lg"
                  onClick={handleTestEmail}
                  disabled={testEmailSending || loading}
                >
                  {testEmailSending ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2"></span>
                      Sending...
                    </>
                  ) : (
                    <>
                      <i className="bi bi-send"></i> Send Test Email
                    </>
                  )}
                </button>
              </div>
            </form>

            <div className="alert alert-warning mt-4" role="alert">
              <i className="bi bi-shield-exclamation"></i> <strong>Security Note:</strong> These credentials are stored securely and used to send email notifications from the system.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

window.SMTPSettings = SMTPSettings;