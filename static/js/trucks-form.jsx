const TrucksForm = ({ formData, options, customFields, handleChange, handleSelectChange }) => {
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
        <SelectOrCustom 
          field="truck_type"
          label="Truck Type"
          optionsList={options.truck_types}
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
          placeholder="Odometer reading"
        />
      </div>
      
      <div className="col-md-6">
        <SelectOrCustom 
          field="engine_type"
          label="Engine Type"
          optionsList={options.engine_types}
          formData={formData}
          customFields={customFields}
          handleChange={handleChange}
          handleSelectChange={handleSelectChange}
        />
      </div>
      
      <div className="col-md-6">
        <label className="form-label fw-bold">Hours</label>
        <input 
          type="number"
          className="form-control"
          value={formData.hours || ''}
          onChange={(e) => handleChange('hours', e.target.value)}
          placeholder="Engine hours"
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
          field="condition"
          label="Condition"
          optionsList={options.conditions}
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
window.TrucksForm = TrucksForm;