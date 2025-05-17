'use client';
// This is a client component wrapper

import dynamic from 'next/dynamic';

// Use dynamic import with ssr:false to prevent hydration issues with client components
const TaskHub = dynamic(() => import('@/components/TaskHub'), { 
  ssr: false,
  loading: () => <div className="flex justify-center py-10">
    <div className="animate-spin rounded-full h-10 w-10 border-t-2 border-b-2 border-blue-500"></div>
  </div>
});

export default function TaskHubWrapper() {
  return <TaskHub />;
}