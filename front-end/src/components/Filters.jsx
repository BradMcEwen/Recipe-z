import React, { useState } from 'react';

const Filters = ({ onFilterChange }) => {
  const [selectedCourse, setSelectedCourse] = useState('');
  const [selectedMethod, setSelectedMethod] = useState('');
  const [selectedType, setSelectedType] = useState('');
  const [specificIngredient, setSpecificIngredient] = useState('');

  const handleCourseChange = (event) => {
    setSelectedCourse(event.target.value);
    onFilterChange({ type: 'course', value: event.target.value });
  };

  const handleMethodChange = (event) => {
    setSelectedMethod(event.target.value);
    onFilterChange({ type: 'method', value: event.target.value });
  };

  const handleTypeChange = (event) => {
    setSelectedType(event.target.value);
    onFilterChange({ type: 'type', value: event.target.value });
  };

  const handleIngredientChange = (event) => {
    setSpecificIngredient(event.target.value);
    onFilterChange({ type: 'ingredient', value: event.target.value });
  };

  return (
    <div className="filters">
      <h3>Filters</h3>
      <div>
        <h4>Course</h4>
        <select value={selectedCourse} onChange={handleCourseChange}>
          <option value="">All</option>
          <option value="breakfast">Breakfast</option>
          <option value="lunch">Lunch</option>
          <option value="dinner">Dinner</option>
          <option value="dessert">Dessert</option>
        </select>
      </div>
      <div>
        <h4>Cooking Method</h4>
        <select value={selectedMethod} onChange={handleMethodChange}>
          <option value="">All</option>
          <option value="bake">Bake</option>
          <option value="fry">Fry</option>
          <option value="crockpot">Crockpot</option>
          <option value="grill">Grill</option>
          <option value="stovetop">Stovetop</option>
          <option value="smoker">Smoker</option>
          <option value="instant pot">Instant Pot</option>
        </select>
      </div>
      <div>
        <h4>Type of Dish</h4>
        <select value={selectedType} onChange={handleTypeChange}>
          <option value="">All</option>
          <option value="chicken">Chicken</option>
          <option value="beef">Beef</option>
          <option value="vegetarian">Vegetarian</option>
          <option value="fish">Fish</option>
          <option value="pasta">Pasta</option>
        </select>
      </div>
      <div>
        <h4>Specific Ingredients</h4>
        <input
          type="text"
          placeholder="Enter ingredients"
          value={specificIngredient}
          onChange={handleIngredientChange}
        />
      </div>
    </div>
  );
};

export default Filters;
