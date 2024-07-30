import React from 'react';
import { useParams } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import { saveRecipe } from '../redux/slices/recipeSlice';

const RecipeDetails = () => {
  const { id } = useParams();
  const dispatch = useDispatch();
  const recipe = useSelector((state) =>
    state.recipes.recipes.find((r) => r.id === parseInt(id))
  );

  const handleSaveRecipe = () => {
    dispatch(saveRecipe(recipe));
  };

  if (!recipe) return <p>Recipe not found</p>;

  return (
    <div className="recipe-details">
      <img src={recipe.image} alt={recipe.title} />
      <h2>{recipe.title}</h2>
      <p>{recipe.description}</p>
      <button onClick={handleSaveRecipe}>Add to Cookbook</button>
    </div>
  );
};

export default RecipeDetails;