import React from 'react';
import { NavLink } from 'react-router-dom';

const Navbar = () => {
  return (
    <nav>
      <NavLink to="/">Dashboard</NavLink>
      <NavLink to="/add-recipe">Add Recipe</NavLink>
      <NavLink to="/profile">Profile</NavLink>
    </nav>
  );
};

export default Navbar;
