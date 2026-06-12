// Books.js
import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import axios from 'axios';

const Books = () => {
    const [books, setBooks] = useState([]);
    const navigate = useNavigate();

    const handleUpdate = (book) => {
        navigate('/update', { state: { book } });
    };

    const handleDelete = (bookId) => {
        axios.delete(`http://localhost:5001/delete/${bookId}`)
            .then(() => {
                // Remove from state only after backend confirms deletion
                setBooks(prev => prev.filter(book => String(book.id) !== String(bookId)));
            })
            .catch(err => {
                console.error('Delete failed:', err);
            });
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
            .catch(err => {
                console.error('Backend fetch failed:', err);
            });
    }, []);

    return (
        <div className="container py-3">
            <div className="d-flex justify-content-between align-items-center mb-3">
                <h3>Books</h3>
                <Link to="/create" className="btn btn-success">Create Link</Link>
            </div>

            <table className="table">
                <thead>
                    <tr>
                        <th scope='col'>Publisher</th>
                        <th scope='col'>Book</th>
                        <th scope='col'>Date</th>
                        <th scope='col'>cost</th>
                        <th scope='col'>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {books.length > 0 ? (
                        books.map(book => (
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
                        ))
                    ) : (
                        <tr>
                            <td colSpan={5} className="text-center">No records</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}

export default Books;
