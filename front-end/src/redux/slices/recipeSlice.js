import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  recipes: [],
  savedRecipes: [],
};

const recipesSlice = createSlice({
  name: 'recipes',
  initialState,
  reducers: {
    setRecipes(state, action) {
      state.recipes = action.payload;
    },
    addRecipe(state, action) {
      state.recipes.push(action.payload);
    },
    saveRecipe(state, action) {
      state.savedRecipes.push(action.payload);
    },
  },
});

export const { setRecipes, addRecipe, saveRecipe } = recipesSlice.actions;

export default recipesSlice.reducer;
