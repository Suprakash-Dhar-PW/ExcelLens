import { UploadCloud } from "lucide-react"
import FileUploadDropzone from "../components/upload/FileUploadDropzone"

export default function Upload() {
  return (
    <div className="max-w-2xl mx-auto mt-10">
      <div className="text-center mb-8">
        <h2 className="text-3xl font-bold tracking-tight">Upload Data</h2>
        <p className="text-muted-foreground">Upload your Excel workbook to generate insights.</p>
      </div>
      <FileUploadDropzone />
    </div>
  )
}
