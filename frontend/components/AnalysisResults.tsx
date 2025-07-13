'use client';

import { motion } from 'framer-motion';
import { CheckCircle, AlertTriangle, TrendingUp, RotateCcw, Play } from 'lucide-react';

interface AnalysisResult {
  exercise: string;
  score: number;
  risks: string[];
  corrections: string[];
  rep_count: number;
}

interface AnalysisResultsProps {
  result: AnalysisResult;
  onRetry: () => void;
  onNewAnalysis: () => void;
}

export function AnalysisResults({ result, onRetry, onNewAnalysis }: AnalysisResultsProps) {
  const getScoreClass = (score: number) => {
    if (score >= 8) return 'score-excellent';
    if (score >= 6) return 'score-good';
    if (score >= 4) return 'score-fair';
    return 'score-poor';
  };

  const getScoreLabel = (score: number) => {
    if (score >= 8) return 'Excellent';
    if (score >= 6) return 'Good';
    if (score >= 4) return 'Fair';
    return 'Needs Improvement';
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-gray-900 mb-2">
          Analysis Complete!
        </h2>
        <p className="text-gray-600">
          Here's your detailed form analysis for {result.exercise}
        </p>
      </div>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Score Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className="lg:col-span-1"
        >
          <div className="card text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Form Score
            </h3>
            
            <div className={`score-circle mx-auto mb-4 ${getScoreClass(result.score)}`}>
              {result.score.toFixed(1)}
            </div>
            
            <p className="text-lg font-medium text-gray-900 mb-2">
              {getScoreLabel(result.score)}
            </p>
            
            <div className="flex items-center justify-center space-x-2 text-sm text-gray-600">
              <TrendingUp className="w-4 h-4" />
              <span>{result.rep_count} repetitions detected</span>
            </div>
          </div>
        </motion.div>

        {/* Risks and Corrections */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="lg:col-span-2 space-y-6"
        >
          {/* Detected Risks */}
          <div className="card">
            <div className="flex items-center space-x-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-warning-600" />
              <h3 className="text-lg font-semibold text-gray-900">
                Detected Risks
              </h3>
            </div>
            
            <div className="space-y-3">
              {result.risks.map((risk, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.3 + index * 0.1 }}
                  className="flex items-start space-x-3 p-3 bg-warning-50 rounded-lg border border-warning-200"
                >
                  <div className="w-2 h-2 bg-warning-500 rounded-full mt-2 flex-shrink-0" />
                  <p className="text-gray-800">{risk}</p>
                </motion.div>
              ))}
            </div>
          </div>

          {/* Corrections */}
          <div className="card">
            <div className="flex items-center space-x-2 mb-4">
              <CheckCircle className="w-5 h-5 text-success-600" />
              <h3 className="text-lg font-semibold text-gray-900">
                Recommended Corrections
              </h3>
            </div>
            
            <div className="space-y-3">
              {result.corrections.map((correction, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
                  className="flex items-start space-x-3 p-3 bg-success-50 rounded-lg border border-success-200"
                >
                  <div className="w-2 h-2 bg-success-500 rounded-full mt-2 flex-shrink-0" />
                  <p className="text-gray-800">{correction}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Exercise Summary */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.3 }}
        className="card"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Exercise Summary
        </h3>
        
        <div className="grid md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-2">
              <Play className="w-6 h-6 text-primary-600" />
            </div>
            <p className="text-sm text-gray-600">Exercise Type</p>
            <p className="font-semibold text-gray-900 capitalize">{result.exercise}</p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center mx-auto mb-2">
              <TrendingUp className="w-6 h-6 text-success-600" />
            </div>
            <p className="text-sm text-gray-600">Repetitions</p>
            <p className="font-semibold text-gray-900">{result.rep_count}</p>
          </div>
          
          <div className="text-center">
            <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center mx-auto mb-2">
              <AlertTriangle className="w-6 h-6 text-warning-600" />
            </div>
            <p className="text-sm text-gray-600">Issues Found</p>
            <p className="font-semibold text-gray-900">{result.risks.length}</p>
          </div>
        </div>
      </motion.div>

      {/* Action Buttons */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="flex flex-col sm:flex-row gap-4 justify-center"
      >
        <button
          onClick={onNewAnalysis}
          className="btn-primary flex items-center justify-center space-x-2"
        >
          <Play className="w-5 h-5" />
          <span>Analyze Another Video</span>
        </button>
        
        <button
          onClick={onRetry}
          className="btn-secondary flex items-center justify-center space-x-2"
        >
          <RotateCcw className="w-5 h-5" />
          <span>Retry This Video</span>
        </button>
      </motion.div>

      {/* Tips for Improvement */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.5 }}
        className="bg-blue-50 border border-blue-200 rounded-lg p-6"
      >
        <h3 className="font-semibold text-blue-900 mb-3">
          Tips for Improvement
        </h3>
        <div className="grid md:grid-cols-2 gap-4 text-sm text-blue-800">
          <ul className="space-y-1">
            <li>• Practice the corrections regularly</li>
            <li>• Record yourself from different angles</li>
            <li>• Focus on one correction at a time</li>
          </ul>
          <ul className="space-y-1">
            <li>• Maintain consistent form throughout</li>
            <li>• Consider working with a trainer</li>
            <li>• Track your progress over time</li>
          </ul>
        </div>
      </motion.div>
    </div>
  );
} 