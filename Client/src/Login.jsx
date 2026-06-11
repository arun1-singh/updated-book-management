import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

const Login = ({ onLogin }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    axios.post('http://localhost:5001/login', { username, password })
      .then(res => {
        const token = res.data.access_token;
        localStorage.setItem('access_token', token);
        // set default axios header for subsequent requests
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        if (onLogin) {
          onLogin();
        }
        navigate('/');
      })
      .catch(err => {
        setError(err.response?.data?.error || 'Login failed');
      });
  };

  return (
    <div className='d-flex align-items-center flex-column mt-3'>
      <h2>Login</h2>
      <form onSubmit={handleSubmit} className='w-25'>
        {error && <div className='alert alert-danger'>{error}</div>}
        <div className='mb-3'>
          <label className='form-label'>Username</label>
          <input className='form-control' value={username} onChange={e => setUsername(e.target.value)} />
        </div>
        <div className='mb-3'>
          <label className='form-label'>Password</label>
          <input type='password' className='form-control' value={password} onChange={e => setPassword(e.target.value)} />
        </div>
        <button className='btn btn-primary' type='submit'>Login</button>
        <div className='mt-3'>
          Don't have an account? <Link to='/signup'>Sign up</Link>
        </div>
      </form>
    </div>
  );
};

export default Login;