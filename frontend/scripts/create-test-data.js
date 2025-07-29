#!/usr/bin/env node

/**
 * Create test data for development
 */

const API_BASE = 'http://localhost:8000/api/v1';

async function login() {
  const credentials = Buffer.from('test@example.com:testpass123').toString('base64');
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${credentials}`,
    },
  });
  
  if (!response.ok) {
    // Try to register first
    const registerResponse = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: 'test@example.com',
        username: 'testuser',
        password: 'testpass123',
      }),
    });
    
    if (!registerResponse.ok) {
      const errorText = await registerResponse.text();
      console.error('Registration failed:', registerResponse.status, errorText);
      throw new Error(`Failed to register test user: ${errorText}`);
    }
    
    // Try login again
    const loginRetry = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Authorization': `Basic ${credentials}`,
      },
    });
    
    if (!loginRetry.ok) {
      throw new Error('Failed to login');
    }
    
    const data = await loginRetry.json();
    return data.access_token;
  }
  
  const data = await response.json();
  return data.access_token;
}

async function createSample(token, sampleData) {
  const formData = new FormData();
  
  // Create a fake audio file
  const blob = new Blob(['fake audio data'], { type: 'audio/wav' });
  formData.append('file', blob, `${sampleData.title}.wav`);
  
  Object.keys(sampleData).forEach(key => {
    if (key === 'tags') {
      formData.append(key, JSON.stringify(sampleData[key]));
    } else {
      formData.append(key, sampleData[key]);
    }
  });
  
  const response = await fetch(`${API_BASE}/samples/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
    body: formData,
  });
  
  if (!response.ok) {
    const error = await response.text();
    console.error(`Failed to create sample ${sampleData.title}: ${response.status} - ${error}`);
    return false;
  }
  
  return true;
}

async function main() {
  try {
    console.log('Logging in...');
    const token = await login();
    console.log('Logged in successfully');
    
    const genres = ['hip-hop', 'jazz', 'electronic', 'soul', 'trap'];
    const moods = ['chill', 'energetic', 'dark', 'uplifting', 'mysterious'];
    const types = ['drums', 'bass', 'melody', 'vocals', 'fx'];
    
    console.log('Creating samples...');
    for (let i = 1; i <= 50; i++) {
      const sample = {
        title: `Sample ${i} - ${moods[i % moods.length]}`,
        genre: genres[i % genres.length],
        bpm: 60 + Math.floor(Math.random() * 120),
        musical_key: ['C', 'D', 'E', 'F', 'G', 'A', 'B'][i % 7] + ['', 'm'][i % 2],
        tags: [moods[i % moods.length], types[i % types.length]],
      };
      
      const success = await createSample(token, sample);
      if (success) {
        console.log(`Created sample ${i}/50`);
      }
    }
    
    console.log('Test data created successfully!');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

main();