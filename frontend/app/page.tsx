'use client';

import { useState } from 'react';
import Tab1Clean from '@/components/Tab1Clean';
import Tab2Submit from '@/components/Tab2Submit';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'clean' | 'submit'>('clean');

  return (
    <main className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold text-center mb-2 text-gray-800">
          Form Pipeline
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Upload student spreadsheets and automate form submissions
        </p>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('clean')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'clean'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Tab 1: Clean Spreadsheet
              </button>
              <button
                onClick={() => setActiveTab('submit')}
                className={`flex-1 py-4 px-6 text-center font-medium transition-colors ${
                  activeTab === 'submit'
                    ? 'border-b-2 border-blue-500 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Tab 2: Submit Forms
              </button>
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'clean' ? <Tab1Clean /> : <Tab2Submit />}
          </div>
        </div>
      </div>
    </main>
  );
}

