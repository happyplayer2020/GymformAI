'use client';

import { motion } from 'framer-motion';
import { Upload, Video, X, Play, Loader2 } from 'lucide-react';
import { formatFileSize } from '@/utils/fileUtils';

interface VideoUploadProps {
  uploadedFile: File | null;
  isDragActive: boolean;
  getRootProps: () => any;
  getInputProps: () => any;
  isAnalyzing: boolean;
  uploadProgress: number;
  onAnalyze: () => void;
}

export function VideoUpload({
  uploadedFile,
  isDragActive,
  getRootProps,
  getInputProps,
  isAnalyzing,
  uploadProgress,
  onAnalyze,
}: VideoUploadProps) {
  const handleRemoveFile = () => {
    // This will be handled by the parent component
    window.location.reload();
  };

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Upload Your Workout Video
        </h2>
        <p className="text-gray-600">
          Upload a video of your exercise to get AI-powered form analysis
        </p>
      </div>

      {!uploadedFile ? (
        <div
          {...getRootProps()}
          className={`video-upload-area ${isDragActive ? 'dragover' : ''}`}
        >
          <input {...getInputProps()} />
          
          <motion.div
            initial={{ scale: 1 }}
            animate={{ scale: isDragActive ? 1.05 : 1 }}
            transition={{ duration: 0.2 }}
            className="space-y-4"
          >
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto">
              {isDragActive ? (
                <Upload className="w-8 h-8 text-primary-600" />
              ) : (
                <Video className="w-8 h-8 text-primary-600" />
              )}
            </div>
            
            <div>
              <p className="text-lg font-medium text-gray-900 mb-2">
                {isDragActive ? 'Drop your video here' : 'Drag & drop your video here'}
              </p>
              <p className="text-gray-500 mb-4">
                or click to browse files
              </p>
              
              <div className="text-sm text-gray-500 space-y-1">
                <p>Supported formats: MP4, WebM, MOV</p>
                <p>Maximum file size: 20MB</p>
              </div>
            </div>
          </motion.div>
        </div>
      ) : (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className="space-y-4"
        >
          {/* File Preview */}
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <Play className="w-6 h-6 text-primary-600" />
                </div>
                <div>
                  <p className="font-medium text-gray-900">{uploadedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {formatFileSize(uploadedFile.size)} • {uploadedFile.type}
                  </p>
                </div>
              </div>
              
              <button
                onClick={handleRemoveFile}
                className="p-2 text-gray-400 hover:text-gray-600 transition-colors"
                disabled={isAnalyzing}
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Progress Bar */}
          {isAnalyzing && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm text-gray-600">
                <span>Analyzing video...</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-bar-fill"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-4">
            <button
              onClick={onAnalyze}
              disabled={isAnalyzing}
              className="flex-1 btn-primary flex items-center justify-center space-x-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  <span>Analyze Form</span>
                </>
              )}
            </button>
            
            {!isAnalyzing && (
              <button
                onClick={handleRemoveFile}
                className="btn-secondary"
              >
                Remove
              </button>
            )}
          </div>
        </motion.div>
      )}

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 mb-2">Tips for best results:</h3>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• Record from a side angle for better pose detection</li>
          <li>• Ensure good lighting and clear visibility</li>
          <li>• Keep the camera steady and at a consistent distance</li>
          <li>• Include your full body in the frame</li>
          <li>• Perform 3-5 repetitions for accurate analysis</li>
        </ul>
      </div>
    </div>
  );
} 