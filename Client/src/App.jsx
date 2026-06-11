import { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Books from './Books';
import CreateBook from './CreateBook';
import UpdateBook from './UpdateBook';
import Nav from './Nav';
import Login from './Login';
import Signup from './Signup';
import axios from 'axios';

const getStoredToken = () => localStorage.getItem('access_token');

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(!!getStoredToken());

  useEffect(() => {
    const token = getStoredToken();
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      setIsAuthenticated(true);
    } else {
      delete axios.defaults.headers.common['Authorization'];
      setIsAuthenticated(false);
    }
  }, []);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
  };

  return (
    <BrowserRouter>
      <Nav onLogout={handleLogout} />
      <Routes>
        <Route path='/login' element={<Login onLogin={handleLogin} />} />
        <Route path='/signup' element={<Signup />} />
        <Route path='/' element={isAuthenticated ? <Books /> : <Navigate to='/login' />} />
        <Route path='/create' element={isAuthenticated ? <CreateBook /> : <Navigate to='/login' />} />
        <Route path='/update' element={isAuthenticated ? <UpdateBook /> : <Navigate to='/login' />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;