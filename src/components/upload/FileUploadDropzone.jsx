import { useState, useRef } from "react"
import { UploadCloud, File, CheckCircle, AlertCircle, Loader2 } from "lucide-react"
import axios from "axios"

export default function FileUploadDropzone({ onUploadSuccess }) {
  const [isDragging, setIsDragging] = useState(false)
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(false)
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && (droppedFile.name.endsWith('.xlsx') || droppedFile.name.endsWith('.xls') || droppedFile.name.endsWith('.csv'))) {
      setFile(droppedFile)
      setError(null)
      setSuccess(false)
    } else {
      setError("Please upload a valid Excel or CSV file.")
    }
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
      setSuccess(false)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setError(null)

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await axios.post("http://localhost:8000/api/v1/upload/", formData)
      
      setSuccess(true)
      if (onUploadSuccess) {
        onUploadSuccess(response.data)
      }
    } catch (err) {
      console.error("Upload error:", err)
      setError(err.response?.data?.detail || "Failed to upload file. Make sure the backend is running.")
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="w-full">
      <div 
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors cursor-pointer
          ${isDragging ? 'border-primary bg-primary/5' : 'border-border bg-card hover:bg-accent/50'}
          ${error ? 'border-destructive bg-destructive/5' : ''}
          ${success ? 'border-green-500 bg-green-500/5' : ''}
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !uploading && fileInputRef.current?.click()}
      >
        <input 
          type="file" 
          ref={fileInputRef} 
          className="hidden" 
          accept=".xlsx, .xls, .csv" 
          onChange={handleFileChange}
          disabled={uploading}
        />

        {uploading ? (
          <div className="flex flex-col items-center justify-center">
            <Loader2 className="h-12 w-12 text-primary animate-spin mb-4" />
            <h3 className="text-lg font-semibold mb-2">Uploading and parsing...</h3>
            <p className="text-sm text-muted-foreground">This might take a few seconds</p>
          </div>
        ) : success ? (
          <div className="flex flex-col items-center justify-center">
            <div className="w-16 h-16 bg-green-500/20 text-green-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle size={32} />
            </div>
            <h3 className="text-lg font-semibold text-green-500 mb-2">Upload Complete!</h3>
            <p className="text-sm text-muted-foreground mb-4">Your data is ready for analysis.</p>
            <button 
              onClick={(e) => { e.stopPropagation(); setFile(null); setSuccess(false); }}
              className="px-4 py-2 bg-secondary text-secondary-foreground rounded-md hover:bg-secondary/80 text-sm font-medium"
            >
              Upload another file
            </button>
          </div>
        ) : file ? (
          <div className="flex flex-col items-center justify-center">
            <div className="w-16 h-16 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <File size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2">{file.name}</h3>
            <p className="text-sm text-muted-foreground mb-4">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
            <div className="flex gap-4">
              <button 
                onClick={(e) => { e.stopPropagation(); setFile(null); }}
                className="px-4 py-2 border border-input bg-background rounded-md hover:bg-accent text-sm font-medium"
              >
                Cancel
              </button>
              <button 
                onClick={(e) => { e.stopPropagation(); handleUpload(); }}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 text-sm font-medium"
              >
                Process Data
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center">
            <div className="w-16 h-16 bg-primary/10 text-primary rounded-full flex items-center justify-center mx-auto mb-4">
              <UploadCloud size={32} />
            </div>
            <h3 className="text-lg font-semibold mb-2">Click or drag file to this area to upload</h3>
            <p className="text-sm text-muted-foreground">
              Support for Excel (.xlsx) and CSV files.
            </p>
            {error && (
              <div className="mt-4 flex items-center gap-2 text-destructive bg-destructive/10 px-4 py-2 rounded-md">
                <AlertCircle size={16} />
                <span className="text-sm">{error}</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
