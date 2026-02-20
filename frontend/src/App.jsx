import { BrowserRouter, Routes, Route, Navigate, useNavigate, Link } from 'react-router-dom';
import { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'http://localhost:8080';
const AppContext = createContext();

const api = axios.create({
  baseURL: API_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add CSRF token to requests
api.interceptors.request.use((config) => {
  const csrfToken = document.cookie.match(/csrftoken=([\w-]+)/);
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken[1];
  }
  return config;
});

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const res = await api.get('/api/user/');
      setUser(res.data);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const res = await api.post('/api/login/', { username, password });
      await checkAuth();
      return res.data;
    } catch (err) {
      throw new Error(err.response?.data?.error || 'Invalid credentials');
    }
  };

  const logout = async () => {
    try {
      await api.post('/api/logout/');
    } catch {}
    setUser(null);
  };

  if (loading) {
    return <div className="loading-screen"><div className="loader"></div></div>;
  }

  return (
    <AppContext.Provider value={{ user, setUser, login, logout, api }}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={!user ? <Login /> : <Navigate to="/" />} />
          <Route path="/register" element={!user ? <Register /> : <Navigate to="/" />} />
          <Route path="/*" element={user?.is_staff ? <AdminLayout /> : (user ? <StudentLayout /> : <Navigate to="/login" />)} />
        </Routes>
      </BrowserRouter>
    </AppContext.Provider>
  );
}

function AdminLayout() {
  const { user, logout } = useContext(AppContext);
  const navigate = useNavigate();
  
  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };
  
  return (
    <div className="app-layout">
      <nav className="sidebar">
        <div className="logo">
          <svg className="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          <span className="logo-text">ExamPro</span>
        </div>
        <div className="nav-links">
          <NavLink to="/" label="Dashboard" />
          <NavLink to="/admin/students" label="Manage Students" />
          <NavLink to="/admin/exams" label="Manage Exams" />
          <NavLink to="/admin/questions" label="Manage Questions" />
        </div>
        <div className="user-section">
          <div className="user-info">
            <div className="avatar">{user?.username?.[0]?.toUpperCase()}</div>
            <div className="user-details">
              <span className="username">{user?.username}</span>
              <span className="role">Admin</span>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </nav>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<AdminDashboard />} />
          <Route path="/admin/students" element={<AdminStudents />} />
          <Route path="/admin/exams" element={<AdminExams />} />
          <Route path="/admin/questions" element={<AdminQuestions />} />
        </Routes>
      </main>
    </div>
  );
}

function StudentLayout() {
  const { user, logout } = useContext(AppContext);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <div className="app-layout">
      <nav className="sidebar">
        <div className="logo">
          <svg className="logo-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
            <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
          </svg>
          <span className="logo-text">ExamPro</span>
        </div>
        <div className="nav-links">
          <NavLink to="/" label="Dashboard" />
          <NavLink to="/practice" label="Practice Tests" />
          <NavLink to="/worksheets" label="Worksheets" />
          <NavLink to="/materials" label="Study Materials" />
          <NavLink to="/progress" label="My Progress" />
          <NavLink to="/bookmarks" label="Bookmarks" />
        </div>
        <div className="user-section">
          <div className="user-info">
            <div className="avatar">{user?.username?.[0]?.toUpperCase()}</div>
            <div className="user-details">
              <span className="username">{user?.username}</span>
              <span className="role">{user?.is_staff ? 'Admin' : 'Student'}</span>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </nav>
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/exam/:id" element={<ExamStart />} />
          <Route path="/exam/:id/take" element={<ExamTake />} />
          <Route path="/practice" element={<PracticeTests />} />
          <Route path="/practice/:id" element={<PracticeTestStart />} />
          <Route path="/worksheets" element={<Worksheets />} />
          <Route path="/worksheets/:id" element={<WorksheetStart />} />
          <Route path="/materials" element={<StudyMaterials />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/bookmarks" element={<Bookmarks />} />
        </Routes>
      </main>
    </div>
  );
}

function NavLink({ to, label }) {
  return (
    <Link to={to} className="nav-link">
      <span className="nav-label">{label}</span>
    </Link>
  );
}

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useContext(AppContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Welcome Back</h1>
          <p>Sign in to continue to ExamPro</p>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}
          <div className="form-group">
            <label>Username</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
            />
          </div>
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              required
            />
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        <p className="auth-footer">
          Don't have an account? <Link to="/register">Register</Link>
        </p>
      </div>
    </div>
  );
}

function Register() {
  const [formData, setFormData] = useState({
    username: '', email: '', password: '', confirm_password: '',
    first_name: '', last_name: '', student_id: '', department: ''
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/register/', formData);
      navigate('/login');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card register-card">
        <div className="auth-header">
          <h1>Create Account</h1>
          <p>Join ExamPro today</p>
        </div>
        <form onSubmit={handleSubmit} className="auth-form">
          {error && <div className="error-message">{error}</div>}
          <div className="form-row">
            <div className="form-group">
              <label>First Name</label>
              <input type="text" name="first_name" value={formData.first_name} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Last Name</label>
              <input type="text" name="last_name" value={formData.last_name} onChange={handleChange} required />
            </div>
          </div>
          <div className="form-group">
            <label>Username</label>
            <input type="text" name="username" value={formData.username} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Email</label>
            <input type="email" name="email" value={formData.email} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Student ID</label>
            <input type="text" name="student_id" value={formData.student_id} onChange={handleChange} required />
          </div>
          <div className="form-group">
            <label>Department</label>
            <input type="text" name="department" value={formData.department} onChange={handleChange} />
          </div>
          <div className="form-row">
            <div className="form-group">
              <label>Password</label>
              <input type="password" name="password" value={formData.password} onChange={handleChange} required />
            </div>
            <div className="form-group">
              <label>Confirm Password</label>
              <input type="password" name="confirm_password" value={formData.confirm_password} onChange={handleChange} required />
            </div>
          </div>
          <button type="submit" className="btn-primary">Create Account</button>
        </form>
        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign In</Link>
        </p>
      </div>
    </div>
  );
}

function Dashboard() {
  const { api } = useContext(AppContext);
  const [exams, setExams] = useState([]);
  const [results, setResults] = useState([]);
  const [stats, setStats] = useState({ completed: 0, passed: 0, avgScore: 0 });

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const [examsRes, resultsRes] = await Promise.all([
        api.get('/api/exams/'),
        api.get('/api/results/')
      ]);
      setExams(examsRes.data.available || []);
      setResults(resultsRes.data.results || []);
      setStats(resultsRes.data.stats || { completed: 0, passed: 0, avgScore: 0 });
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Dashboard</h1>
        <p>Welcome back! Here's your exam overview.</p>
      </div>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
          </div>
          <div className="stat-info">
            <span className="stat-value">{stats.completed}</span>
            <span className="stat-label">Exams Completed</span>
          </div>
        </div>
        <div className="stat-card success">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
          </div>
          <div className="stat-info">
            <span className="stat-value">{stats.passed}</span>
            <span className="stat-label">Passed</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          </div>
          <div className="stat-info">
            <span className="stat-value">{stats.avgScore}%</span>
            <span className="stat-label">Average Score</span>
          </div>
        </div>
      </div>

      <div className="content-grid">
        <div className="section">
          <h2>Available Exams</h2>
          {exams.length === 0 ? (
            <div className="empty-state">No exams available right now</div>
          ) : (
            <div className="exam-list">
              {exams.map(exam => (
                <div key={exam.id} className="exam-card">
                  <div className="exam-info">
                    <h3>{exam.title}</h3>
                    <p>{exam.description}</p>
                    <div className="exam-meta">
                      <span>{exam.exam_date}</span>
                      <span>{exam.duration_minutes} min</span>
                      <span>{exam.number_of_questions} questions</span>
                    </div>
                  </div>
                  <Link to={`/practice/${exam.id}`} className="btn-primary">Start</Link>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="section">
          <h2>Recent Results</h2>
          {results.length === 0 ? (
            <div className="empty-state">No results yet</div>
          ) : (
            <div className="results-list">
              {results.map(result => (
                <div key={result.id} className="result-card">
                  <div className="result-info">
                    <h4>{result.exam_title}</h4>
                    <span className="result-date">{result.submitted_at}</span>
                  </div>
                  <div className={`result-score ${result.passed ? 'passed' : 'failed'}`}>
                    {result.score}%
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function PracticeTests() {
  const { api } = useContext(AppContext);
  const [tests, setTests] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filter, setFilter] = useState({ category: '', difficulty: '' });

  useEffect(() => {
    loadData();
  }, [filter]);

  const loadData = async () => {
    try {
      const params = new URLSearchParams(filter).toString();
      const [testsRes, catRes] = await Promise.all([
        api.get(`/api/practice/tests/?${params}`),
        api.get('/api/categories/')
      ]);
      setTests(testsRes.data.tests || testsRes.data);
      setCategories(catRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Practice Tests</h1>
        <p>Sharpen your skills with timed practice tests</p>
      </div>

      <div className="filters">
        <select value={filter.category} onChange={(e) => setFilter({ ...filter, category: e.target.value })}>
          <option value="">All Categories</option>
          {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
        </select>
        <select value={filter.difficulty} onChange={(e) => setFilter({ ...filter, difficulty: e.target.value })}>
          <option value="">All Levels</option>
          <option value="easy">Easy</option>
          <option value="medium">Medium</option>
          <option value="hard">Hard</option>
        </select>
      </div>

      <div className="cards-grid">
        {tests.length === 0 ? (
          <div className="empty-state">No practice tests available</div>
        ) : (
          tests.map(test => (
            <div key={test.id} className="content-card">
              <div className="card-header">
                <span className={`difficulty-badge ${test.difficulty}`}>{test.difficulty}</span>
                {test.is_timed && <span className="timed-badge">Timed</span>}
              </div>
              <h3>{test.title}</h3>
              <p>{test.description}</p>
              <div className="card-meta">
                <span>{test.number_of_questions} questions</span>
                {test.time_limit_minutes > 0 && <span>{test.time_limit_minutes} min</span>}
              </div>
              <Link to={`/practice/${test.id}`} className="btn-primary">Start Practice</Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function PracticeTestStart() {
  return <div className="page"><div className="page-header"><h1>Practice Test</h1></div><p>Starting practice test...</p></div>;
}

function Worksheets() {
  const { api } = useContext(AppContext);
  const [worksheets, setWorksheets] = useState([]);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    loadWorksheets();
  }, []);

  const loadWorksheets = async () => {
    try {
      const [wsRes, catRes] = await Promise.all([
        api.get('/api/worksheets/'),
        api.get('/api/categories/')
      ]);
      setWorksheets(wsRes.data.worksheets || wsRes.data);
      setCategories(catRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Worksheets</h1>
        <p>Practice with downloadable worksheets</p>
      </div>

      <div className="cards-grid">
        {worksheets.length === 0 ? (
          <div className="empty-state">No worksheets available</div>
        ) : (
          worksheets.map(ws => (
            <div key={ws.id} className="content-card">
              <div className="card-header">
                <span className={`difficulty-badge ${ws.difficulty}`}>{ws.difficulty}</span>
              </div>
              <h3>{ws.title}</h3>
              <p>{ws.description}</p>
              <div className="card-meta">
                <span>{ws.number_of_questions} questions</span>
                {ws.time_limit_minutes > 0 && <span>{ws.time_limit_minutes} min</span>}
              </div>
              <Link to={`/worksheets/${ws.id}`} className="btn-secondary">View Worksheet</Link>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function WorksheetStart() {
  return <div className="page"><div className="page-header"><h1>Worksheet</h1></div><p>Loading worksheet...</p></div>;
}

function StudyMaterials() {
  const { api } = useContext(AppContext);
  const [materials, setMaterials] = useState([]);
  const [categories, setCategories] = useState([]);
  const [filter, setFilter] = useState({ category: '', type: '' });

  useEffect(() => {
    loadData();
  }, [filter]);

  const loadData = async () => {
    try {
      const params = new URLSearchParams(filter).toString();
      const [matRes, catRes] = await Promise.all([
        api.get(`/api/materials/?${params}`),
        api.get('/api/categories/')
      ]);
      setMaterials(matRes.data.materials || matRes.data);
      setCategories(catRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Study Materials</h1>
        <p>Access notes, videos, and learning resources</p>
      </div>

      <div className="filters">
        <select value={filter.category} onChange={(e) => setFilter({ ...filter, category: e.target.value })}>
          <option value="">All Categories</option>
          {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
        </select>
        <select value={filter.type} onChange={(e) => setFilter({ ...filter, type: e.target.value })}>
          <option value="">All Types</option>
          <option value="notes">Notes</option>
          <option value="video">Video</option>
          <option value="article">Article</option>
          <option value="cheatsheet">Cheat Sheet</option>
        </select>
      </div>

      <div className="cards-grid">
        {materials.length === 0 ? (
          <div className="empty-state">No study materials available</div>
        ) : (
          materials.map(mat => (
            <div key={mat.id} className="content-card">
              <div className="card-header">
                <span className="type-badge">{mat.material_type}</span>
              </div>
              <h3>{mat.title}</h3>
              <p>{mat.description}</p>
              {mat.external_link && (
                <a href={mat.external_link} target="_blank" rel="noopener noreferrer" className="btn-secondary">
                  Open Resource
                </a>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function Progress() {
  const { api } = useContext(AppContext);
  const [progress, setProgress] = useState(null);

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      const res = await api.get('/api/progress/');
      setProgress(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>My Progress</h1>
        <p>Track your learning journey</p>
      </div>
      
      {progress ? (
        <div className="progress-container">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
              </div>
              <div className="stat-info">
                <span className="stat-value">{progress.total_attempted}</span>
                <span className="stat-label">Questions Attempted</span>
              </div>
            </div>
            <div className="stat-card success">
              <div className="stat-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
              </div>
              <div className="stat-info">
                <span className="stat-value">{progress.correct}</span>
                <span className="stat-label">Correct</span>
              </div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
              </div>
              <div className="stat-info">
                <span className="stat-value">{progress.accuracy}%</span>
                <span className="stat-label">Accuracy</span>
              </div>
            </div>
          </div>
        </div>
      ) : (
        <div className="empty-state">Loading progress...</div>
      )}
    </div>
  );
}

function Bookmarks() {
  const { api } = useContext(AppContext);
  const [bookmarks, setBookmarks] = useState([]);

  useEffect(() => {
    loadBookmarks();
  }, []);

  const loadBookmarks = async () => {
    try {
      const res = await api.get('/api/bookmarks/');
      setBookmarks(res.data.bookmarks || res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const removeBookmark = async (questionId) => {
    try {
      await api.post('/api/bookmarks/toggle/', { question_id: questionId });
      setBookmarks(bookmarks.filter(b => b.question_id !== questionId));
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>My Bookmarks</h1>
        <p>Questions you've saved for later</p>
      </div>

      <div className="bookmarks-list">
        {bookmarks.length === 0 ? (
          <div className="empty-state">No bookmarks yet</div>
        ) : (
          bookmarks.map(bm => (
            <div key={bm.id} className="bookmark-card">
              <div className="bookmark-content">
                <p>{bm.question_text}</p>
                <div className="bookmark-options">
                  <span>A: {bm.option1}</span>
                  <span>B: {bm.option2}</span>
                  <span>C: {bm.option3}</span>
                  <span>D: {bm.option4}</span>
                </div>
              </div>
              <button className="btn-remove" onClick={() => removeBookmark(bm.question_id)}>Remove</button>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function AdminDashboard() {
  const { api } = useContext(AppContext);
  const [stats, setStats] = useState({ total_students: 0, total_exams: 0, total_questions: 0, total_results: 0 });
  const [recentResults, setRecentResults] = useState([]);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const res = await api.get('/api/admin/dashboard/');
      setStats(res.data.stats);
      setRecentResults(res.data.recent_results);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Admin Dashboard</h1>
        <p>Manage your exam system</p>
      </div>
      
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          </div>
          <div className="stat-info">
            <span className="stat-value">{stats.total_students}</span>
            <span className="stat-label">Total Students</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
          </div>
          <div className="stat-info">
            <span className="stat-value">{stats.total_exams}</span>
            <span className="stat-label">Total Exams</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          </div>
          <div className="stat-info">
            <span className="stat-value">{stats.total_questions}</span>
            <span className="stat-label">Total Questions</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
          </div>
          <div className="stat-info">
            <span className="stat-value">{stats.total_results}</span>
            <span className="stat-label">Total Results</span>
          </div>
        </div>
      </div>

      <div className="section">
        <h2>Recent Exam Results</h2>
        {recentResults.length === 0 ? (
          <div className="empty-state">No results yet</div>
        ) : (
          <div className="results-list">
            {recentResults.map(result => (
              <div key={result.id} className="result-card">
                <div className="result-info">
                  <h4>{result.exam_title}</h4>
                  <span className="result-date">{result.student_name} - {result.submitted_at}</span>
                </div>
                <div className={`result-score ${result.passed ? 'passed' : 'failed'}`}>
                  {result.score}%
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function AdminStudents() {
  const { api } = useContext(AppContext);
  const [students, setStudents] = useState([]);
  const [editingId, setEditingId] = useState(null);
  const [editForm, setEditForm] = useState({});

  useEffect(() => {
    loadStudents();
  }, []);

  const loadStudents = async () => {
    try {
      const res = await api.get('/api/admin/students/');
      setStudents(res.data.students);
    } catch (err) {
      console.error(err);
    }
  };

  const handleEdit = (student) => {
    setEditingId(student.id);
    setEditForm({
      first_name: student.first_name,
      last_name: student.last_name,
      email: student.email,
      department: student.department,
      is_active: student.is_active,
    });
  };

  const handleSave = async (studentId) => {
    try {
      await api.post(`/api/admin/students/${studentId}/`, editForm);
      setEditingId(null);
      loadStudents();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (studentId) => {
    if (confirm('Are you sure you want to delete this student?')) {
      try {
        await api.delete(`/api/admin/students/${studentId}/`);
        loadStudents();
      } catch (err) {
        console.error(err);
      }
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Manage Students</h1>
        <p>View and edit student accounts</p>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Name</th>
              <th>Email</th>
              <th>Student ID</th>
              <th>Department</th>
              <th>Status</th>
              <th>Joined</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {students.map(student => (
              <tr key={student.id}>
                <td>{student.username}</td>
                <td>
                  {editingId === student.id ? (
                    <input type="text" value={editForm.first_name} onChange={(e) => setEditForm({...editForm, first_name: e.target.value})} placeholder="First" className="input-sm" />
                  ) : (
                    `${student.first_name} ${student.last_name}`
                  )}
                </td>
                <td>
                  {editingId === student.id ? (
                    <input type="email" value={editForm.email} onChange={(e) => setEditForm({...editForm, email: e.target.value})} className="input-sm" />
                  ) : (
                    student.email
                  )}
                </td>
                <td>{student.student_id}</td>
                <td>
                  {editingId === student.id ? (
                    <input type="text" value={editForm.department} onChange={(e) => setEditForm({...editForm, department: e.target.value})} className="input-sm" />
                  ) : (
                    student.department
                  )}
                </td>
                <td>
                  {editingId === student.id ? (
                    <select value={editForm.is_active ? 'true' : 'false'} onChange={(e) => setEditForm({...editForm, is_active: e.target.value === 'true'})} className="input-sm">
                      <option value="true">Active</option>
                      <option value="false">Inactive</option>
                    </select>
                  ) : (
                    <span className={`status-badge ${student.is_active ? 'active' : 'inactive'}`}>
                      {student.is_active ? 'Active' : 'Inactive'}
                    </span>
                  )}
                </td>
                <td>{student.date_joined}</td>
                <td>
                  {editingId === student.id ? (
                    <>
                      <button className="btn-sm btn-primary" onClick={() => handleSave(student.id)}>Save</button>
                      <button className="btn-sm" onClick={() => setEditingId(null)}>Cancel</button>
                    </>
                  ) : (
                    <>
                      <button className="btn-sm" onClick={() => handleEdit(student)}>Edit</button>
                      <button className="btn-sm btn-danger" onClick={() => handleDelete(student.id)}>Delete</button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function AdminExams() {
  const { api } = useContext(AppContext);
  const [exams, setExams] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    title: '', description: '', exam_date: '', start_time: '09:00', end_time: '17:00',
    duration_minutes: 60, number_of_questions: 50, passing_percentage: 50, is_active: true
  });

  useEffect(() => {
    loadExams();
  }, []);

  const loadExams = async () => {
    try {
      const res = await api.get('/api/admin/exams/');
      setExams(res.data.exams);
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/admin/exams/create/', formData);
      setShowForm(false);
      setFormData({
        title: '', description: '', exam_date: '', start_time: '09:00', end_time: '17:00',
        duration_minutes: 60, number_of_questions: 50, passing_percentage: 50, is_active: true
      });
      loadExams();
    } catch (err) {
      console.error(err);
    }
  };

  const handleDelete = async (examId) => {
    if (confirm('Delete this exam?')) {
      try {
        await api.delete(`/api/admin/exams/${examId}/`);
        loadExams();
      } catch (err) {
        console.error(err);
      }
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Manage Exams</h1>
        <p>Create and manage exams</p>
      </div>

      <button className="btn-primary" onClick={() => setShowForm(!showForm)} style={{ marginBottom: '20px', width: 'auto' }}>
        {showForm ? 'Cancel' : 'Add New Exam'}
      </button>

      {showForm && (
        <div className="section" style={{ marginBottom: '20px' }}>
          <form onSubmit={handleSubmit} className="admin-form">
            <div className="form-row">
              <div className="form-group">
                <label>Title</label>
                <input type="text" value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>Date</label>
                <input type="date" value={formData.exam_date} onChange={(e) => setFormData({...formData, exam_date: e.target.value})} required />
              </div>
            </div>
            <div className="form-group">
              <label>Description</label>
              <textarea value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} />
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Start Time</label>
                <input type="time" value={formData.start_time} onChange={(e) => setFormData({...formData, start_time: e.target.value})} required />
              </div>
              <div className="form-group">
                <label>End Time</label>
                <input type="time" value={formData.end_time} onChange={(e) => setFormData({...formData, end_time: e.target.value})} required />
              </div>
            </div>
            <div className="form-row">
              <div className="form-group">
                <label>Duration (min)</label>
                <input type="number" value={formData.duration_minutes} onChange={(e) => setFormData({...formData, duration_minutes: parseInt(e.target.value)})} required />
              </div>
              <div className="form-group">
                <label>Questions</label>
                <input type="number" value={formData.number_of_questions} onChange={(e) => setFormData({...formData, number_of_questions: parseInt(e.target.value)})} required />
              </div>
              <div className="form-group">
                <label>Pass %</label>
                <input type="number" value={formData.passing_percentage} onChange={(e) => setFormData({...formData, passing_percentage: parseInt(e.target.value)})} required />
              </div>
            </div>
            <button type="submit" className="btn-primary" style={{ width: 'auto' }}>Create Exam</button>
          </form>
        </div>
      )}

      <div className="cards-grid">
        {exams.length === 0 ? (
          <div className="empty-state">No exams yet</div>
        ) : (
          exams.map(exam => (
            <div key={exam.id} className="content-card">
              <div className="card-header">
                <span className={`status-badge ${exam.is_active ? 'active' : 'inactive'}`}>
                  {exam.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <h3>{exam.title}</h3>
              <p>{exam.description}</p>
              <div className="card-meta">
                <span>{exam.exam_date}</span>
                <span>{exam.duration_minutes} min</span>
                <span>{exam.total_attempts} attempts</span>
              </div>
              <div className="card-actions">
                <button className="btn-danger" onClick={() => handleDelete(exam.id)}>Delete</button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

function AdminQuestions() {
  const { api } = useContext(AppContext);
  const [questions, setQuestions] = useState([]);
  const [categories, setCategories] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [qRes, cRes] = await Promise.all([
        api.get('/api/admin/questions/'),
        api.get('/api/categories/')
      ]);
      setQuestions(qRes.data.questions);
      setCategories(cRes.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <h1>Manage Questions</h1>
        <p>View all questions in the bank</p>
      </div>

      <div className="table-container">
        <table className="data-table">
          <thead>
            <tr>
              <th>Question</th>
              <th>Category</th>
              <th>Difficulty</th>
              <th>Correct</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {questions.map(q => (
              <tr key={q.id}>
                <td>{q.question_text.substring(0, 50)}...</td>
                <td>{q.category || 'None'}</td>
                <td><span className={`difficulty-badge ${q.difficulty}`}>{q.difficulty}</span></td>
                <td>{q.correct_answer}</td>
                <td><span className={`status-badge ${q.is_active ? 'active' : 'inactive'}`}>{q.is_active ? 'Active' : 'Inactive'}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function ExamStart() {
  const { api } = useContext(AppContext);
  const navigate = useNavigate();
  const [exam, setExam] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const examId = window.location.pathname.split('/').pop();

  useEffect(() => {
    loadExam();
  }, []);

  const loadExam = async () => {
    try {
      const res = await api.get(`/api/exam/${examId}/`);
      setExam(res.data);
    } catch (err) {
      setError('Unable to load exam');
    } finally {
      setLoading(false);
    }
  };

  const startExam = async () => {
    try {
      const res = await api.post(`/api/exam/${examId}/start/`);
      navigate(`/exam/${examId}/take/`, { state: { session_id: res.data.session_id } });
    } catch (err) {
      alert('Failed to start exam');
    }
  };

  if (loading) return <div className="page"><div className="empty-state">Loading...</div></div>;
  if (error) return <div className="page"><div className="empty-state">{error}</div></div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1>{exam?.title}</h1>
        <p>{exam?.description}</p>
      </div>
      <div className="content-card" style={{ maxWidth: '600px' }}>
        <div className="exam-info-card">
          <div className="info-row"><span>Duration:</span><strong>{exam?.duration_minutes} minutes</strong></div>
          <div className="info-row"><span>Questions:</span><strong>{exam?.number_of_questions}</strong></div>
          <div className="info-row"><span>Passing Score:</span><strong>{exam?.passing_percentage}%</strong></div>
          <div className="warning-box">
            <strong>Instructions:</strong>
            <ul>
              <li>Do not switch tabs or minimize the window during the exam</li>
              <li>Any attempt to leave the exam page will be recorded</li>
              <li>Submit your answers before the timer ends</li>
            </ul>
          </div>
          <button className="btn-primary" onClick={startExam}>Start Exam</button>
        </div>
      </div>
    </div>
  );
}

function ExamTake() {
  const { api } = useContext(AppContext);
  const [questions, setQuestions] = useState([]);
  const [currentQ, setCurrentQ] = useState(0);
  const [answers, setAnswers] = useState({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [warning, setWarning] = useState(false);
  const [violations, setViolations] = useState(0);
  const [submitted, setSubmitted] = useState(false);
  const examId = window.location.pathname.split('/')[2];
  const sessionId = new URLSearchParams(window.location.search).get('session');

  useEffect(() => {
    loadExam();
    const interval = setInterval(() => {
      setTimeLeft(t => {
        if (t <= 1) {
          handleSubmit();
          return 0;
        }
        return t - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleVisibility = () => {
      if (document.hidden && !submitted) {
        setWarning(true);
        setViolations(v => v + 1);
        api.post(`/api/exam/${examId}/violation/`, { violation: 'tab_switch' });
        setTimeout(() => setWarning(false), 3000);
      }
    };
    document.addEventListener('visibilitychange', handleVisibility);
    return () => document.removeEventListener('visibilitychange', handleVisibility);
  }, [submitted]);

  const loadExam = async () => {
    try {
      const res = await api.get(`/api/exam/${examId}/take/`);
      setQuestions(res.data.questions);
      setTimeLeft(res.data.time_remaining);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers({ ...answers, [questionId]: answer });
  };

  const handleSubmit = async () => {
    if (!confirm('Are you sure you want to submit?')) return;
    try {
      await api.post(`/api/exam/${examId}/submit/`, { session_id: sessionId, answers });
      setSubmitted(true);
      alert('Exam submitted successfully!');
    } catch (err) {
      console.error(err);
    }
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  if (questions.length === 0) return <div className="page"><div className="empty-state">Loading exam...</div></div>;

  const q = questions[currentQ];

  return (
    <div className="exam-page">
      {warning && (
        <div className="warning-banner">
          Warning: Tab switch detected! This incident has been recorded.
        </div>
      )}
      {violations > 0 && <div className="violation-counter">Violations: {violations}</div>}
      
      <div className="exam-header">
        <div className="exam-title-section">
          <h1>Exam in Progress</h1>
          <p>Question {currentQ + 1} of {questions.length}</p>
        </div>
        <div className={`timer-box ${timeLeft < 300 ? 'timer-warning' : ''}`}>
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" width="20" height="20"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
          <span className="timer-value">{formatTime(timeLeft)}</span>
        </div>
      </div>

      <div className="progress-bar">
        <div className="progress-fill" style={{ width: `${((currentQ + 1) / questions.length) * 100}%` }}></div>
      </div>

      <div className="questions-nav">
        {questions.map((_, i) => (
          <button key={i} className={`question-pill ${answers[questions[i].id] ? 'answered' : ''} ${i === currentQ ? 'current' : ''}`} onClick={() => setCurrentQ(i)}>
            {i + 1}
          </button>
        ))}
      </div>

      <div className="question-card">
        <h3>{q.question_text}</h3>
        <div className="options-list">
          {['A', 'B', 'C', 'D'].map(opt => (
            <label key={opt} className={`option-item ${answers[q.id] === opt ? 'selected' : ''}`}>
              <input type="radio" name={`q-${q.id}`} checked={answers[q.id] === opt} onChange={() => handleAnswer(q.id, opt)} />
              <span className="option-letter">{opt}</span>
              <span className="option-text">{q[`option${opt}`]}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="exam-nav-buttons">
        <button className="btn-secondary" disabled={currentQ === 0} onClick={() => setCurrentQ(c => c - 1)}>Previous</button>
        {currentQ < questions.length - 1 ? (
          <button className="btn-primary" onClick={() => setCurrentQ(c => c + 1)}>Next</button>
        ) : (
          <button className="btn-primary" onClick={handleSubmit}>Submit Exam</button>
        )}
      </div>
    </div>
  );
}

export default App;
