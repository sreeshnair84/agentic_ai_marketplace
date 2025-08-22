import Link from 'next/link';
import NavLinks from '@/app/ui/dashboard/nav-links';
import AcmeLogo from '@/app/ui/acme-logo';
import { PowerIcon } from '@heroicons/react/24/outline';

export default function SideNav() {
  return (
    <aside className="h-full w-64 bg-white dark:bg-gray-900 shadow-lg flex flex-col justify-between border-r border-gray-200 dark:border-gray-800">
      {/* Top: Logo */}
      <div className="px-6 pt-8 pb-4 flex flex-col items-center">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-32 md:w-40">
            <AcmeLogo />
          </div>
        </Link>
      </div>

      {/* Middle: Navigation */}
      <nav className="flex-1 px-2 flex flex-col gap-2">
        <NavLinks />
      </nav>

      {/* Bottom: User/Sign Out */}
      <div className="px-6 py-4 border-t border-gray-100 dark:border-gray-800 bg-gray-50 dark:bg-gray-900">
        <form>
          <button className="flex w-full items-center gap-3 rounded-md bg-gray-100 dark:bg-gray-800 p-3 text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-sky-100 hover:text-blue-600 transition-colors">
            <PowerIcon className="w-5 h-5" />
            <span>Sign Out</span>
          </button>
        </form>
      </div>
    </aside>
  );
}
