'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';

interface Note {
  id: number;
  title: string;
  body: string;
  tags?: string[];
  created_at: string;
}

export default function Home() {
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNotes = async () => {
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/notes`, {
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || ''
        }
      });
      if (!res.ok) {
        if (res.status === 401) throw new Error('Check your API key configuration');
        throw new Error('Failed to fetch notes');
      }
      const data = await res.json();
      setNotes(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotes();
  }, []);

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this note?')) return;
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/notes/${id}`, {
        method: 'DELETE',
        headers: {
          'X-API-Key': process.env.NEXT_PUBLIC_API_KEY || ''
        }
      });
      if (res.ok) {
        setNotes(notes.filter(note => note.id !== id));
      } else {
        alert('Failed to delete note');
      }
    } catch (error) {
      alert('Error deleting note');
    }
  };

  return (
    <div className="max-w-7xl mx-auto p-6 md:p-8 min-h-screen">
      <div className="flex flex-col md:flex-row justify-between items-center mb-10">
        <div className="text-center md:text-left">
          <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-indigo-500 to-purple-600 tracking-tight">
            My Notes
          </h1>
          <p className="text-gray-500 mt-2 text-lg">Manage your thoughts and ideas seamlessly.</p>
        </div>
        <Link 
          href="/new" 
          className="mt-6 md:mt-0 bg-indigo-600 text-white px-6 py-3 rounded-full hover:bg-indigo-700 hover:shadow-lg hover:shadow-indigo-200 transition-all duration-300 font-medium flex items-center space-x-2 transform hover:-translate-y-0.5"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
          </svg>
          <span>Create Note</span>
        </Link>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-32">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-t-2 border-indigo-600"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-700 p-6 rounded-2xl border border-red-100 text-center shadow-sm max-w-2xl mx-auto mt-10">
          <svg className="w-12 h-12 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
          </svg>
          <h3 className="font-bold text-lg mb-2">Error Loading Notes</h3>
          <p>{error}</p>
        </div>
      ) : notes.length === 0 ? (
        <div className="text-center py-32 bg-white rounded-3xl border border-gray-100 shadow-sm max-w-2xl mx-auto">
          <div className="text-6xl mb-6">📝</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-3">No notes yet</h3>
          <p className="text-gray-500 mb-8 text-lg">Create your first note to capture your thoughts.</p>
          <Link href="/new" className="text-indigo-600 font-semibold hover:text-indigo-800 flex items-center justify-center space-x-2 group">
            <span>Create Note</span>
            <span className="transform group-hover:translate-x-1 transition-transform">&rarr;</span>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {notes.map(note => (
            <div key={note.id} className="bg-white rounded-3xl p-7 border border-gray-100 shadow-sm hover:shadow-xl hover:-translate-y-1.5 transition-all duration-300 flex flex-col group relative overflow-hidden h-80">
              <div className="absolute top-0 left-0 w-full h-1.5 bg-gradient-to-r from-indigo-500 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              
              <h2 className="text-xl font-bold text-gray-900 mb-3 line-clamp-1 shrink-0">{note.title}</h2>
              
              {note.tags && note.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-4 shrink-0">
                  {note.tags.map((tag, idx) => (
                    <span key={idx} className="text-xs px-3 py-1 rounded-full bg-indigo-50 text-indigo-600 font-semibold border border-indigo-100">
                      {tag}
                    </span>
                  ))}
                </div>
              )}

              <div className="mb-6 flex-grow overflow-y-auto pr-3 -mr-3 min-h-0" style={{ scrollbarWidth: 'thin' }}>
                <p className="text-gray-600 leading-relaxed whitespace-pre-wrap break-words">
                  {note.body}
                </p>
              </div>
              
              <div className="pt-5 border-t border-gray-50 flex justify-between items-center mt-auto opacity-70 group-hover:opacity-100 transition-opacity shrink-0">
                 <div className="text-xs text-gray-400 font-medium tracking-wide">
                   {new Date(note.created_at).toLocaleDateString(undefined, {
                     year: 'numeric', month: 'short', day: 'numeric'
                   })}
                 </div>
                 <div className="flex space-x-4">
                   <Link 
                     href={`/edit/${note.id}`}
                     className="text-sm font-semibold text-indigo-600 hover:text-indigo-800 transition-colors"
                   >
                     Edit
                   </Link>
                   <button 
                     onClick={() => handleDelete(note.id)}
                     className="text-sm font-semibold text-red-500 hover:text-red-700 transition-colors"
                   >
                     Delete
                   </button>
                 </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
