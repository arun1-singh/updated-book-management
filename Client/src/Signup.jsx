import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate, Link } from 'react-router-dom';

const Signup = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    axios.post('http://localhost:5001/signup', { username, password })
      .then(() => {
        setSuccess('Signup successful — please login');
        // small delay so user can see success message, then redirect to login
        setTimeout(() => navigate('/login'), 800);
      })
      .catch(err => {
        setError(err.response?.data?.error || 'Signup failed');
      });
  };

  return (
    <div className='d-flex align-items-center flex-column mt-3'>
      <h2>Sign Up</h2>
      <form onSubmit={handleSubmit} className='w-25'>
        {error && <div className='alert alert-danger'>{error}</div>}
        {success && <div className='alert alert-success'>{success}</div>}
        <div className='mb-3'>
          <label className='form-label'>Username</label>
          <input className='form-control' value={username} onChange={e => setUsername(e.target.value)} />
        </div>
        <div className='mb-3'>
          <label className='form-label'>Password</label>
          <input type='password' className='form-control' value={password} onChange={e => setPassword(e.target.value)} />
        </div>
        <button className='btn btn-primary' type='submit'>Sign Up</button>
        <div className='mt-3'>
          Already have an account? <Link to='/login'>Login</Link>
        </div>
      </form>
    </div>
  );
};

export default Signup;
