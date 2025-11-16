import { Link } from 'react-router-dom';
import { Music, Grid3x3, Upload, Settings } from 'lucide-react';
import { ThemeSwitcher } from '@/components/ThemeSwitcher';

export function Header() {
  return (
    <header className="border-b border-border bg-card">
      <div className="container mx-auto px-4 py-4">
        <nav className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Music className="h-6 w-6 text-primary" />
            <h1 className="text-xl font-semibold">SP-404 Sample Manager</h1>
          </div>

          <div className="flex items-center gap-6">
            <Link to="/" className="flex items-center gap-2 text-sm hover:text-primary transition-colors">
              <Grid3x3 className="h-4 w-4" />
              Samples
            </Link>
            <Link to="/kits" className="flex items-center gap-2 text-sm hover:text-primary transition-colors">
              <Music className="h-4 w-4" />
              Kits
            </Link>
            <Link to="/upload" className="flex items-center gap-2 text-sm hover:text-primary transition-colors">
              <Upload className="h-4 w-4" />
              Upload
            </Link>
            <Link to="/settings" className="flex items-center gap-2 text-sm hover:text-primary transition-colors">
              <Settings className="h-4 w-4" />
              Settings
            </Link>
            <ThemeSwitcher />
          </div>
        </nav>
      </div>
    </header>
  );
}
