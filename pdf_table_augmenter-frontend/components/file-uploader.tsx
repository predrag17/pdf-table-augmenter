/* eslint-disable @typescript-eslint/no-explicit-any */
"use client";

import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";

const ACCEPTED_FILE_TYPES = ["application/pdf"];

interface FileUploaderProps {
  field: any;
}

const FileUploader = ({ field }: FileUploaderProps) => {
  const [fileName, setFileName] = useState<string | null>(
    field.value ? field.value.name : null
  );

  useEffect(() => {
    if (field.value) {
      setFileName(field.value.name);
    }
  }, [field.value]);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];

    if (file && ACCEPTED_FILE_TYPES.includes(file.type)) {
      setFileName(file.name);
      field.onChange(file);
    }

    event.target.value = "";
  };

  const removeFile = () => {
    setFileName(null);
    field.onChange(null);
  };

  return (
    <div className="flex flex-col gap-4">
      <input
        type="file"
        accept={ACCEPTED_FILE_TYPES.join(",")}
        className="hidden"
        id="fileUpload"
        onChange={handleFileChange}
      />

      {fileName ? (
        <div className="relative flex items-center justify-between p-3 bg-gray-100 rounded-md shadow-sm">
          <span className="text-sm text-gray-700 truncate">{fileName}</span>
          <Button
            type="button"
            variant="destructive"
            size="icon"
            className="ml-2"
            onClick={removeFile}
          >
            <X className="w-4 h-4" />
          </Button>
        </div>
      ) : (
        <Button
          className="w-max"
          variant="outline"
          size="lg"
          type="button"
          onClick={() => document.getElementById("fileUpload")?.click()}
        >
          Upload file
        </Button>
      )}
    </div>
  );
};

export default FileUploader;
