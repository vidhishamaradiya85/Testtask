'use client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import NoteForm, { NoteData } from '@/components/NoteForm';

export default function EditNotePage() {
  const params = useParams();
  const id = params.id;
  const [initialData, setInitialData] = useState<NoteData | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  const apiUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/notes/${id}`;

  useEffect(() => {
    const fetchNote = async () => {
      try {
        const res = await fetch(apiUrl, {
          headers: {
            'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || ''
          }
        });
        
        if (!res.ok) {
           if (res.status === 401) {
             throw new Error('Check your API key configuration');
           }
           let errorMsg = 'Failed to fetch note';
           try {
             const errorData = await res.json();
             errorMsg = errorData.detail || errorData.message || errorMsg;
           } catch {
             // Use default
           }
           throw new Error(errorMsg);
        }
        
        const data = await res.json();
        setInitialData(data);
      } catch (err: any) {
        setError(err.message);
      }
    };
    
    if (id) {
      fetchNote();
    }
  }, [id, apiUrl]);

  return (
    <div className="max-w-4xl mx-auto p-6 md:p-8">
      <div className="mb-6">
        <Link href="/" className="text-indigo-600 hover:text-indigo-800 font-medium text-sm flex items-center">
          &larr; Back to Home
        </Link>
      </div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">Edit Note</h1>
      
      {error ? (
        <div className="max-w-xl mx-auto bg-red-50 text-red-700 p-4 rounded-md border border-red-200 font-medium text-center">
          {error}
        </div>
      ) : !initialData ? (
        <div className="max-w-xl mx-auto text-center p-8 bg-white rounded-lg shadow-sm border border-gray-200">
          <p className="text-gray-500 animate-pulse">Loading note data...</p>
        </div>
      ) : (
        <NoteForm 
          initialData={initialData} 
          apiUrl={apiUrl} 
          method="PUT" 
        />
      )}
    </div>
  );
}
