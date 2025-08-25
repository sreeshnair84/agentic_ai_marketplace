'use client';

import React, { useState, useCallback, useRef } from 'react';
import {
  Upload,
  FileText,
  Image,
  Table,
  Zap,
  CheckCircle,
  AlertCircle,
  X,
  Settings,
  Eye,
  Download
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface ProcessingOptions {
  useDocling: boolean;
  extractTables: boolean;
  extractImages: boolean;
  extractMetadata: boolean;
  llmPreprocessing: boolean;
  llmModelId?: string;
  chunkingStrategy: 'fixed' | 'semantic' | 'sentence' | 'paragraph';
  chunkSize: number;
  chunkOverlap: number;
}

interface DocumentMetadata {
  title?: string;
  author?: string;
  description?: string;
  tags?: string[];
  category?: string;
  language?: string;
  source?: string;
}

interface UploadedFile {
  file: File;
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'error';
  progress: number;
  metadata?: DocumentMetadata;
  processingResult?: {
    chunksCreated: number;
    tablesExtracted: number;
    imagesExtracted: number;
    processingTime: number;
    method: 'docling' | 'basic';
  };
  error?: string;
}

interface EnhancedDocumentUploadProps {
  pipelineId: string;
  onUploadComplete?: (results: any[]) => void;
  onUploadError?: (error: string) => void;
}

const supportedFormats = [
  { ext: '.pdf', icon: <FileText className="h-4 w-4" />, color: 'red' },
  { ext: '.docx', icon: <FileText className="h-4 w-4" />, color: 'blue' },
  { ext: '.txt', icon: <FileText className="h-4 w-4" />, color: 'gray' },
  { ext: '.md', icon: <FileText className="h-4 w-4" />, color: 'purple' },
  { ext: '.csv', icon: <Table className="h-4 w-4" />, color: 'green' },
  { ext: '.html', icon: <FileText className="h-4 w-4" />, color: 'orange' }
];

export default function EnhancedDocumentUpload({
  pipelineId,
  onUploadComplete,
  onUploadError
}: EnhancedDocumentUploadProps) {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [activeTab, setActiveTab] = useState('upload');
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null);
  const [processingOptions, setProcessingOptions] = useState<ProcessingOptions>({
    useDocling: true,
    extractTables: true,
    extractImages: true,
    extractMetadata: true,
    llmPreprocessing: false,
    chunkingStrategy: 'semantic',
    chunkSize: 1000,
    chunkOverlap: 200
  });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragActive, setIsDragActive] = useState(false);

  const acceptedFileTypes = '.pdf,.docx,.txt,.md,.csv,.html';

  const handleFiles = useCallback((files: FileList | null) => {
    if (!files) return;
    
    const fileArray = Array.from(files);
    const newFiles: UploadedFile[] = fileArray.map(file => ({
      file,
      id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      status: 'pending',
      progress: 0,
      metadata: {
        title: file.name.replace(/\.[^/.]+$/, ''),
        tags: [],
        category: 'document'
      }
    }));
    
    setFiles(prev => [...prev, ...newFiles]);
  }, []);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    
    const files = e.dataTransfer?.files;
    handleFiles(files);
  }, [handleFiles]);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    handleFiles(e.target.files);
  }, [handleFiles]);

  const getRootProps = () => ({
    onDragEnter: handleDragEnter,
    onDragLeave: handleDragLeave,
    onDragOver: handleDragOver,
    onDrop: handleDrop,
    onClick: () => fileInputRef.current?.click()
  });

  const getInputProps = () => ({
    ref: fileInputRef,
    type: 'file' as const,
    multiple: true,
    accept: acceptedFileTypes,
    onChange: handleFileInputChange,
    style: { display: 'none' }
  });

  const updateFileMetadata = (fileId: string, metadata: Partial<DocumentMetadata>) => {
    setFiles(prev => prev.map(file => 
      file.id === fileId 
        ? { ...file, metadata: { ...file.metadata, ...metadata } }
        : file
    ));
  };

  const removeFile = (fileId: string) => {
    setFiles(prev => prev.filter(file => file.id !== fileId));
    if (selectedFile?.id === fileId) {
      setSelectedFile(null);
    }
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;
    
    setIsUploading(true);
    
    try {
      const pendingFiles = files.filter(file => file.status === 'pending');
      
      for (const file of pendingFiles) {
        // Update status to processing
        setFiles(prev => prev.map(f => 
          f.id === file.id ? { ...f, status: 'processing', progress: 0 } : f
        ));
        
        // Create FormData
        const formData = new FormData();
        formData.append('files', file.file);
        formData.append('metadata', JSON.stringify(file.metadata || {}));
        formData.append('processing_options', JSON.stringify(processingOptions));
        
        // Simulate upload progress
        const progressInterval = setInterval(() => {
          setFiles(prev => prev.map(f => {
            if (f.id === file.id && f.progress < 90) {
              return { ...f, progress: Math.min(f.progress + 10, 90) };
            }
            return f;
          }));
        }, 500);
        
        try {
          const response = await fetch(`/api/rag-pipelines-v2/${pipelineId}/documents/upload-advanced`, {
            method: 'POST',
            body: formData
          });
          
          clearInterval(progressInterval);
          
          if (!response.ok) {
            throw new Error(`Upload failed: ${response.statusText}`);
          }
          
          const result = await response.json();
          
          // Update file status
          setFiles(prev => prev.map(f => 
            f.id === file.id 
              ? {
                  ...f,
                  status: 'completed',
                  progress: 100,
                  processingResult: {
                    chunksCreated: result.chunks_created || 0,
                    tablesExtracted: result.tables_extracted || 0,
                    imagesExtracted: result.images_extracted || 0,
                    processingTime: result.processing_time || 0,
                    method: processingOptions.useDocling ? 'docling' : 'basic'
                  }
                }
              : f
          ));
          
        } catch (error) {
          clearInterval(progressInterval);
          
          setFiles(prev => prev.map(f => 
            f.id === file.id 
              ? {
                  ...f,
                  status: 'error',
                  progress: 0,
                  error: error instanceof Error ? error.message : 'Upload failed'
                }
              : f
          ));
        }
      }
      
      if (onUploadComplete) {
        const completedFiles = files.filter(f => f.status === 'completed');
        onUploadComplete(completedFiles);
      }
      
    } catch (error) {
      if (onUploadError) {
        onUploadError(error instanceof Error ? error.message : 'Upload process failed');
      }
    } finally {
      setIsUploading(false);
    }
  };

  const getFileIcon = (filename: string) => {
    const ext = '.' + filename.split('.').pop()?.toLowerCase();
    const format = supportedFormats.find(f => f.ext === ext);
    return format ? format.icon : <FileText className="h-4 w-4" />;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'processing':
        return <Settings className="h-4 w-4 text-blue-500 animate-spin" />;
      default:
        return <FileText className="h-4 w-4 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="upload">Upload Documents</TabsTrigger>
          <TabsTrigger value="settings">Processing Settings</TabsTrigger>
          <TabsTrigger value="results">Results</TabsTrigger>
        </TabsList>

        <TabsContent value="upload" className="space-y-4">
          {/* Upload Area */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Upload className="h-5 w-5" />
                <span>Document Upload</span>
              </CardTitle>
              <CardDescription>
                Upload documents to process with advanced parsing and chunking
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
                  isDragActive
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-300 dark:border-gray-600 hover:border-gray-400 dark:hover:border-gray-500'
                }`}
              >
                <input {...getInputProps()} />
                <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                {isDragActive ? (
                  <p className="text-blue-600 dark:text-blue-400">
                    Drop the files here...
                  </p>
                ) : (
                  <>
                    <p className="text-gray-600 dark:text-gray-400 mb-2">
                      Drag & drop files here, or click to select files
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-500">
                      Supports: PDF, DOCX, TXT, MD, CSV, HTML
                    </p>
                  </>
                )}
              </div>

              {/* Supported Formats */}
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Supported Formats:
                </p>
                <div className="flex flex-wrap gap-2">
                  {supportedFormats.map(format => (
                    <Badge key={format.ext} variant="outline" className="flex items-center space-x-1">
                      {format.icon}
                      <span>{format.ext.toUpperCase().slice(1)}</span>
                    </Badge>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* File List */}
          {files.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Files Queue ({files.length})</CardTitle>
                <div className="flex space-x-2">
                  <Button 
                    onClick={uploadFiles}
                    disabled={isUploading || files.every(f => f.status !== 'pending')}
                    className="flex items-center space-x-2"
                  >
                    <Zap className="h-4 w-4" />
                    <span>Process Documents</span>
                  </Button>
                  <Button 
                    variant="outline"
                    onClick={() => setFiles([])}
                    disabled={isUploading}
                  >
                    Clear All
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {files.map(file => (
                    <div key={file.id} className="border rounded-lg p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-2">
                            {getFileIcon(file.file.name)}
                            <span className="font-medium text-sm truncate">
                              {file.file.name}
                            </span>
                            {getStatusIcon(file.status)}
                            <Badge variant={
                              file.status === 'completed' ? 'default' :
                              file.status === 'error' ? 'destructive' :
                              file.status === 'processing' ? 'secondary' :
                              'outline'
                            }>
                              {file.status}
                            </Badge>
                          </div>
                          
                          {file.status === 'processing' && (
                            <Progress value={file.progress} className="mb-2" />
                          )}
                          
                          {file.error && (
                            <p className="text-sm text-red-600 dark:text-red-400">
                              {file.error}
                            </p>
                          )}
                          
                          {file.processingResult && (
                            <div className="text-xs text-gray-600 dark:text-gray-400 mt-2 grid grid-cols-2 gap-2">
                              <span>Chunks: {file.processingResult.chunksCreated}</span>
                              <span>Tables: {file.processingResult.tablesExtracted}</span>
                              <span>Images: {file.processingResult.imagesExtracted}</span>
                              <span>Time: {file.processingResult.processingTime.toFixed(1)}s</span>
                            </div>
                          )}
                        </div>
                        
                        <div className="flex items-center space-x-2 ml-4">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedFile(file)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => removeFile(file.id)}
                            disabled={file.status === 'processing'}
                          >
                            <X className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Processing Configuration</CardTitle>
              <CardDescription>
                Configure how documents are processed and chunked
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Document Processing */}
              <div>
                <h4 className="font-medium mb-4">Document Processing</h4>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="use-docling">Use Advanced Processing (Docling)</Label>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Advanced PDF parsing with table and image extraction
                      </p>
                    </div>
                    <Switch
                      id="use-docling"
                      checked={processingOptions.useDocling}
                      onCheckedChange={(checked) => 
                        setProcessingOptions(prev => ({ ...prev, useDocling: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="extract-tables">Extract Tables</Label>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Preserve table structure and content
                      </p>
                    </div>
                    <Switch
                      id="extract-tables"
                      checked={processingOptions.extractTables}
                      onCheckedChange={(checked) => 
                        setProcessingOptions(prev => ({ ...prev, extractTables: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="extract-images">Extract Images</Label>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Generate descriptions for images and figures
                      </p>
                    </div>
                    <Switch
                      id="extract-images"
                      checked={processingOptions.extractImages}
                      onCheckedChange={(checked) => 
                        setProcessingOptions(prev => ({ ...prev, extractImages: checked }))
                      }
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <Label htmlFor="extract-metadata">Extract Metadata</Label>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Extract document properties and structure
                      </p>
                    </div>
                    <Switch
                      id="extract-metadata"
                      checked={processingOptions.extractMetadata}
                      onCheckedChange={(checked) => 
                        setProcessingOptions(prev => ({ ...prev, extractMetadata: checked }))
                      }
                    />
                  </div>
                </div>
              </div>

              {/* Chunking Strategy */}
              <div>
                <h4 className="font-medium mb-4">Chunking Configuration</h4>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="chunking-strategy">Chunking Strategy</Label>
                    <Select
                      value={processingOptions.chunkingStrategy}
                      onValueChange={(value) => 
                        setProcessingOptions(prev => ({ 
                          ...prev, 
                          chunkingStrategy: value as ProcessingOptions['chunkingStrategy'] 
                        }))
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="semantic">Semantic Chunking</SelectItem>
                        <SelectItem value="sentence">Sentence-based</SelectItem>
                        <SelectItem value="paragraph">Paragraph-based</SelectItem>
                        <SelectItem value="fixed">Fixed Size</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="chunk-size">Chunk Size</Label>
                      <Input
                        id="chunk-size"
                        type="number"
                        min={100}
                        max={4000}
                        value={processingOptions.chunkSize}
                        onChange={(e) => 
                          setProcessingOptions(prev => ({ 
                            ...prev, 
                            chunkSize: parseInt(e.target.value) 
                          }))
                        }
                      />
                    </div>

                    <div>
                      <Label htmlFor="chunk-overlap">Chunk Overlap</Label>
                      <Input
                        id="chunk-overlap"
                        type="number"
                        min={0}
                        max={500}
                        value={processingOptions.chunkOverlap}
                        onChange={(e) => 
                          setProcessingOptions(prev => ({ 
                            ...prev, 
                            chunkOverlap: parseInt(e.target.value) 
                          }))
                        }
                      />
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="results" className="space-y-4">
          {files.length === 0 ? (
            <Card>
              <CardContent className="text-center py-12">
                <FileText className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                <p className="text-gray-600 dark:text-gray-400">
                  No documents processed yet
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {/* Summary Stats */}
              <Card>
                <CardHeader>
                  <CardTitle>Processing Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-4 gap-4 text-center">
                    <div>
                      <div className="text-2xl font-bold text-green-600">
                        {files.filter(f => f.status === 'completed').length}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Completed</p>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-blue-600">
                        {files.filter(f => f.status === 'processing').length}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Processing</p>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-red-600">
                        {files.filter(f => f.status === 'error').length}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Failed</p>
                    </div>
                    <div>
                      <div className="text-2xl font-bold text-gray-600">
                        {files.reduce((sum, f) => sum + (f.processingResult?.chunksCreated || 0), 0)}
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Total Chunks</p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Detailed Results */}
              {files.filter(f => f.status === 'completed').map(file => (
                <Card key={file.id}>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center space-x-2">
                      {getFileIcon(file.file.name)}
                      <span>{file.file.name}</span>
                      <Badge>Completed</Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {file.processingResult && (
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <div className="font-medium">Chunks Created</div>
                          <div className="text-gray-600 dark:text-gray-400">
                            {file.processingResult.chunksCreated}
                          </div>
                        </div>
                        <div>
                          <div className="font-medium">Tables Extracted</div>
                          <div className="text-gray-600 dark:text-gray-400">
                            {file.processingResult.tablesExtracted}
                          </div>
                        </div>
                        <div>
                          <div className="font-medium">Images Processed</div>
                          <div className="text-gray-600 dark:text-gray-400">
                            {file.processingResult.imagesExtracted}
                          </div>
                        </div>
                        <div>
                          <div className="font-medium">Processing Time</div>
                          <div className="text-gray-600 dark:text-gray-400">
                            {file.processingResult.processingTime.toFixed(1)}s
                          </div>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>

      {/* File Details Modal */}
      {selectedFile && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">
                {selectedFile.file.name}
              </h2>
              <Button 
                variant="ghost" 
                onClick={() => setSelectedFile(null)}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">File Information</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>Size: {(selectedFile.file.size / 1024).toFixed(1)} KB</div>
                  <div>Type: {selectedFile.file.type || 'Unknown'}</div>
                  <div>Status: {selectedFile.status}</div>
                  <div>Progress: {selectedFile.progress}%</div>
                </div>
              </div>
              
              {selectedFile.metadata && (
                <div>
                  <h3 className="font-semibold mb-2">Metadata</h3>
                  <div className="space-y-2 text-sm">
                    <div>Title: {selectedFile.metadata.title}</div>
                    <div>Author: {selectedFile.metadata.author || 'Not specified'}</div>
                    <div>Category: {selectedFile.metadata.category}</div>
                    {selectedFile.metadata.tags && selectedFile.metadata.tags.length > 0 && (
                      <div>Tags: {selectedFile.metadata.tags.join(', ')}</div>
                    )}
                  </div>
                </div>
              )}
              
              {selectedFile.processingResult && (
                <div>
                  <h3 className="font-semibold mb-2">Processing Results</h3>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>Chunks: {selectedFile.processingResult.chunksCreated}</div>
                    <div>Tables: {selectedFile.processingResult.tablesExtracted}</div>
                    <div>Images: {selectedFile.processingResult.imagesExtracted}</div>
                    <div>Method: {selectedFile.processingResult.method}</div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}