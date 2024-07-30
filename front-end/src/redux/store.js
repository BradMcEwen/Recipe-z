import { configureStore } from '@reduxjs/toolkit';
import recipesReducer from './slices/recipeSlice';
import userReducer from './slices/userSlice';

export const store = configureStore({
  reducer: {
    recipes: recipesReducer,
    user: userReducer,
  },
});
