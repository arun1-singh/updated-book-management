import React from 'react'
import 'bootstrap/dist/css/bootstrap.min.css'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'

const Nav = ({ onLogout }) => {
  const navigate = useNavigate();
  const token = localStorage.getItem('access_token');

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    delete axios.defaults.headers.common['Authorization'];
    if (onLogout) {
      onLogout();
    }
    navigate('/login');
  }

  return (
    <div className='d-flex justify-content-between align-items-center px-3 py-2 shadow-sm'>
      <div className='fs-4 fw-bold'>Book Management System</div>
      <div>
        {token ? (
          <button className='btn btn-outline-secondary' onClick={handleLogout}>Logout</button>
        ) : (
          <>
            <button className='btn btn-outline-secondary me-2' onClick={() => navigate('/signup')}>Signup</button>
            <button className='btn btn-primary' onClick={() => navigate('/login')}>Login</button>
          </>
        )}
      </div>
    </div>
  )
}

export default Nav