const SelectOrCustom = ({ field, label, optionsList, required = false, type = "text", step = null, formData, customFields, handleChange, handleSelectChange }) => (
  <div>
    <label className="form-label fw-bold">
      {label} {required && <span className="text-danger">*</span>}
    </label>
    
    {!customFields[field] ? (
      <>
        <select 
          className="form-select"
          value={formData[field] || ''}
          onChange={(e) => handleSelectChange(field, e.target.value)}
          required={required}
        >
          <option value="">Select {label}</option>
          {optionsList?.map((opt, idx) => (
            <option key={idx} value={opt}>{opt}</option>
          ))}
          <option value="custom">+ Add Custom {label}</option>
        </select>
      </>
    ) : (
      <>
        <input 
          type={type}
          step={step}
          className="form-control"
          value={formData[field] || ''}
          onChange={(e) => handleChange(field, e.target.value)}
          placeholder={`Enter custom ${label.toLowerCase()} (click to go back)`}
          onClick={() => {
            const newCustom = { ...customFields };
            delete newCustom[field];
            handleChange(field, '');
          }}
          required={required}
        />
      </>
    )}
  </div>
);

window.SelectOrCustom = SelectOrCustom;