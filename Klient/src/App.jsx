import React, { useState, useEffect, createContext, useContext } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';
import './App.css';


const AppContext = createContext();


const api = axios.create({ baseURL: 'http://localhost:8000' });

function App() {
  const [loading, setLoading] = useState(false); 
  const [toast, setToast] = useState(null); 

  
  const showToast = (msg, isError) => {
    setToast({ msg, isError });
    setTimeout(() => setToast(null), 3000);
  };


  useEffect(() => {
    const reqInt = api.interceptors.request.use(config => {
      setLoading(true);
      return config;
    });
    const resInt = api.interceptors.response.use(
      res => { setLoading(false); return res; },
      err => { setLoading(false); return Promise.reject(err); }
    );
    return () => {
      api.interceptors.request.eject(reqInt);
      api.interceptors.response.eject(resInt);
    };
  }, []);

  return (
    <AppContext.Provider value={{ showToast }}>
      
      {loading && <div className="loader-overlay">wczytywanie...</div>}
      
      
      {toast && (
        <div className={`toast ${toast.isError ? 'toast-red' : 'toast-green'}`}>
          {toast.isError ? "Wystąpił błąd" : "Poprawnie zapisano zmiany"}
        </div>
      )}

      <BrowserRouter>
        <div style={{ padding: 20 }}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/add" element={<CarForm />} />
            <Route path="/edit/:id" element={<CarForm />} />
          </Routes>
        </div>
      </BrowserRouter>
    </AppContext.Provider>
  );
}


function Home() {
  const [cars, setCars] = useState([]);
  const [filter, setFilter] = useState("all"); 
  const [deleteId, setDeleteId] = useState(null); 
  const { showToast } = useContext(AppContext);


  const fetchCars = () => {
    api.get(`/cars/?filter_type=${filter}`)
      .then(res => setCars(res.data))
      .catch(() => showToast("Błąd pobierania", true));
  };

  useEffect(() => {
    fetchCars();
  }, [filter]); 

  const handleDeleteConfirm = () => {
    api.delete(`/cars/${deleteId}`)
      .then(() => {
        showToast("Usunięto", false); 
        setDeleteId(null);
        fetchCars();
      })
      .catch(() => {
        showToast("Błąd usuwania", true);
        setDeleteId(null);
      });
  };

  return (
    <div>
      <h1>Lista Samochodów</h1>
      <Link to="/add"><button>Dodaj</button></Link>
      
  
      <div style={{ margin: '10px 0' }}>
        Filtrowanie: 
        <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="all">Wszystkie (True/False)</option>
          <option value="true">Tylko na chodzie (True)</option>
          <option value="false">Tylko nie na chodzie (False)</option>
        </select>
      </div>


      <div className="grid-container">
        {cars.map(car => (
          <div key={car.id} className="kafelek">
            <h3>{car.marka_model}</h3>
            <p>Rok: {car.rok_produkcji}</p>
            <p>Na chodzie: {car.czy_na_chodzie ? "Tak" : "Nie"}</p>
            
       
            <Link to={`/edit/${car.id}`}><button>Edytuj</button></Link>
       
            <button onClick={() => setDeleteId(car.id)}>Usuń</button>
          </div>
        ))}
      </div>


      {deleteId && (
        <div className="modal-overlay">
          <div className="modal-content">
            <p>Czy na pewno chcesz usunąć ten rekord?</p>
            <button onClick={handleDeleteConfirm}>Potwierdź</button>
            <button onClick={() => setDeleteId(null)}>Anuluj</button>
          </div>
        </div>
      )}
    </div>
  );
}


function CarForm() {
  const { id } = useParams(); 
  const navigate = useNavigate();
  const { showToast } = useContext(AppContext);
  
  const [form, setForm] = useState({ marka_model: "", rok_produkcji: 2000, czy_na_chodzie: true });
  const [errorMsg, setErrorMsg] = useState(null);


  useEffect(() => {
    if (id) {
      api.get(`/cars/${id}`).then(res => setForm(res.data));
    }
  }, [id]);

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMsg(null);
    
    const request = id 
      ? api.put(`/cars/${id}`, form) 
      : api.post('/cars/', form);

    request
      .then(() => {
        showToast("Zapisano", false); 
        navigate('/'); 
      })
      .catch(err => {
        showToast("Błąd", true); 
      
        if (err.response && err.response.data) {
            setErrorMsg(err.response.data.detail);
        }
      });
  };

  return (
    <div>
      <h2>{id ? "Edycja" : "Dodawanie"}</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Marka/Model (Tekst): </label>
          <input 
            type="text" 
            value={form.marka_model} 
            onChange={e => setForm({...form, marka_model: e.target.value})} 
            required 
          />
        </div>
        <div>
          <label>Rok (Liczba): </label>
          <input 
            type="number" 
            value={form.rok_produkcji} 
            onChange={e => setForm({...form, rok_produkcji: Number(e.target.value)})} 
            required 
          />
        </div>
        <div>
          <label>Na chodzie (Boolean): </label>
          <input 
            type="checkbox" 
            checked={form.czy_na_chodzie} 
            onChange={e => setForm({...form, czy_na_chodzie: e.target.checked})} 
          />
        </div>
        
        {errorMsg && <div style={{ color: 'red' }}>Błąd API: {errorMsg}</div>}

        <button type="submit">Zapisz</button>
      </form>
    </div>
  );
}

export default App;