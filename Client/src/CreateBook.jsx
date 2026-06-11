import axios from 'axios'//core react library for building user interface
import React, {useState} from 'react'//for making requests to your backend server
import { useNavigate } from 'react-router-dom' // useNavigate use to navigate to different routes

const CreateBook = () => { // defined the functional component named createbook
    const [ values, setValues] = useState({
        publisher:"",
        name:"",
        date:'',
        cost:''
    })
    const navigate = useNavigate() // navigate to the home page
    const handleSubmit= (e) =>{    // event handler to handle form submission
        e.preventDefault()        // prevent default form submission
        axios.post('http://localhost:5001/create', values) // sends the post request to the server
        .then(res => navigate('/'))                        // on successful response user will be navigated to the home page 
        .catch(err => console.log(err))                    //logs error occur during request
    }
    return ( // div container contain flexbox classes to centring content
        <div className='d-flex align-items-center flex-column mt-3'> 
            <h2>Add a Book</h2>
            <form className='wt-50' onSubmit={handleSubmit}>
                <div class="mb-3 mt-3">
                    <label htmlFor="Publisher" 
                    class="form-label">Publisher
                    </label>
                    <input type="text" 
                    class="form-control"  
                    placeholder="Enter Publisher name" 
                    name="publisher" 
                    onChange={(e)=> setValues({...values, publisher: e.target.value})}
                    />
                </div>
                <div class="mb-3">
                    <label htmlFor="Book name" 
                    class="form-label">Book name:
                    </label>
                    <input type="text" 
                    class="form-control" 
                    placeholder="Enter Book name" 
                    name="name" 
                    onChange={(e)=> setValues({...values, name: e.target.value})}
                    />
                </div>
                <div class="mb-3">
                    <label htmlFor="Publish date" 
                    class="form-label">Publish Date:
                    </label>
                    <input type="date" 
                     class="form-control"
                    name="name" 
                    onChange={(e)=> setValues({...values, date: e.target.value})}
                    />
                </div>
                <div class="mb-3">
                    <label htmlFor="cost" 
                    class="form-label">Cost:
                    </label>
                    <input type="text" 
                     class="form-control"
                    name="cost" 
                    onChange={(e)=> setValues({...values, cost: e.target.value})}
                    />
                </div>
                <button type="submit" class="btn btn-primary">Submit</button>
            </form>
        </div>
    )
}

export default CreateBook
