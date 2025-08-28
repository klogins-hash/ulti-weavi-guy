'use client';

import { useState, useEffect } from 'react';
import { ScrapeForm } from '@/components/ScrapeForm';
import { ChatInterface } from '@/components/ChatInterface';
import { JobStatus } from '@/components/JobStatus';
import { CollectionsList } from '@/components/CollectionsList';

export default function Home() {
  const [activeTab, setActiveTab] = useState('scrape');
  const [jobs, setJobs] = useState([]);
  const [collections, setCollections] = useState([]);

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

  const handleJobCreated = (jobId: string) => {
    // Refresh collections after job completion
    setTimeout(fetchCollections, 2000);
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

      {/* Navigation Tabs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {[
              { id: 'scrape', label: 'Scrape & Embed', icon: '🕷️' },
              { id: 'chat-data', label: 'Chat with Data', icon: '💬' },
              { id: 'chat-config', label: 'Configure DB', icon: '⚙️' },
              { id: 'collections', label: 'Collections', icon: '📚' },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Primary Content */}
          <div className="lg:col-span-2">
            {activeTab === 'scrape' && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">
                    Scrape & Auto-Embed
                  </h2>
                  <p className="text-gray-600 mb-6">
                    Describe what you want to scrape in natural language. The system will automatically
                    scrape, embed with Cohere v3, and upload to Weaviate.
                  </p>
                  <ScrapeForm onJobCreated={handleJobCreated} />
                </div>
              </div>
            )}

            {activeTab === 'chat-data' && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Chat with Your Data
                </h2>
                <p className="text-gray-600 mb-6">
                  Ask questions about your scraped data. Claude will search through your collections
                  and provide contextual answers.
                </p>
                <ChatInterface type="data" collections={collections} />
              </div>
            )}

            {activeTab === 'chat-config' && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Configure Weaviate
                </h2>
                <p className="text-gray-600 mb-6">
                  Manage your Weaviate database structure through natural language.
                  Create collections, modify schemas, and organize your data.
                </p>
                <ChatInterface type="config" collections={collections} />
              </div>
            )}

            {activeTab === 'collections' && (
              <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Collections Overview
                </h2>
                <CollectionsList 
                  collections={collections} 
                  onRefresh={fetchCollections}
                />
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Job Status */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Recent Jobs
              </h3>
              <JobStatus jobs={jobs} />
            </div>

            {/* Quick Stats */}
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Quick Stats
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Collections</span>
                  <span className="font-medium">{collections.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Documents</span>
                  <span className="font-medium">
                    {collections.reduce((sum, col) => sum + (col.count || 0), 0)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Embedding Model</span>
                  <span className="font-medium text-sm">Cohere v3</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Chat Model</span>
                  <span className="font-medium text-sm">Claude 3.5</span>
                </div>
              </div>
            </div>

            {/* Help */}
            <div className="bg-blue-50 rounded-lg p-6">
              <h3 className="text-lg font-medium text-blue-900 mb-2">
                Getting Started
              </h3>
              <ul className="text-sm text-blue-800 space-y-2">
                <li>• Try: "Scrape all blog posts from example.com"</li>
                <li>• Try: "Process my PDF files in /documents"</li>
                <li>• Try: "What are the main topics in my data?"</li>
                <li>• Try: "Create a collection for news articles"</li>
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
