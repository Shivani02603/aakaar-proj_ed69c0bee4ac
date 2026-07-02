import React, { useEffect, useState } from 'react';
import { formatDistanceToNow } from 'date-fns';
import { getSessions, createSession } from '../api/client';
import { Document, ChatSession } from '../types';
import { toast } from 'react-toastify';

interface SessionSidebarProps {
  onSelectSession: (id: string) => void;
  activeSessionId?: string;
}

const SessionSidebar: React.FC<SessionSidebarProps> = ({ onSelectSession, activeSessionId }) => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSessions = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await getSessions();
        const sortedSessions = response.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
        setSessions(sortedSessions);
      } catch (err) {
        setError('Failed to fetch sessions');
        toast.error('Failed to fetch sessions');
      } finally {
        setLoading(false);
      }
    };

    fetchSessions();
  }, []);

  const handleNewChat = async () => {
    try {
      const newSession = await createSession();
      setSessions((prev) => [newSession, ...prev]);
      onSelectSession(newSession.id);
    } catch (err) {
      toast.error('Failed to create new session');
    }
  };

  return (
    <div className="w-64 bg-gray-100 h-full border-r border-gray-300">
      <div className="p-4 border-b border-gray-300">
        <button
          onClick={handleNewChat}
          className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
        >
          New Chat
        </button>
      </div>
      <div className="p-4 space-y-2">
        {loading ? (
          Array.from({ length: 3 }).map((_, index) => (
            <div
              key={index}
              className="h-10 bg-gray-300 animate-pulse rounded"
            ></div>
          ))
        ) : error ? (
          <div className="text-red-500">{error}</div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => onSelectSession(session.id)}
              className={`p-3 rounded cursor-pointer ${
                activeSessionId === session.id
                  ? 'bg-blue-100 border-l-4 border-blue-500'
                  : 'hover:bg-gray-200'
              }`}
            >
              <div className="font-medium truncate">
                {session.session_id.length > 30
                  ? `${session.session_id.slice(0, 30)}...`
                  : session.session_id}
              </div>
              <div className="text-sm text-gray-500">
                {formatDistanceToNow(new Date(session.created_at), {
                  addSuffix: true,
                })}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default SessionSidebar;