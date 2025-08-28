'use client';

import { useState, useEffect } from 'react';

export default function Home() {
  const [activeTab, setActiveTab] = useState('scrape');
  const [jobs, setJobs] = useState<any[]>([]);
  const [collections, setCollections] = useState<any[]>([]);

  useEffect(() => {
    // Load initial data
    fetchCollections();
  }, []);

  const fetchCollections = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/collections`);
      const data = await response.json();
      setCollections(data.collections || []);
    } catch (error) {
      console.error('Error fetching collections:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <h1 className="text-3xl font-bold text-gray-900">
                Ulti Weavi Guy 🚀
              </h1>
              <span className="ml-3 px-2 py-1 text-xs font-semibold text-blue-600 bg-blue-100 rounded-full">
                MVP
              </span>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Collections: {collections.length}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow p-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Welcome to Ulti Weavi Guy
          </h2>
          <p className="text-gray-600 mb-6">
            Your ultimate Weaviate frontend tool is deploying! This MVP includes:
          </p>
          <ul className="space-y-2 text-gray-700">
            <li>• Universal scraping with Firecrawl, Apify, and Unstructured.io</li>
            <li>• Cohere v3 embeddings for semantic search</li>
            <li>• Claude Sonnet 3.5 for intelligent chat</li>
            <li>• Weaviate vector database integration</li>
            <li>• Job orchestration with Redis queue</li>
          </ul>
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <p className="text-blue-800">
              🚀 Deployment successful! The full UI components will be available once the backend is connected.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
