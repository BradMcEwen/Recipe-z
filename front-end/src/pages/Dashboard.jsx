import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { setRecipes } from '../redux/slices/recipeSlice';
import RecipeCard from '../components/RecipeCard';
import Filters from '../components/Filters';

const Dashboard = () => {
  const dispatch = useDispatch();
  const recipes = useSelector((state) => state.recipes.recipes);
  const handleFilterChange = (filter) => {
    console.log(filter); // Handle filter logic here
    // Implement the filtering logic based on the selected filters
  };

  useEffect(() => {
    // Fetch recipes and set them in state
    fetch('/api/recipes') // Replace with your API endpoint
      .then((res) => res.json())
      .then((data) => dispatch(setRecipes(data)));
  }, [dispatch]);

  return (
    <div className="dashboard">
      <div className="filter">
      <Filters onFilterChange={handleFilterChange} />
      </div>
      <div className="recipe-cards">
        {recipes.map((recipe) => (
          <RecipeCard key={recipe.id} recipe={recipe} />
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
