import React, { useEffect, useState } from 'react';
import "./Header.scss";
import Navbar from "./Navbar";
import SearchForm from "./SearchForm";
import axios from 'axios';

const Header = () => {
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    // Fetch categories from the API
    const fetchCategories = async () => {
      try {
        const response = await axios.get('https://www.themealdb.com/api/json/v1/1/categories.php');
        setCategories(response.data.categories);
      } catch (error) {
        console.error("Error fetching categories:", error);
      }
    };

    fetchCategories();
  }, []);

  return (
    <header className='header'>
      <Navbar />
      <div className='header-content flex align-center justify-center flex-column text-center'>
        <h1 className='text-white header-title ls-2'>Welcome to Recipe-Z</h1>
        <p className='text-uppercase text-white my-3 ls-1'>Discover Your Perfect Recipes with Advanced Filters!</p>
        {/* Pass the categories to SearchForm */}
        <SearchForm categories={categories} />
      </div>
    </header>
  )
}

export default Header;
