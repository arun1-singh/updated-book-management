// Books.js
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Link } from 'react-router-dom';

const Books = () => {
    const [books, setBooks] = useState([]);
    const navigate = useNavigate();

    const handleUpdate = (book) => {
        navigate('/update', { state: { book } });
    };

    const handleDelete = (bookId) => {
        axios.delete(`http://localhost:5001/delete/${bookId}`)
            .then(() => {
                setBooks(books.filter(book => book.id !== bookId));
            })
            .catch(err => console.log(err));
    };

    useEffect(() => {
        axios.get('http://localhost:5001')
            .then(res => {
                if (Array.isArray(res.data)) {
                    setBooks(res.data);
                } else {
                    console.error('Expected an array but got:', res.data);
                }
            })
            .catch(err => console.log(err));
    }, []);

    return (
        <div className='container'>
            <Link to='/create' className='btn btn-success'>Create Link</Link>
            {books.length !== 0 ?
                <table className="table">
                    <thead>
                        <tr>
                            <th scope='col'>Publisher</th>
                            <th scope='col'>Book</th>
                            <th scope='col'>Date</th>
                            <th scope='col'>Cost</th>
                            <th scope='col'>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {books.map(book =>
                            <tr key={book.id}>
                                <td>{book.publisher}</td>
                                <td>{book.name}</td>
                                <td>{book.date}</td>
                                <td>{book.cost}</td>
                                <td>
                                    <button className="btn btn-primary" onClick={() => handleUpdate(book)}>
                                        Update
                                    </button>
                                    <button className="btn btn-danger ms-2" onClick={() => handleDelete(book.id)}>
                                        Delete
                                    </button>
                                </td>
                            </tr>
                        )}
                    </tbody>
                </table>
                : <h2>No records</h2>
            }
        </div>
    );
}

export default Books;
