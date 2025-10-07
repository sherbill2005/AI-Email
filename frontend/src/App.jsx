import React, { useState, useEffect } from 'react';
import './App.css';

// IMPORTANT: Replace this with your actual Google Client ID from your .env file
const GOOGLE_CLIENT_ID = "898998234950-qlhhcg2qgcs6o5nd69mbeb15asd7n19t.apps.googleusercontent.com";

// The public URL of your FastAPI backend, read from environment variables
const BACKEND_URL = import.meta.env.VITE_BACKEND_PUBLIC_URL;

// We construct the Google login URL ourselves.
// This is the exact link Google needs you to visit.
const GOOGLE_AUTH_URL = `https://accounts.google.com/o/oauth2/v2/auth?` + 
  `response_type=code&` + 
  `client_id=${GOOGLE_CLIENT_ID}&` + 
  `redirect_uri=${BACKEND_URL}/apis/v1/auth/google&` + 
  `scope=openid%20https://www.googleapis.com/auth/userinfo.email%20https://www.googleapis.com/auth/userinfo.profile%20https://www.googleapis.com/auth/gmail.readonly&` + 
  `access_type=offline`;


function App() {
  const [accessToken, setAccessToken] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // This code runs when the component loads.
    // It checks if we have been redirected back from the backend with a token or an error.
    const urlParams = new URLSearchParams(window.location.search);
    const token = urlParams.get('token');
    const authError = urlParams.get('error');

    if (token) {
      console.log("Received access token:", token);
      setAccessToken(token);
      // Clean the URL so the token is not visible anymore
      window.history.replaceState({}, document.title, "/");
    } else if (authError) {
      console.error("Received error:", authError);
      setError(`Authentication failed: ${authError}`);
      window.history.replaceState({}, document.title, "/");
    }
  }, []); // The empty array means this effect runs only once

  return (
    <div className="App">
      <h1>AI Email Summarizer</h1>
      
      {accessToken ? (
        <div className='card'>
          <h2>Login Successful!</h2>
          <p style={{ color: 'green', wordBreak: 'break-all' }}>Your API Access Token is: {accessToken}</p>
          <p>You can now use this token to make authenticated API calls.</p>
        </div>
      ) : error ? (
        <div className='card'>
          <p style={{ color: 'red' }}>{error}</p>
          <a href={GOOGLE_AUTH_URL}>
            <button>Try Again</button>
          </a>
        </div>
      ) : (
        <div className='card'>
          <p>Please sign in to continue</p>
          <a href={GOOGLE_AUTH_URL}>
            <button>Sign in with Google</button>
          </a>
        </div>
      )}
    </div>
  );
}

export default App;
