import React, { useState } from 'react';
import "./Header.scss";
import { BsSearch } from "react-icons/bs";
import { useMealContext } from '../../context/mealContext';
import { useNavigate } from 'react-router-dom';
import { startFetchMealsBySearch } from '../../actions/mealsActions';
import { Modal, Button, Form } from 'react-bootstrap';

const SearchForm = ({ categories }) => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedCategories, setSelectedCategories] = useState([]);
  const { dispatch } = useMealContext();
  const [showModal, setShowModal] = useState(false);

  const handleSearchTermChange = (e) => {
    setSearchTerm(e.target.value);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    navigate("/");
    startFetchMealsBySearch(dispatch, searchTerm, selectedCategories);
    closeModal();
  };

  const handleCategoryChange = (category) => {
    setSelectedCategories((prevCategories) =>
      prevCategories.includes(category)
        ? prevCategories.filter((c) => c !== category)
        : [...prevCategories, category]
    );
  };

  const openModal = () => {
    setShowModal(true);
    document.body.style.overflow = 'hidden'; // Prevent background scrolling
  };

  const closeModal = () => {
    setShowModal(false);
    document.body.style.overflow = 'auto'; // Allow background scrolling
  };

  return (
    <>
      <form className='search-form flex align-center' onClick={openModal}>
        <input
          type="text"
          className='form-control-input text-dark-gray fs-15'
          placeholder='Search recipes here ...'
          value={searchTerm}
          onChange={handleSearchTermChange}
          readOnly // Makes the input readonly to trigger modal on click
        />
        <button
          type="button"
          className='form-submit-btn text-white text-uppercase fs-14'
          onClick={openModal}
        >
          <BsSearch className='btn-icon' size={20} />
        </button>
      </form>

      <Modal show={showModal} onHide={closeModal} centered backdropClassName="custom-backdrop">
        <Modal.Header closeButton>
          <Modal.Title>Advanced Search</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form className="advanced-search-form">
            <Form.Group controlId="formCategories">
              <Form.Label>Select Course Options</Form.Label>
              <div className="options-group">
                {['Breakfast', 'Lunch', 'Dinner', 'Dessert'].map(option => (
                  <span
                    key={option}
                    className={`filter-option-bubble ${selectedCategories.includes(option) ? 'active' : ''}`}
                    onClick={() => handleCategoryChange(option)}
                  >
                    {option}
                  </span>
                ))}
              </div>

              <Form.Label>Select Meal Types</Form.Label>
              <div className="options-group">
                {['Chicken', 'Beef', 'Seafood', 'Vegan', 'Vegetarian', 'Pork', 'Lamb', 'Pasta'].map(option => (
                  <span
                    key={option}
                    className={`filter-option-bubble ${selectedCategories.includes(option) ? 'active' : ''}`}
                    onClick={() => handleCategoryChange(option)}
                  >
                    {option}
                  </span>
                ))}
              </div>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={closeModal}>
            Close
          </Button>
          <Button variant="primary" onClick={handleSearch}>
            Apply Filters
          </Button>
        </Modal.Footer>
      </Modal>
    </>
  );
};

export default SearchForm;
