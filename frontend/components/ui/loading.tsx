import React from 'react';

interface LoadingProps {
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  type?: 'spinner' | 'skeleton' | 'dots';
}

const Loading: React.FC<LoadingProps> = ({ 
  className = '', 
  size = 'md',
  type = 'spinner' 
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8', 
    lg: 'w-12 h-12'
  };

  if (type === 'skeleton') {
    return (
      <div className={`animate-pulse bg-gray-300 rounded ${className}`}>
        <div className="h-4 bg-gray-300 rounded w-3/4 mb-2"></div>
        <div className="h-3 bg-gray-300 rounded w-1/2"></div>
      </div>
    );
  }

  if (type === 'dots') {
    return (
      <div className={`flex space-x-1 ${className}`}>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"></div>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
      </div>
    );
  }

  // Default spinner
  return (
    <div className={`${sizeClasses[size]} ${className}`}>
      <div className="animate-spin rounded-full border-2 border-gray-300 border-t-blue-600 w-full h-full"></div>
    </div>
  );
};

export default Loading;
