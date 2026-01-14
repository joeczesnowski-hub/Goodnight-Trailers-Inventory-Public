const AdminPanel = () => {
  const [activeTab, setActiveTab] = React.useState('users');
  const [users, setUsers] = React.useState([]);
  const [groups, setGroups] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState('');
  const [editingUser, setEditingUser] = React.useState(null);
  const [editingGroup, setEditingGroup] = React.useState(null);
  const [showAddModal, setShowAddModal] = React.useState(false);
  const [showAddGroupModal, setShowAddGroupModal] = React.useState(false);

  React.useEffect(() => {
    fetchUsers();
    fetchGroups();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await fetch('/admin/api/users');
      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError('Error loading users');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchGroups = async () => {
    try {
      const response = await fetch('/admin/api/groups');
      const data = await response.json();
      setGroups(data);
    } catch (err) {
      console.error('Error loading groups:', err);
    }
  };

  const handleEditClick = (user) => {
    setEditingUser({
      id: user.id,
      username: user.username,
      email: user.email || '',
      group_id: user.group_id || '',
      is_active: user.is_active,
      new_password: ''
    });
  };

  const handleEditGroupClick = (group) => {
    setEditingGroup({
      id: group.id,
      name: group.name,
      can_view: group.can_view,
      can_edit: group.can_edit,
      can_delete: group.can_delete,
      can_view_financial: group.can_view_financial,
      can_view_summary: group.can_view_summary,
      can_view_sold: group.can_view_sold,
      receive_new_item_emails: group.receive_new_item_emails,
      receive_sold_item_emails: group.receive_sold_item_emails,
      user_count: group.user_count
    });
  };

  const handleSaveEdit = async () => {
    try {
      const formData = new URLSearchParams();
      formData.append('email', editingUser.email);
      formData.append('group_id', editingUser.group_id);
      formData.append('is_active', editingUser.is_active);
      if (editingUser.new_password) {
        formData.append('new_password', editingUser.new_password);
      }

      const response = await fetch(`/admin/users/${editingUser.id}/edit`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData
      });

      if (response.ok) {
        await fetchUsers();
        setEditingUser(null);
      } else {
        alert('Error updating user');
      }
    } catch (err) {
      console.error(err);
      alert('Error updating user');
    }
  };

  const handleSaveGroup = async () => {
    try {
      const response = await fetch(`/admin/api/groups/${editingGroup.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editingGroup)
      });

      if (response.ok) {
        await fetchGroups();
        await fetchUsers();
        setEditingGroup(null);
      } else {
        const data = await response.json();
        alert(data.error || 'Error updating group');
      }
    } catch (err) {
      console.error(err);
      alert('Error updating group');
    }
  };

  const handleDeleteUser = async (userId, username) => {
    if (!confirm(`Are you sure you want to delete user "${username}"?`)) return;

    try {
      const response = await fetch(`/admin/users/${userId}/delete`, {
        method: 'POST'
      });

      if (response.ok) {
        await fetchUsers();
      } else {
        alert('Error deleting user');
      }
    } catch (err) {
      console.error(err);
      alert('Error deleting user');
    }
  };

  const handleDeleteGroup = async (groupId, groupName, userCount) => {
    if (userCount > 0) {
      alert(`Cannot delete group "${groupName}" - it has ${userCount} user(s) assigned.`);
      return;
    }
    if (!confirm(`Are you sure you want to delete group "${groupName}"?`)) return;

    try {
      const response = await fetch(`/admin/api/groups/${groupId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        await fetchGroups();
      } else {
        const data = await response.json();
        alert(data.error || 'Error deleting group');
      }
    } catch (err) {
      console.error(err);
      alert('Error deleting group');
    }
  };

  const handleAddUser = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);

    try {
      const response = await fetch('/admin/users/add', {
        method: 'POST',
        body: new URLSearchParams(formData)
      });

      if (response.ok) {
        await fetchUsers();
        setShowAddModal(false);
        e.target.reset();
      } else {
        alert('Error adding user');
      }
    } catch (err) {
      console.error(err);
      alert('Error adding user');
    }
  };

  const handleAddGroup = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = {
      name: formData.get('name'),
      can_view: 1,
      can_edit: 0,
      can_delete: 0,
      can_view_financial: 0,
      can_view_summary: 0,
      can_view_sold: 0
    };

    try {
      const response = await fetch('/admin/api/groups', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        await fetchGroups();
        setShowAddGroupModal(false);
        e.target.reset();
      } else {
        const result = await response.json();
        alert(result.error || 'Error adding group');
      }
    } catch (err) {
      console.error(err);
      alert('Error adding group');
    }
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
          <h2 style={{ margin: 0 }}><i className="bi bi-people"></i> User & Group Management</h2>
          <p style={{ margin: '5px 0 0 0', opacity: 0.9 }}>Manage user accounts and group permissions</p>
        </div>
        <a href="/" className="btn btn-light">
          <i className="bi bi-arrow-left"></i> Back to Inventory
        </a>
      </div>

      {/* Error Alert */}
      {error && (
        <div className="alert alert-danger">{error}</div>
      )}

      {/* Tabs */}
      <ul className="nav nav-tabs mb-3">
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'users' ? 'active' : ''}`}
            onClick={() => setActiveTab('users')}
            style={{ cursor: 'pointer' }}
          >
            <i className="bi bi-people"></i> Users ({users.length})
          </button>
        </li>
        <li className="nav-item">
          <button 
            className={`nav-link ${activeTab === 'groups' ? 'active' : ''}`}
            onClick={() => setActiveTab('groups')}
            style={{ cursor: 'pointer' }}
          >
            <i className="bi bi-collection"></i> Groups ({groups.length})
          </button>
        </li>
      </ul>

      {/* Users Tab */}
      {activeTab === 'users' && (
        <>
          <div className="mb-3">
            <button 
              className="btn btn-primary"
              onClick={() => setShowAddModal(true)}
            >
              <i className="bi bi-plus-circle"></i> Add New User
            </button>
          </div>

          <div style={{
            background: 'white',
            borderRadius: '10px',
            padding: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <div className="table-responsive">
              <table className="table table-hover">
                <thead style={{ background: '#667eea', color: 'white' }}>
                  <tr>
                    <th>ID</th>
                    <th>Username</th>
                    <th>Email</th>
                    <th>Group</th>
                    <th>Status</th>
                    <th>Last Login</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map(user => (
                    <tr key={user.id}>
                      <td>{user.id}</td>
                      <td>{user.username}</td>
                      <td>{user.email || <span className="text-muted">Not set</span>}</td>
                      <td>
                        <span className={`badge bg-${user.group_name === 'Admin' ? 'danger' : user.group_name === 'Marketing' ? 'warning' : 'primary'}`}>
                          {user.group_name || 'No Group'}
                        </span>
                      </td>
                      <td>
                        <span className={`badge bg-${user.is_active ? 'success' : 'secondary'}`}>
                          {user.is_active ? 'Active' : 'Locked'}
                        </span>
                      </td>
                      <td>{user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}</td>
                      <td>
                        <div className="btn-group btn-group-sm">
                          {user.username !== 'anonymous' && (
                            <>
                              <button 
                                className="btn btn-primary"
                                onClick={() => handleEditClick(user)}
                              >
                                <i className="bi bi-pencil"></i> Edit
                              </button>
                              <button 
                                className="btn btn-danger"
                                onClick={() => handleDeleteUser(user.id, user.username)}
                              >
                                <i className="bi bi-trash"></i>
                              </button>
                            </>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Groups Tab */}
      {activeTab === 'groups' && (
        <>
          <div className="mb-3">
            <button 
              className="btn btn-primary"
              onClick={() => setShowAddGroupModal(true)}
            >
              <i className="bi bi-plus-circle"></i> Add New Group
            </button>
          </div>

          <div style={{
            background: 'white',
            borderRadius: '10px',
            padding: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
          }}>
            <div className="table-responsive">
              <table className="table table-hover">
                <thead style={{ background: '#667eea', color: 'white' }}>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Users</th>
                    <th>View</th>
                    <th>Edit</th>
                    <th>Delete</th>
                    <th>Financial</th>
                    <th>Summary</th>
                    <th>Sold</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {groups.map(group => (
                    <tr key={group.id}>
                      <td>{group.id}</td>
                      <td><strong>{group.name}</strong></td>
                      <td><span className="badge bg-secondary">{group.user_count}</span></td>
                      <td>{group.can_view ? <i className="bi bi-check-circle text-success"></i> : <i className="bi bi-x-circle text-danger"></i>}</td>
                      <td>{group.can_edit ? <i className="bi bi-check-circle text-success"></i> : <i className="bi bi-x-circle text-danger"></i>}</td>
                      <td>{group.can_delete ? <i className="bi bi-check-circle text-success"></i> : <i className="bi bi-x-circle text-danger"></i>}</td>
                      <td>{group.can_view_financial ? <i className="bi bi-check-circle text-success"></i> : <i className="bi bi-x-circle text-danger"></i>}</td>
                      <td>{group.can_view_summary ? <i className="bi bi-check-circle text-success"></i> : <i className="bi bi-x-circle text-danger"></i>}</td>
                      <td>{group.can_view_sold ? <i className="bi bi-check-circle text-success"></i> : <i className="bi bi-x-circle text-danger"></i>}</td>
                      <td>
                        <div className="btn-group btn-group-sm">
                          <button 
                            className="btn btn-primary"
                            onClick={() => handleEditGroupClick(group)}
                          >
                            <i className="bi bi-pencil"></i> Edit
                          </button>
                          <button 
                            className="btn btn-danger"
                            onClick={() => handleDeleteGroup(group.id, group.name, group.user_count)}
                            disabled={group.user_count > 0}
                          >
                            <i className="bi bi-trash"></i>
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {/* Edit User Modal */}
      {editingUser && (
        <EditUserModal 
          user={editingUser}
          groups={groups}
          onClose={() => setEditingUser(null)}
          onSave={handleSaveEdit}
          onChange={(field, value) => setEditingUser(prev => ({...prev, [field]: value}))}
        />
      )}

      {/* Edit Group Modal */}
      {editingGroup && (
        <EditGroupModal 
          group={editingGroup}
          onClose={() => setEditingGroup(null)}
          onSave={handleSaveGroup}
          onChange={(field, value) => setEditingGroup(prev => ({...prev, [field]: value}))}
        />
      )}

      {/* Add User Modal */}
      {showAddModal && (
        <AddUserModal 
          groups={groups}
          onClose={() => setShowAddModal(false)}
          onSubmit={handleAddUser}
        />
      )}

      {/* Add Group Modal */}
      {showAddGroupModal && (
        <AddGroupModal 
          onClose={() => setShowAddGroupModal(false)}
          onSubmit={handleAddGroup}
        />
      )}
    </div>
  );
};

const EditUserModal = ({ user, groups, onClose, onSave, onChange }) => {
  return (
    <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Edit User: {user.username}</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            <div className="mb-3">
              <label className="form-label">Email Address</label>
              <input 
                type="email" 
                className="form-control"
                value={user.email}
                onChange={(e) => onChange('email', e.target.value)}
                placeholder="user@example.com"
              />
            </div>
            <div className="mb-3">
              <label className="form-label">Group</label>
              <select 
                className="form-select"
                value={user.group_id}
                onChange={(e) => onChange('group_id', e.target.value)}
              >
                <option value="">Select a group...</option>
                {groups.map(group => (
                  <option key={group.id} value={group.id}>{group.name}</option>
                ))}
              </select>
              <small className="text-muted">Permissions are determined by the group</small>
            </div>
            <div className="mb-3">
              <label className="form-label">Status</label>
              <select 
                className="form-select"
                value={user.is_active}
                onChange={(e) => onChange('is_active', e.target.value)}
              >
                <option value="1">Active</option>
                <option value="0">Locked</option>
              </select>
            </div>
            <div className="mb-3">
              <label className="form-label">New Password</label>
              <input 
                type="password" 
                className="form-control"
                value={user.new_password}
                onChange={(e) => onChange('new_password', e.target.value)}
                placeholder="Leave blank to keep current password"
              />
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="button" className="btn btn-primary" onClick={onSave}>Save Changes</button>
          </div>
        </div>
      </div>
    </div>
  );
};

const EditGroupModal = ({ group, onClose, onSave, onChange }) => {
  return (
    <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog modal-lg">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title">Edit Group: {group.name}</h5>
            <button type="button" className="btn-close" onClick={onClose}></button>
          </div>
          <div className="modal-body">
            <div className="mb-3">
              <label className="form-label">Group Name</label>
              <input 
                type="text" 
                className="form-control"
                value={group.name}
                onChange={(e) => onChange('name', e.target.value)}
              />
            </div>
            
            <h6 className="border-bottom pb-2 mb-3">Permissions</h6>
            <p className="text-muted small">Changes apply to all {group.user_count} user(s) in this group</p>
            
            <div className="row">
              <div className="col-md-6">
                <div className="form-check mb-2">
                  <input 
                    className="form-check-input" 
                    type="checkbox" 
                    id="can_view"
                    checked={group.can_view}
                    onChange={(e) => onChange('can_view', e.target.checked ? 1 : 0)}
                  />
                  <label className="form-check-label" htmlFor="can_view">
                    <i className="bi bi-eye"></i> Can View Inventory
                  </label>
                </div>
                <div className="form-check mb-2">
                  <input 
                    className="form-check-input" 
                    type="checkbox" 
                    id="can_edit"
                    checked={group.can_edit}
                    onChange={(e) => onChange('can_edit', e.target.checked ? 1 : 0)}
                  />
                  <label className="form-check-label" htmlFor="can_edit">
                    <i className="bi bi-pencil"></i> Can Edit Items
                  </label>
                </div>
                <div className="form-check mb-2">
                  <input 
                    className="form-check-input" 
                    type="checkbox" 
                    id="can_delete"
                    checked={group.can_delete}
                    onChange={(e) => onChange('can_delete', e.target.checked ? 1 : 0)}
                  />
                  <label className="form-check-label" htmlFor="can_delete">
                    <i className="bi bi-trash"></i> Can Delete Items
                  </label>
                </div>
              </div>
              <div className="col-md-6">
                <div className="form-check mb-2">
                  <input 
                    className="form-check-input" 
                    type="checkbox" 
                    id="can_view_financial"
                    checked={group.can_view_financial}
                    onChange={(e) => onChange('can_view_financial', e.target.checked ? 1 : 0)}
                  />
                  <label className="form-check-label" htmlFor="can_view_financial">
                    <i className="bi bi-currency-dollar"></i> Can View Financial Data
                  </label>
                </div>
                <div className="form-check mb-2">
                  <input 
                    className="form-check-input" 
                    type="checkbox" 
                    id="can_view_summary"
                    checked={group.can_view_summary}
                    onChange={(e) => onChange('can_view_summary', e.target.checked ? 1 : 0)}
                  />
                  <label className="form-check-label" htmlFor="can_view_summary">
                    <i className="bi bi-card-list"></i> Can View Summary
                  </label>
                </div>
                <div className="form-check mb-2">
                  <input 
                    className="form-check-input" 
                    type="checkbox" 
                    id="can_view_sold"
                    checked={group.can_view_sold}
                    onChange={(e) => onChange('can_view_sold', e.target.checked ? 1 : 0)}
                  />
                  <label className="form-check-label" htmlFor="can_view_sold">
                    <i className="bi bi-archive"></i> Can View Sold Items
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
            <button type="button" className="btn btn-primary" onClick={onSave}>Save Changes</button>
          </div>
        </div>
      </div>
    </div>
  );
};

const AddUserModal = ({ groups, onClose, onSubmit }) => {
  return (
    <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog">
        <div className="modal-content">
          <form onSubmit={onSubmit}>
            <div className="modal-header">
              <h5 className="modal-title">Add New User</h5>
              <button type="button" className="btn-close" onClick={onClose}></button>
            </div>
            <div className="modal-body">
              <div className="mb-3">
                <label className="form-label">Username *</label>
                <input type="text" className="form-control" name="username" required />
              </div>
              <div className="mb-3">
                <label className="form-label">Password *</label>
                <input type="password" className="form-control" name="password" required />
              </div>
              <div className="mb-3">
                <label className="form-label">Email</label>
                <input type="email" className="form-control" name="email" />
              </div>
              <div className="mb-3">
                <label className="form-label">Group *</label>
                <select className="form-select" name="group_id" required>
                  <option value="">Select a group...</option>
                  {groups.map(group => (
                    <option key={group.id} value={group.id}>{group.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
              <button type="submit" className="btn btn-primary">Add User</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

const AddGroupModal = ({ onClose, onSubmit }) => {
  return (
    <div className="modal show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
      <div className="modal-dialog">
        <div className="modal-content">
          <form onSubmit={onSubmit}>
            <div className="modal-header">
              <h5 className="modal-title">Add New Group</h5>
              <button type="button" className="btn-close" onClick={onClose}></button>
            </div>
            <div className="modal-body">
              <div className="mb-3">
                <label className="form-label">Group Name *</label>
                <input type="text" className="form-control" name="name" required />
              </div>
              <p className="text-muted small">
                The group will be created with default permissions (View only). 
                You can edit permissions after creation.
              </p>
            </div>
            <div className="modal-footer">
              <button type="button" className="btn btn-secondary" onClick={onClose}>Cancel</button>
              <button type="submit" className="btn btn-primary">Add Group</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

window.AdminPanel = AdminPanel;