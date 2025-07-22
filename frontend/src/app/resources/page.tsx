"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";

interface Service {
  id?: string;
  name: string;
  description: string;
  endpoint_url: string;
  pricing_model: string;
  base_price: number;
  currency: string;
  category: string;
  tags: string[];
  rate_limit: number;
  timeout: number;
  provider_address: string;
  api_spec: object;
}

const ResourcesPage = () => {
  const [services, setServices] = useState<Service[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copySuccess, setCopySuccess] = useState(false);
  
  // Placeholder proxy link - this will be replaced with the actual link later
  const proxyLink = "https://proxy.tokenlab.metis/api/v1";
  
  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(proxyLink);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy: ', err);
      // Fallback for browsers that don't support clipboard API
      const textArea = document.createElement('textarea');
      textArea.value = proxyLink;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      setCopySuccess(true);
      setTimeout(() => setCopySuccess(false), 2000);
    }
  };

  useEffect(() => {
    const fetchServices = async () => {
      try {
        const response = await fetch("/api/v1/services");
        if (!response.ok) {
          throw new Error("Failed to fetch services");
        }
        const data = await response.json();
        setServices(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : "An error occurred");
      } finally {
        setLoading(false);
      }
    };

    fetchServices();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
        <div className="container mx-auto px-4 py-8">
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6">
            <h2 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-2">
              Error
            </h2>
            <p className="text-red-600 dark:text-red-300">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">
            API Services
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Browse and manage your available API services
          </p>
        </div>

        {/* Proxy Link Section - Main Feature */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 border border-blue-200 dark:border-blue-700 rounded-xl p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center mb-3">
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                  </div>
                  <div>
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                      TokenLab Proxy URL
                    </h2>
                    <p className="text-sm text-gray-600 dark:text-gray-300">
                      Use this URL to access all services through our proxy
                    </p>
                  </div>
                </div>
                
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600 p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 mr-4">
                      <code className="text-sm font-mono text-gray-900 dark:text-white break-all">
                        {proxyLink}
                      </code>
                    </div>
                    <button
                      onClick={copyToClipboard}
                      className="flex items-center space-x-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 dark:focus:ring-offset-gray-800"
                    >
                      {copySuccess ? (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          <span className="text-sm font-medium">Copied!</span>
                        </>
                      ) : (
                        <>
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                          </svg>
                          <span className="text-sm font-medium">Copy</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
                
                <div className="mt-4 flex items-center text-sm text-gray-600 dark:text-gray-400">
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>This proxy URL provides secure access to all registered services</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Services Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service, index) => (
            <Link
              key={service.id || index}
              href={`/resources/${service.id || index}`}
              className="group"
            >
              <div className="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 p-6 h-full transition-all duration-200 hover:shadow-lg hover:scale-[1.02] hover:border-blue-300 dark:hover:border-blue-600">
                {/* Service Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                      {service.name}
                    </h3>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                      {service.category}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-gray-900 dark:text-white">
                      {service.base_price} {service.currency}
                    </div>
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      {service.pricing_model}
                    </div>
                  </div>
                </div>

                {/* Description */}
                <p className="text-gray-600 dark:text-gray-300 text-sm mb-4 line-clamp-2">
                  {service.description}
                </p>

                {/* Tags */}
                {service.tags.length > 0 && (
                  <div className="flex flex-wrap gap-1 mb-4">
                    {service.tags.slice(0, 3).map((tag, tagIndex) => (
                      <span
                        key={tagIndex}
                        className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300"
                      >
                        {tag}
                      </span>
                    ))}
                    {service.tags.length > 3 && (
                      <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300">
                        +{service.tags.length - 3}
                      </span>
                    )}
                  </div>
                )}

                {/* Service Stats */}
                <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100 dark:border-gray-700">
                  <div className="text-center">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {service.rate_limit}
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Rate Limit
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {service.timeout}s
                    </div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      Timeout
                    </div>
                  </div>
                </div>

                {/* Hover Arrow */}
                <div className="mt-4 flex items-center text-blue-600 dark:text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity">
                  <span className="text-sm font-medium">View Details</span>
                  <svg
                    className="w-4 h-4 ml-2 transform group-hover:translate-x-1 transition-transform"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* Empty State */}
        {services.length === 0 && (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-600"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13-8V4a1 1 0 00-1-1H7a1 1 0 00-1 1v1m8 0V4a1 1 0 00-1-1H9a1 1 0 00-1 1v1"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">
              No services
            </h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Get started by adding your first API service.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResourcesPage;
