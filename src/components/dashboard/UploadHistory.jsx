import React from 'react';
import { FileSpreadsheet, Clock } from 'lucide-react';

export default function UploadHistory({ uploads = [], loading }) {
  if (loading) {
    return (
      <div className="glass-panel p-6 rounded-xl flex flex-col space-y-4">
        <h3 className="text-lg font-semibold">Recent Uploads</h3>
        <div className="space-y-3 mt-4">
          <div className="h-16 rounded-lg bg-accent/20 animate-pulse" />
        </div>
      </div>
    );
  }

  return (
    <div className="glass-panel p-6 rounded-xl">
      <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
        <FileSpreadsheet className="w-5 h-5 text-primary" /> Recent Uploads
      </h3>
      {uploads && uploads.length > 0 ? (
        <div className="space-y-3">
          {uploads.map((upload, idx) => (
            <div key={idx} className="p-4 rounded-lg bg-accent/10 border border-accent/20 flex justify-between items-center hover:bg-accent/20 transition-colors">
              <div className="flex items-center gap-3">
                <FileSpreadsheet className="w-8 h-8 text-muted-foreground p-1.5 bg-background rounded-md border" />
                <div>
                  <p className="text-sm font-medium">{upload.filename}</p>
                  <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                    <Clock className="w-3 h-3" /> {new Date(upload.upload_date).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <span className="px-2.5 py-1 rounded-full text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 uppercase tracking-wider">
                {upload.status}
              </span>
            </div>
          ))}
        </div>
      ) : (
        <div className="py-8 text-center text-sm text-muted-foreground">
          No recent uploads found.
        </div>
      )}
    </div>
  );
}
