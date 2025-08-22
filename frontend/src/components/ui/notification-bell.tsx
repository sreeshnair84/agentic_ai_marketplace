import { useEffect, useState } from 'react';
import { Bell } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface Notification {
  id: number;
  user_id: string;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
  read_at?: string;
  metadata?: any;
}

export function NotificationBell({ userId }: { userId: string }) {
  const [notifications, setNotifications] = useState<Notification[] | undefined>([]);
  const [showDropdown, setShowDropdown] = useState(false);
  const safeNotifications = Array.isArray(notifications) ? notifications : [];
  const unreadCount = safeNotifications.filter(n => !n.is_read).length;

  useEffect(() => {
    if (!userId) return;
    fetch(`/api/v1/notifications?user_id=${userId}`)
      .then(res => res.json())
      .then(data => setNotifications(Array.isArray(data) ? data : []));
  }, [userId]);

  const markAsRead = async (id: number) => {
    await fetch(`/api/v1/notifications/${id}/read?user_id=${userId}`, { method: 'POST' });
    setNotifications(notifications => {
      const safe = Array.isArray(notifications) ? notifications : [];
      return safe.map(n => n.id === id ? { ...n, is_read: true } : n);
    });
  };

  const clearAll = async () => {
    await fetch(`/api/v1/notifications/clear?user_id=${userId}`, { method: 'POST' });
    setNotifications([]);
  };

  return (
    <div className="relative">
      <button className="relative" onClick={() => setShowDropdown(v => !v)}>
        <Bell className={cn('w-6 h-6', unreadCount ? 'text-red-500' : 'text-gray-500')} />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full px-1">{unreadCount}</span>
        )}
      </button>
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-80 bg-white shadow-lg rounded border z-50">
          <div className="flex items-center justify-between px-4 py-2 border-b">
            <span className="font-semibold">Notifications</span>
            <button className="text-xs text-blue-600" onClick={clearAll}>Clear All</button>
          </div>
          <ul className="max-h-80 overflow-y-auto">
            {safeNotifications.length === 0 && <li className="p-4 text-gray-500">No notifications</li>}
            {safeNotifications.map(n => (
              <li key={n.id} className={cn('px-4 py-2 border-b flex flex-col', !n.is_read && 'bg-blue-50')}
                  onClick={() => !n.is_read && markAsRead(n.id)}>
                <span className="font-medium">{n.message}</span>
                <span className="text-xs text-gray-400">{new Date(n.created_at).toLocaleString()}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
