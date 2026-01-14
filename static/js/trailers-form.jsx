const TrailersForm = ({ formData, options, customFields, handleChange, handleSelectChange }) => {
  return (
    <div className="row g-3">
      <div className="col-md-6">
        <SelectOrCustom 
          field="length"
          label="Length (ft)"
          optionsList={options.lengths}
          required={true}
          type="number"
          step="0.1"
          formData={formData}
          customFields={customFields}
          handleChange={handleChange}
          handleSelectChange={handleSelectChange}
        />
      </div>

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
          field="type"
          label="Type"
          optionsList={options.types}
          required={true}
          formData={formData}
          customFields={customFields}
          handleChange={handleChange}
          handleSelectChange={handleSelectChange}
        />
      </div>

      <div className="col-md-6">
        <SelectOrCustom 
          field="dimensions"
          label="Width"
          optionsList={options.dimensions}
          formData={formData}
          customFields={customFields}
          handleChange={handleChange}
          handleSelectChange={handleSelectChange}
        />
      </div>

      <div className="col-md-6">
        <SelectOrCustom 
          field="capacity"
          label="Capacity"
          optionsList={options.capacities}
          formData={formData}
          customFields={customFields}
          handleChange={handleChange}
          handleSelectChange={handleSelectChange}
        />
      </div>

      <div className="col-md-6">
        <SelectOrCustom 
          field="hitch_type"
          label="Hitch Type"
          optionsList={options.hitch_types}
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

window.TrailersForm = TrailersForm;