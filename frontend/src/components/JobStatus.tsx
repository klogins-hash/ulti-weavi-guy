'use client';

import { useState, useEffect } from 'react';

interface Job {
  id: string;
  type: string;
  status: string;
  prompt?: string;
  progress: number;
  created_at: string;
  error?: string;
  result?: {
    collection_name?: string;
    documents_processed?: number;
    success?: boolean;
  };
}

interface JobStatusProps {
  jobs: Job[];
}

export function JobStatus({ jobs: initialJobs }: JobStatusProps) {
  const [jobs, setJobs] = useState<Job[]>(initialJobs);
  const [pollingJobs, setPollingJobs] = useState<Set<string>>(new Set());

  // Poll job status for running jobs
  useEffect(() => {
    const interval = setInterval(async () => {
      if (pollingJobs.size === 0) return;

      const updatedJobs = [...jobs];
      let hasUpdates = false;

      for (const jobId of pollingJobs) {
        try {
          const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/jobs/${jobId}`);
          if (response.ok) {
            const jobData = await response.json();
            const jobIndex = updatedJobs.findIndex(j => j.id === jobId);
            if (jobIndex !== -1) {
              updatedJobs[jobIndex] = jobData;
              hasUpdates = true;

              // Stop polling if job is completed or failed
              if (jobData.status === 'completed' || jobData.status === 'failed') {
                setPollingJobs(prev => {
                  const newSet = new Set(prev);
                  newSet.delete(jobId);
                  return newSet;
                });
              }
            }
          }
        } catch (error) {
          console.error(`Error polling job ${jobId}:`, error);
        }
      }

      if (hasUpdates) {
        setJobs(updatedJobs);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [jobs, pollingJobs]);

  // Add new jobs to polling when they're running
  useEffect(() => {
    const runningJobs = jobs.filter(job => job.status === 'running' || job.status === 'pending');
    const newPollingJobs = new Set(runningJobs.map(job => job.id));
    setPollingJobs(newPollingJobs);
  }, [jobs]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'running':
        return 'text-blue-600 bg-blue-100';
      case 'pending':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'failed':
        return '❌';
      case 'running':
        return '🔄';
      case 'pending':
        return '⏳';
      default:
        return '❓';
    }
  };

  if (jobs.length === 0) {
    return (
      <div className="text-center text-gray-500 py-4">
        <p>No jobs yet</p>
        <p className="text-sm mt-1">Start a scraping job to see progress here</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {jobs.slice(0, 5).map((job) => (
        <div key={job.id} className="border border-gray-200 rounded-lg p-3">
          {/* Job Header */}
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center space-x-2">
              <span className="text-lg">{getStatusIcon(job.status)}</span>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                {job.status}
              </span>
            </div>
            <span className="text-xs text-gray-500">
              {new Date(job.created_at).toLocaleTimeString()}
            </span>
          </div>

          {/* Job Details */}
          <div className="space-y-2">
            {job.prompt && (
              <p className="text-sm text-gray-700 truncate" title={job.prompt}>
                {job.prompt}
              </p>
            )}

            {/* Progress Bar */}
            {(job.status === 'running' || job.status === 'pending') && (
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${job.progress * 100}%` }}
                ></div>
              </div>
            )}

            {/* Results */}
            {job.status === 'completed' && job.result && (
              <div className="text-xs text-green-700 bg-green-50 p-2 rounded">
                <p>✅ Collection: {job.result.collection_name}</p>
                <p>📄 Documents: {job.result.documents_processed}</p>
              </div>
            )}

            {/* Error */}
            {job.status === 'failed' && job.error && (
              <div className="text-xs text-red-700 bg-red-50 p-2 rounded">
                <p>❌ Error: {job.error}</p>
              </div>
            )}
          </div>
        </div>
      ))}

      {jobs.length > 5 && (
        <div className="text-center">
          <button className="text-sm text-blue-600 hover:text-blue-800">
            View all {jobs.length} jobs
          </button>
        </div>
      )}
    </div>
  );
}
