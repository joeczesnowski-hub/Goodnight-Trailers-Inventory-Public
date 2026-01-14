const ClassicCarsForm = ({ formData, options, customFields, handleChange, handleSelectChange }) => {
  return (
    <div className="row g-3">
      <div className="col-md-6">
        <label className="form-label fw-bold">Year</label>
        <select 
          className="form-select"
          value={formData.year || ''}
          onChange={(e) => handleChange('year', e.target.value)}
        >
          <option value="">Select Year</option>
          {options.years?.map(year => (
            <option key={year} value={year}>{year}</option>
          ))}
        </select>
      </div>

      <div className="col-md-6">
        <SelectOrCustom 
          field="make"
          label="Make"
          optionsList={options.makes}
          required={true}
          formData={formData}
          customFields={customFields}
          handleChange={handleChange}
          handleSelectChange={handleSelectChange}
        />
      </div>

      <div className="col-md-6">
        <SelectOrCustom 
          field="model"
          label="Model"
          optionsList={options.models}
          required={true}
          formData={formData}
          customFields={customFields}
          handleChange={handleChange}
          handleSelectChange={handleSelectChange}
        />
      </div>

      <div className="col-md-6">
        <label className="form-label fw-bold">Mileage</label>
        <input 
          type="number"
          className="form-control"
          value={formData.mileage || ''}
          onChange={(e) => handleChange('mileage', e.target.value)}
        />
      </div>

      <div className="col-md-6">
        <label className="form-label fw-bold">Engine Specs</label>
        <input 
          type="text"
          className="form-control"
          value={formData.engine_specs || ''}
          onChange={(e) => handleChange('engine_specs', e.target.value)}
          placeholder="e.g., V8 350ci"
        />
      </div>

      <div className="col-md-6">
        <SelectOrCustom 
          field="transmission"
          label="Transmission"
          optionsList={options.transmissions}
          formData={formData}
          customFields={customFields}
          handleChange={handleChange}
          handleSelectChange={handleSelectChange}
        />
      </div>

      <div className="col-md-6">
        <label className="form-label fw-bold">VIN <span className="text-danger">*</span></label>
        <input 
          type="text"
          className="form-control"
          value={formData.vin || ''}
          onChange={(e) => handleChange('vin', e.target.value)}
          required
        />
      </div>

      <div className="col-md-6">
        <SelectOrCustom 
          field="restoration_status"
          label="Restoration Status"
          optionsList={options.restoration_statuses}
          formData={formData}
          customFields={customFields}
          handleChange={handleChange}
          handleSelectChange={handleSelectChange}
        />
      </div>

      <div className="col-md-6">
        <SelectOrCustom 
          field="condition"
          label="Condition"
          optionsList={options.conditions}
          formData={formData}
          customFields={customFields}
          handleChange={handleChange}
          handleSelectChange={handleSelectChange}
        />
      </div>

      <div className="col-md-6">
        <SelectOrCustom 
          field="color"
          label="Color"
          optionsList={options.colors}
          formData={formData}
          customFields={customFields}
          handleChange={handleChange}
          handleSelectChange={handleSelectChange}
        />
      </div>

      <div className="col-12">
        <label className="form-label fw-bold">Description</label>
        <textarea 
          className="form-control"
          rows="4"
          value={formData.description || ''}
          onChange={(e) => handleChange('description', e.target.value)}
          placeholder="Enter detailed description..."
        />
      </div>
    </div>
  );
};

window.ClassicCarsForm = ClassicCarsForm;