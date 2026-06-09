import { Bell, Search, Menu, Moon, Sun } from "lucide-react"

export default function Topbar({ darkMode, setDarkMode, sidebarOpen, setSidebarOpen }) {
  return (
    <header className="h-16 bg-background/80 backdrop-blur-md border-b border-border flex items-center justify-between px-6 sticky top-0 z-40">
      <div className="flex items-center">
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="md:hidden mr-4 text-muted-foreground hover:text-foreground"
        >
          <Menu size={24} />
        </button>
        <div className="relative w-64 hidden sm:block">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <input 
            type="search" 
            placeholder="Search commands..." 
            className="pl-9 h-9 w-full rounded-md border border-border bg-accent/50 px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
          />
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <button 
          onClick={() => setDarkMode(!darkMode)}
          className="p-2 bg-secondary text-secondary-foreground hover:bg-secondary/80 rounded-lg transition-colors border border-border"
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
        <button className="relative p-2 text-muted-foreground hover:text-foreground transition-colors">
          <Bell size={20} />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full border border-background"></span>
        </button>
      </div>
    </header>
  )
}
