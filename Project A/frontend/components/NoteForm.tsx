'use client';
import { useState, FormEvent } from 'react';
import { useRouter } from 'next/navigation';

export interface NoteData {
  title: string;
  body: string;
  tags?: string[];
}

interface NoteFormProps {
  initialData?: NoteData;
  apiUrl: string;
  method: 'POST' | 'PUT';
}

export default function NoteForm({ initialData, apiUrl, method }: NoteFormProps) {
  const router = useRouter();
  const [title, setTitle] = useState(initialData?.title || '');
  const [body, setBody] = useState(initialData?.body || '');
  const [tags, setTags] = useState(initialData?.tags?.join(', ') || '');
  
  const [errors, setErrors] = useState<{title?: string; body?: string}>({});
  const [serverError, setServerError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setErrors({});
    setServerError(null);

    let hasError = false;
    const newErrors: {title?: string; body?: string} = {};
    if (!title.trim()) {
      newErrors.title = 'Title is required';
      hasError = true;
    }
    if (!body.trim()) {
      newErrors.body = 'Body is required';
      hasError = true;
    }
    
    if (hasError) {
      setErrors(newErrors);
      return;
    }

    setIsSubmitting(true);
    
    const tagArray = tags
      .split(',')
      .map(t => t.trim())
      .filter(t => t.length > 0);
      
    try {
      const response = await fetch(apiUrl, {
        method,
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || ''
        },
        body: JSON.stringify({
          title: title.trim(),
          body: body.trim(),
          tags: tagArray
        })
      });

      if (!response.ok) {
        if (response.status === 401) {
          throw new Error('Check your API key configuration');
        }
        
        let errorMsg = 'An error occurred';
        try {
          const errorData = await response.json();
          // Display details from typical FastAPI error response
          if (Array.isArray(errorData.detail)) {
             errorMsg = errorData.detail.map((err: any) => err.msg).join(', ');
          } else {
             errorMsg = errorData.detail || errorData.message || JSON.stringify(errorData);
          }
        } catch {
          errorMsg = `Server error: ${response.status} ${response.statusText}`;
        }
        throw new Error(errorMsg);
      }

      router.push('/');
      router.refresh();
    } catch (error: any) {
      setServerError(error.message || 'An unexpected error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="max-w-xl mx-auto space-y-6 bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      {serverError && (
        <div className="bg-red-50 text-red-700 p-4 rounded-md border border-red-200 font-medium">
          {serverError}
        </div>
      )}

      <div>
        <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">Title <span className="text-red-500">*</span></label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className={`block w-full rounded-md border py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 ${errors.title ? 'border-red-500 bg-red-50 text-red-900' : 'border-gray-300'}`}
        />
        {errors.title && <p className="mt-1 text-sm text-red-600 font-medium">{errors.title}</p>}
      </div>

      <div>
        <label htmlFor="body" className="block text-sm font-medium text-gray-700 mb-1">Body <span className="text-red-500">*</span></label>
        <textarea
          id="body"
          rows={6}
          value={body}
          onChange={(e) => setBody(e.target.value)}
          className={`block w-full rounded-md border py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500 ${errors.body ? 'border-red-500 bg-red-50 text-red-900' : 'border-gray-300'}`}
        />
        {errors.body && <p className="mt-1 text-sm text-red-600 font-medium">{errors.body}</p>}
      </div>

      <div>
        <label htmlFor="tags" className="block text-sm font-medium text-gray-700 mb-1">Tags (comma-separated)</label>
        <input
          id="tags"
          type="text"
          value={tags}
          onChange={(e) => setTags(e.target.value)}
          placeholder="e.g. personal, urgent, wishlist"
          className="block w-full rounded-md border border-gray-300 py-2 px-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-70 disabled:cursor-not-allowed transition-colors"
      >
        {isSubmitting ? 'Saving Note...' : 'Save Note'}
      </button>
    </form>
  );
}
