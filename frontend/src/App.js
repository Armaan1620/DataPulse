import React, { useState, useEffect, useContext, createContext } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Create Auth Context
const AuthContext = createContext();

// Auth Provider Component
const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API}/auth/me`, {
            headers: { Authorization: `Bearer ${token}` }
          });
          setUser(response.data);
        } catch (error) {
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };
    initAuth();
  }, [token]);

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { email, password });
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(user);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (username, email, password) => {
    try {
      const response = await axios.post(`${API}/auth/register`, { username, email, password });
      const { access_token, user } = response.data;
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(user);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth
const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Login Component
const LoginForm = ({ onToggleMode }) => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await login(formData.email, formData.password);
    if (!result.success) {
      setError(result.error);
    }
    setLoading(false);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">DataPulse</h2>
          <p className="mt-2 text-gray-600">Sign in to your account</p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="your@email.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="••••••••"
              />
            </div>
          </div>
          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </div>
          <div className="text-center">
            <button
              type="button"
              onClick={onToggleMode}
              className="text-blue-600 hover:text-blue-500"
            >
              Don't have an account? Sign up
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Register Component
const RegisterForm = ({ onToggleMode }) => {
  const [formData, setFormData] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const result = await register(formData.username, formData.email, formData.password);
    if (!result.success) {
      setError(result.error);
    }
    setLoading(false);
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-md w-full space-y-8 p-8 bg-white rounded-xl shadow-lg">
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900">Join DataPulse</h2>
          <p className="mt-2 text-gray-600">Create your analytics account</p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
          <div className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium text-gray-700">
                Username
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={formData.username}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="johndoe"
              />
            </div>
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="your@email.com"
              />
            </div>
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="••••••••"
              />
            </div>
          </div>
          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Creating account...' : 'Sign up'}
            </button>
          </div>
          <div className="text-center">
            <button
              type="button"
              onClick={onToggleMode}
              className="text-blue-600 hover:text-blue-500"
            >
              Already have an account? Sign in
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// File Upload Component
const FileUpload = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const { token } = useAuth();

  const handleFiles = (files) => {
    const file = files[0];
    if (file) {
      uploadFile(file);
    }
  };

  const uploadFile = async (file) => {
    if (!file.name.match(/\.(csv|json)$/i)) {
      alert('Please upload a CSV or JSON file');
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(`${API}/datasets/upload`, formData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      });
      onUploadSuccess(response.data);
    } catch (error) {
      alert('Upload failed: ' + (error.response?.data?.detail || error.message));
    }
    setUploading(false);
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = [...e.dataTransfer.files];
    handleFiles(files);
  };

  const handleChange = (e) => {
    const files = [...e.target.files];
    handleFiles(files);
  };

  return (
    <div className="w-full">
      <div
        className={`relative border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
          dragActive 
            ? 'border-blue-400 bg-blue-50' 
            : 'border-gray-300 hover:border-blue-400'
        } ${uploading ? 'pointer-events-none opacity-50' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          type="file"
          multiple={false}
          accept=".csv,.json"
          onChange={handleChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploading}
        />
        
        <div className="space-y-2">
          <div className="mx-auto w-12 h-12 text-gray-400">
            <svg fill="none" stroke="currentColor" viewBox="0 0 48 48">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" />
            </svg>
          </div>
          <div>
            <p className="text-lg font-medium text-gray-900">
              {uploading ? 'Processing...' : 'Upload your dataset'}
            </p>
            <p className="text-sm text-gray-500">
              Drag & drop or click to select CSV/JSON files (max 50MB)
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

// Dataset List Component
const DatasetList = ({ datasets, onSelectDataset, selectedDataset }) => {
  const { token } = useAuth();

  const deleteDataset = async (datasetId) => {
    if (!window.confirm('Are you sure you want to delete this dataset?')) return;
    
    try {
      await axios.delete(`${API}/datasets/${datasetId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      window.location.reload(); // Simple refresh for now
    } catch (error) {
      alert('Delete failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1048576) return Math.round(bytes / 1024) + ' KB';
    return Math.round(bytes / 1048576) + ' MB';
  };

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold text-gray-900">Your Datasets</h3>
      {datasets.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No datasets uploaded yet</p>
      ) : (
        <div className="space-y-2">
          {datasets.map((dataset) => (
            <div
              key={dataset.id}
              className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                selectedDataset?.id === dataset.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => onSelectDataset(dataset)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{dataset.filename}</h4>
                  <div className="text-sm text-gray-500 space-y-1">
                    <p>Size: {formatFileSize(dataset.file_size)}</p>
                    <p>Rows: {dataset.row_count || 'Unknown'} | Columns: {dataset.column_count || 'Unknown'}</p>
                    <p>Status: <span className={`font-medium ${dataset.status === 'completed' ? 'text-green-600' : dataset.status === 'failed' ? 'text-red-600' : 'text-yellow-600'}`}>
                      {dataset.status}
                    </span></p>
                    <p>Uploaded: {new Date(dataset.upload_time).toLocaleDateString()}</p>
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteDataset(dataset.id);
                  }}
                  className="text-red-600 hover:text-red-800 p-1"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Analysis Display Component
const AnalysisDisplay = ({ analysis }) => {
  if (!analysis) return null;

  const { summary_stats, correlations, missing_data, outliers, ai_insights } = analysis;

  return (
    <div className="space-y-6">
      <h3 className="text-lg font-semibold text-gray-900">Analysis Results</h3>
      
      {/* AI Insights */}
      {ai_insights && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">🤖 AI Insights</h4>
          <p className="text-blue-800 whitespace-pre-wrap">{ai_insights}</p>
        </div>
      )}

      {/* Summary Statistics */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">📊 Summary Statistics</h4>
        {summary_stats?.numeric && (
          <div className="mb-4">
            <h5 className="font-medium text-gray-700 mb-2">Numeric Columns</h5>
            <div className="overflow-x-auto">
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2">Column</th>
                    <th className="text-left py-2">Mean</th>
                    <th className="text-left py-2">Std</th>
                    <th className="text-left py-2">Min</th>
                    <th className="text-left py-2">Max</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(summary_stats.numeric).map(([column, stats]) => (
                    <tr key={column} className="border-b">
                      <td className="py-2 font-medium">{column}</td>
                      <td className="py-2">{stats.mean?.toFixed(2) || 'N/A'}</td>
                      <td className="py-2">{stats.std?.toFixed(2) || 'N/A'}</td>
                      <td className="py-2">{stats.min || 'N/A'}</td>
                      <td className="py-2">{stats.max || 'N/A'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {/* Missing Data */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">🔍 Missing Data Analysis</h4>
        {Object.keys(missing_data?.total_missing || {}).length > 0 ? (
          <div className="space-y-2">
            {Object.entries(missing_data.total_missing).map(([column, count]) => (
              <div key={column} className="flex justify-between items-center">
                <span className="text-gray-700">{column}</span>
                <span className={`px-2 py-1 rounded text-sm ${count > 0 ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'}`}>
                  {count} missing ({missing_data.percentage_missing[column]?.toFixed(1)}%)
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500">No missing data information available</p>
        )}
      </div>

      {/* Outliers */}
      <div className="bg-white border border-gray-200 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">⚠️ Outlier Detection</h4>
        {outliers?.total_outliers !== undefined ? (
          <div className="space-y-2">
            <p className="text-gray-700">
              Found <strong>{outliers.total_outliers}</strong> outliers 
              ({outliers.outlier_percentage?.toFixed(1)}% of data)
            </p>
            {outliers.outlier_rows && outliers.outlier_rows.length > 0 && (
              <div>
                <p className="text-sm text-gray-600">Sample outlier row indices:</p>
                <p className="text-sm font-mono bg-gray-100 p-2 rounded">
                  {outliers.outlier_rows.join(', ')}
                </p>
              </div>
            )}
          </div>
        ) : outliers?.error ? (
          <p className="text-red-600">{outliers.error}</p>
        ) : (
          <p className="text-gray-500">No outlier analysis available</p>
        )}
      </div>

      {/* Correlations */}
      {Object.keys(correlations || {}).length > 0 && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3">🔗 Correlation Matrix</h4>
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead>
                <tr>
                  <th className="text-left py-2">Variable</th>
                  {Object.keys(correlations).map(col => (
                    <th key={col} className="text-left py-2 px-2">{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {Object.entries(correlations).map(([row, values]) => (
                  <tr key={row} className="border-t">
                    <td className="py-2 font-medium">{row}</td>
                    {Object.entries(values).map(([col, corr]) => (
                      <td key={col} className="py-2 px-2">
                        <span className={`px-1 rounded text-xs ${
                          Math.abs(corr) > 0.7 ? 'bg-red-100 text-red-800' :
                          Math.abs(corr) > 0.5 ? 'bg-yellow-100 text-yellow-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {corr?.toFixed(2) || 'N/A'}
                        </span>
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

// Main Dashboard Component
const Dashboard = () => {
  const [datasets, setDatasets] = useState([]);
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const { user, logout, token } = useAuth();

  const fetchDatasets = async () => {
    try {
      const response = await axios.get(`${API}/datasets`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDatasets(response.data);
    } catch (error) {
      console.error('Failed to fetch datasets:', error);
    }
    setLoading(false);
  };

  const fetchAnalysis = async (datasetId) => {
    setAnalysisLoading(true);
    try {
      const response = await axios.get(`${API}/datasets/${datasetId}/analysis`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setAnalysisData(response.data.analysis);
    } catch (error) {
      console.error('Failed to fetch analysis:', error);
    }
    setAnalysisLoading(false);
  };

  useEffect(() => {
    fetchDatasets();
  }, [token]);

  useEffect(() => {
    if (selectedDataset) {
      fetchAnalysis(selectedDataset.id);
    } else {
      setAnalysisData(null);
    }
  }, [selectedDataset]);

  const handleUploadSuccess = (result) => {
    alert(`File processed successfully! Rows: ${result.rows}, Columns: ${result.columns}`);
    fetchDatasets(); // Refresh the list
  };

  const handleSelectDataset = (dataset) => {
    setSelectedDataset(dataset);
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">DataPulse</h1>
              <p className="text-sm text-gray-500">Analytics Platform</p>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-gray-700">Welcome, {user?.username}</span>
              <button
                onClick={logout}
                className="bg-gray-100 hover:bg-gray-200 px-3 py-2 rounded-md text-sm font-medium text-gray-700"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Panel - Upload & Dataset List */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Upload Dataset</h2>
              <FileUpload onUploadSuccess={handleUploadSuccess} />
            </div>
            
            <div className="bg-white rounded-lg shadow p-6">
              <DatasetList 
                datasets={datasets} 
                onSelectDataset={handleSelectDataset}
                selectedDataset={selectedDataset}
              />
            </div>
          </div>

          {/* Right Panel - Analysis Results */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow p-6">
              {selectedDataset ? (
                <div>
                  <div className="mb-6">
                    <h2 className="text-lg font-semibold text-gray-900">
                      Analysis: {selectedDataset.filename}
                    </h2>
                    <p className="text-sm text-gray-500">
                      {selectedDataset.row_count} rows • {selectedDataset.column_count} columns
                    </p>
                  </div>
                  
                  {analysisLoading ? (
                    <div className="text-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="mt-2 text-gray-600">Loading analysis...</p>
                    </div>
                  ) : analysisData ? (
                    <AnalysisDisplay analysis={analysisData} />
                  ) : (
                    <p className="text-gray-500 text-center py-8">No analysis data available</p>
                  )}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-gray-400 mb-4">
                    <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Select a dataset</h3>
                  <p className="text-gray-500">Choose a dataset from the left panel to view its analysis</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

// Auth Component (Login/Register Toggle)
const AuthComponent = () => {
  const [isLogin, setIsLogin] = useState(true);
  
  return isLogin ? (
    <LoginForm onToggleMode={() => setIsLogin(false)} />
  ) : (
    <RegisterForm onToggleMode={() => setIsLogin(true)} />
  );
};

// Main App Component
function App() {
  return (
    <AuthProvider>
      <AuthContent />
    </AuthProvider>
  );
}

const AuthContent = () => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }
  
  return user ? <Dashboard /> : <AuthComponent />;
};

export default App;