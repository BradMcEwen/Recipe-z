import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { addRecipe } from '../redux/slices/recipeSlice';
import { useNavigate } from 'react-router-dom';

const AddRecipe = () => {
  const [form, setForm] = useState({
    image: '',
    title: '',
    ingredients: '',
    steps: '',
  });
  const dispatch = useDispatch();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Assuming the image is a URL for simplicity
    dispatch(addRecipe({ ...form, id: Date.now() }));
    navigate('/');
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        name="image"
        placeholder="Image URL"
        value={form.image}
        onChange={handleChange}
        required
      />
      <input
        type="text"
        name="title"
        placeholder="Recipe Title"
        value={form.title}
        onChange={handleChange}
        required
      />
      <textarea
        name="ingredients"
        placeholder="Ingredients"
        value={form.ingredients}
        onChange={handleChange}
        required
      />
      <textarea
        name="steps"
        placeholder="Steps"
        value={form.steps}
        onChange={handleChange}
        required
      />
      <button type="submit">Submit</button>
    </form>
  );
};

export default AddRecipe;
