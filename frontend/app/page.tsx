'use client';

import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload, Video, Play, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { useSupabase } from '@/components/providers/SupabaseProvider';
import { useAnalytics } from '@/components/providers/AnalyticsProvider';
import { Header } from '@/components/Header';
import { VideoUpload } from '@/components/VideoUpload';
import { AnalysisResults } from '@/components/AnalysisResults';
import { AuthModal } from '@/components/AuthModal';
import { SubscriptionModal } from '@/components/SubscriptionModal';
import { AnalysisService } from '@/lib/analysisService';
import { formatFileSize } from '@/utils/fileUtils';
import toast from 'react-hot-toast';

interface AnalysisResult {
  exercise: string;
  score: number;
  risks: string[];
  corrections: string[];
  rep_count: number;
}

export default function HomePage() {
  const { user, loading: authLoading } = useSupabase();
  const { track } = useAnalytics();
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (file) {
      // Validate file size (20MB max)
      if (file.size > 20 * 1024 * 1024) {
        toast.error('File size must be less than 20MB');
        return;
      }

      // Validate file type
      const allowedTypes = ['video/mp4', 'video/webm', 'video/quicktime'];
      if (!allowedTypes.includes(file.type)) {
        toast.error('Please upload a valid video file (MP4, WebM, or MOV)');
        return;
      }

      setUploadedFile(file);
      track('video_uploaded', {
        file_size: file.size,
        file_type: file.type,
        file_name: file.name,
      });
      toast.success('Video uploaded successfully!');
    }
  }, [track]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.webm', '.mov'],
    },
    multiple: false,
    maxSize: 20 * 1024 * 1024, // 20MB
  });

  const handleAnalyze = async () => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }

    if (!uploadedFile) {
      toast.error('Please upload a video first');
      return;
    }

    setIsAnalyzing(true);
    setUploadProgress(0);
    setAnalysisResult(null);

    try {
      track('analysis_started', {
        user_id: user.id,
        file_size: uploadedFile.size,
        file_type: uploadedFile.type,
      });

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);

      const result = await AnalysisService.analyzeVideo(uploadedFile, (progress) => {
        setUploadProgress(progress);
      });

      clearInterval(progressInterval);
      setUploadProgress(100);

      setAnalysisResult(result);
      
      track('analysis_completed', {
        user_id: user.id,
        exercise_type: result.exercise,
        score: result.score,
        rep_count: result.rep_count,
      });

      toast.success('Analysis completed successfully!');
    } catch (error: any) {
      console.error('Analysis error:', error);
      
      if (error.message?.includes('subscription')) {
        setShowSubscriptionModal(true);
      } else {
        toast.error(error.message || 'Analysis failed. Please try again.');
      }
      
      track('analysis_failed', {
        user_id: user.id,
        error: error.message,
      });
    } finally {
      setIsAnalyzing(false);
      setUploadProgress(0);
    }
  };

  const handleRetry = () => {
    setUploadedFile(null);
    setAnalysisResult(null);
  };

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  return (
    <div className="min-h-screen gradient-bg">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="text-center mb-12"
        >
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-4">
            GymformAI
          </h1>
          <p className="text-xl md:text-2xl text-gray-600 max-w-3xl mx-auto">
            Analyze your workout form with AI. Get instant feedback on your exercise technique, 
            rep counting, and personalized corrections.
          </p>
        </motion.div>

        <div className="max-w-4xl mx-auto">
          {!analysisResult ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.2 }}
              className="card"
            >
              <VideoUpload
                uploadedFile={uploadedFile}
                isDragActive={isDragActive}
                getRootProps={getRootProps}
                getInputProps={getInputProps}
                isAnalyzing={isAnalyzing}
                uploadProgress={uploadProgress}
                onAnalyze={handleAnalyze}
              />
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <AnalysisResults
                result={analysisResult}
                onRetry={handleRetry}
                onNewAnalysis={() => {
                  setAnalysisResult(null);
                  setUploadedFile(null);
                }}
              />
            </motion.div>
          )}
        </div>

        {/* Features Section */}
        <motion.section
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.4 }}
          className="mt-20"
        >
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Why Choose GymformAI?
            </h2>
            <p className="text-lg text-gray-600">
              Get professional-level form analysis in seconds
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="card text-center">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Video className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">AI-Powered Analysis</h3>
              <p className="text-gray-600">
                Advanced computer vision and AI algorithms analyze your form with precision
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <CheckCircle className="w-8 h-8 text-success-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Instant Feedback</h3>
              <p className="text-gray-600">
                Get detailed form scores, risk detection, and personalized corrections
              </p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-warning-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Play className="w-8 h-8 text-warning-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">Rep Counting</h3>
              <p className="text-gray-600">
                Automatic repetition counting and exercise type detection
              </p>
            </div>
          </div>
        </motion.section>
      </main>

      {/* Modals */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
      />
      
      <SubscriptionModal
        isOpen={showSubscriptionModal}
        onClose={() => setShowSubscriptionModal(false)}
      />
    </div>
  );
} 