import React from 'react';
import { useSelector } from 'react-redux';
import RecipeCard from '../components/RecipeCard';

const Profile = () => {
  const savedRecipes = useSelector((state) => state.recipes.savedRecipes);

  return (
    <div className="profile">
      <h2>Your Cookbook</h2>
      <div className="recipe-cards">
        {savedRecipes.map((recipe) => (
          <RecipeCard key={recipe.id} recipe={recipe} />
        ))}
      </div>
    </div>
  );
};

export default Profile;
