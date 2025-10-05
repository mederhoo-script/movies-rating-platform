import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { movieService } from '../services/api';
import { useAuth } from '../context/AuthContext';
import './AddMovie.css';

const AddMovie = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useAuth();
  
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    release_year: new Date().getFullYear(),
    genre: '',
    director: '',
    imdb_id: '',
    imdb_rank: '',
    actors: '',
    aka: '',
    imdb_url: '',
    imdb_iv: '',
    poster_url: '',
    photo_width: '',
    photo_height: '',
  });
  const [posterFile, setPosterFile] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setPosterFile(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      // Create FormData if we have a poster file, otherwise use regular object
      let dataToSend;
      
      if (posterFile) {
        dataToSend = new FormData();
        
        // Add all non-empty fields to FormData
        Object.keys(formData).forEach(key => {
          if (formData[key] !== null && formData[key] !== undefined && formData[key] !== '') {
            dataToSend.append(key, formData[key]);
          }
        });
        
        // Add the poster file
        dataToSend.append('poster_image', posterFile);
      } else {
        // Send as regular JSON, filtering out empty optional fields
        dataToSend = {};
        Object.keys(formData).forEach(key => {
          if (formData[key] !== null && formData[key] !== undefined && formData[key] !== '') {
            dataToSend[key] = formData[key];
          }
        });
      }

      const response = await movieService.createMovie(dataToSend);
      navigate(`/movies/${response.data.id}`);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create movie');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="add-movie-container">
      <div className="add-movie-card">
        <h2>Add New Movie</h2>
        {error && <div className="error-message">{error}</div>}
        <form onSubmit={handleSubmit}>
          <div className="form-section">
            <h3>Basic Information</h3>
            
            <div className="form-group">
              <label htmlFor="title">Title *</label>
              <input
                type="text"
                id="title"
                name="title"
                value={formData.title}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="description">Description *</label>
              <textarea
                id="description"
                name="description"
                value={formData.description}
                onChange={handleChange}
                rows="5"
                required
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="release_year">Release Year *</label>
                <input
                  type="number"
                  id="release_year"
                  name="release_year"
                  value={formData.release_year}
                  onChange={handleChange}
                  min="1900"
                  max={new Date().getFullYear() + 5}
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="genre">Genre *</label>
                <input
                  type="text"
                  id="genre"
                  name="genre"
                  value={formData.genre}
                  onChange={handleChange}
                  placeholder="e.g., Action, Drama, Comedy"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="director">Director *</label>
              <input
                type="text"
                id="director"
                name="director"
                value={formData.director}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="actors">Actors (optional)</label>
              <input
                type="text"
                id="actors"
                name="actors"
                value={formData.actors}
                onChange={handleChange}
                placeholder="e.g., Actor 1, Actor 2, Actor 3"
              />
              <div className="form-hint">Comma-separated list of actors</div>
            </div>
          </div>

          <div className="form-section">
            <h3>IMDB Information (Optional)</h3>
            
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="imdb_id">IMDB ID</label>
                <input
                  type="text"
                  id="imdb_id"
                  name="imdb_id"
                  value={formData.imdb_id}
                  onChange={handleChange}
                  placeholder="e.g., tt1234567"
                />
              </div>

              <div className="form-group">
                <label htmlFor="imdb_rank">IMDB Rating</label>
                <input
                  type="number"
                  id="imdb_rank"
                  name="imdb_rank"
                  value={formData.imdb_rank}
                  onChange={handleChange}
                  placeholder="e.g., 8.5"
                  step="0.1"
                  min="0"
                  max="10"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="imdb_url">IMDB URL</label>
              <input
                type="url"
                id="imdb_url"
                name="imdb_url"
                value={formData.imdb_url}
                onChange={handleChange}
                placeholder="https://www.imdb.com/title/tt1234567/"
              />
            </div>

            <div className="form-group">
              <label htmlFor="aka">Alternative Titles (AKA)</label>
              <input
                type="text"
                id="aka"
                name="aka"
                value={formData.aka}
                onChange={handleChange}
                placeholder="Alternative or foreign language titles"
              />
            </div>

            <div className="form-group">
              <label htmlFor="imdb_iv">IMDB IV</label>
              <input
                type="text"
                id="imdb_iv"
                name="imdb_iv"
                value={formData.imdb_iv}
                onChange={handleChange}
                placeholder="IMDB IV identifier"
              />
            </div>
          </div>

          <div className="form-section">
            <h3>Poster Image (Optional)</h3>
            
            <div className="poster-upload-options">
              <div className="upload-option">
                <label>Upload Poster Image</label>
                <div className="file-input-wrapper">
                  <label htmlFor="poster_image" className="file-input-label">
                    {posterFile ? '📎 Change File' : '📁 Choose File'}
                  </label>
                  <input
                    type="file"
                    id="poster_image"
                    name="poster_image"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="file-input"
                  />
                </div>
                {posterFile && (
                  <div className="file-name">Selected: {posterFile.name}</div>
                )}
              </div>

              <div className="upload-option">
                <label htmlFor="poster_url">Or Provide Poster URL</label>
                <input
                  type="url"
                  id="poster_url"
                  name="poster_url"
                  value={formData.poster_url}
                  onChange={handleChange}
                  placeholder="https://example.com/poster.jpg"
                  disabled={!!posterFile}
                />
                {posterFile && (
                  <div className="form-hint">Clear file selection to use URL instead</div>
                )}
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="photo_width">Poster Width (px)</label>
                <input
                  type="number"
                  id="photo_width"
                  name="photo_width"
                  value={formData.photo_width}
                  onChange={handleChange}
                  placeholder="e.g., 500"
                  min="1"
                />
              </div>

              <div className="form-group">
                <label htmlFor="photo_height">Poster Height (px)</label>
                <input
                  type="number"
                  id="photo_height"
                  name="photo_height"
                  value={formData.photo_height}
                  onChange={handleChange}
                  placeholder="e.g., 750"
                  min="1"
                />
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? 'Creating...' : 'Create Movie'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddMovie;
