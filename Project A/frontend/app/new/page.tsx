'use client';
import NoteForm from '@/components/NoteForm';
import Link from 'next/link';

export default function NewNotePage() {
  const apiUrl = `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/notes`;

  return (
    <div className="max-w-4xl mx-auto p-6 md:p-8">
      <div className="mb-6">
        <Link href="/" className="text-indigo-600 hover:text-indigo-800 font-medium text-sm flex items-center">
          &larr; Back to Home
        </Link>
      </div>
      <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">Create New Note</h1>
      <NoteForm apiUrl={apiUrl} method="POST" />
    </div>
  );
}
