import React from 'react';
import Content from './component/content';

function App() {
  return (
    <div className="min-h-screen flex flex-col bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-800 text-white p-4">
        <h1 className="text-xl font-bold">Teach Simple App</h1>
      </header>

      {/* Main content area */}
      <main className="flex-1 flex flex-col items-center justify-center p-4">
        <Content />
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-center border-t border-gray-700 p-4">
        <p className="text-sm text-gray-400">
          © {new Date().getFullYear()} Teach Simple App. All rights reserved.
        </p>
      </footer>
    </div>
  );
}

export default App;
