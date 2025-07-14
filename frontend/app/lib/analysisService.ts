// This file was recreated to fix Vercel build issues. Do not remove.
import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for video processing
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

export interface AnalysisResult {
  exercise: string;
  score: number;
  risks: string[];
  corrections: string[];
  rep_count: number;
}

export interface AnalysisError {
  message: string;
  code?: string;
  details?: any;
}

export class AnalysisService {
  static async analyzeVideo(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<AnalysisResult> {
    try {
      // Create FormData
      const formData = new FormData();
      formData.append('video', file);

      // Add progress tracking
      const config = {
        onUploadProgress: (progressEvent: any) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            onProgress(progress);
          }
        },
      };

      // Make API call
      const response = await api.post('/api/analyze', formData, config);

      if (response.status === 200) {
        return response.data;
      } else {
        throw new Error('Analysis failed');
      }
    } catch (error: any) {
      console.error('Analysis service error:', error);

      // Handle specific error cases
      if (error.response) {
        const { status, data } = error.response;
        
        switch (status) {
          case 401:
            throw new Error('Please sign in to analyze videos');
          case 402:
            throw new Error('You have reached your daily limit. Please upgrade to Pro for unlimited analyses.');
          case 413:
            throw new Error('Video file is too large. Please upload a file smaller than 20MB.');
          case 422:
            throw new Error(data?.detail || 'Invalid video file format');
          case 429:
            throw new Error('Too many requests. Please try again later.');
          case 500:
            throw new Error('Server error. Please try again later.');
          default:
            throw new Error(data?.detail || 'Analysis failed. Please try again.');
        }
      } else if (error.request) {
        throw new Error('Network error. Please check your connection and try again.');
      } else {
        throw new Error(error.message || 'Analysis failed. Please try again.');
      }
    }
  }

  static async getAnalysisHistory(): Promise<AnalysisResult[]> {
    try {
      const response = await api.get('/api/analyses');
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch analysis history:', error);
      throw new Error('Failed to load analysis history');
    }
  }

  static async getAnalysisById(id: string): Promise<AnalysisResult> {
    try {
      const response = await api.get(`/api/analyses/${id}`);
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch analysis:', error);
      throw new Error('Failed to load analysis');
    }
  }

  static async deleteAnalysis(id: string): Promise<void> {
    try {
      await api.delete(`/api/analyses/${id}`);
    } catch (error: any) {
      console.error('Failed to delete analysis:', error);
      throw new Error('Failed to delete analysis');
    }
  }

  static async getUserUsage(): Promise<{
    daily_analyses: number;
    daily_limit: number;
    subscription_status: string;
  }> {
    try {
      const response = await api.get('/api/user/usage');
      return response.data;
    } catch (error: any) {
      console.error('Failed to fetch user usage:', error);
      throw new Error('Failed to load usage information');
    }
  }
}

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    // Get token from localStorage or wherever you store it
    const token = localStorage.getItem('supabase.auth.token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle token expiration
    if (error.response?.status === 401) {
      // Redirect to login or refresh token
      localStorage.removeItem('supabase.auth.token');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
); 