export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function validateVideoFile(file: File): { isValid: boolean; error?: string } {
  // Check file size (20MB max)
  const maxSize = 20 * 1024 * 1024; // 20MB in bytes
  if (file.size > maxSize) {
    return {
      isValid: false,
      error: `File size must be less than ${formatFileSize(maxSize)}`,
    };
  }

  // Check file type
  const allowedTypes = ['video/mp4', 'video/webm', 'video/quicktime'];
  if (!allowedTypes.includes(file.type)) {
    return {
      isValid: false,
      error: 'Please upload a valid video file (MP4, WebM, or MOV)',
    };
  }

  // Check file extension
  const allowedExtensions = ['.mp4', '.webm', '.mov'];
  const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'));
  if (!allowedExtensions.includes(fileExtension)) {
    return {
      isValid: false,
      error: 'Please upload a valid video file (MP4, WebM, or MOV)',
    };
  }

  return { isValid: true };
}

export function generateFileName(originalName: string, userId: string): string {
  const timestamp = Date.now();
  const extension = originalName.substring(originalName.lastIndexOf('.'));
  return `${userId}_${timestamp}${extension}`;
}

export function getVideoDuration(file: File): Promise<number> {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video');
    video.preload = 'metadata';

    video.onloadedmetadata = () => {
      window.URL.revokeObjectURL(video.src);
      resolve(video.duration);
    };

    video.onerror = () => {
      window.URL.revokeObjectURL(video.src);
      reject(new Error('Failed to load video metadata'));
    };

    video.src = URL.createObjectURL(file);
  });
}

export function createVideoThumbnail(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const video = document.createElement('video');
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    video.onloadedmetadata = () => {
      // Set canvas size
      canvas.width = 320;
      canvas.height = 240;

      // Seek to 1 second or middle of video
      const seekTime = Math.min(1, video.duration / 2);
      video.currentTime = seekTime;
    };

    video.onseeked = () => {
      if (ctx) {
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const thumbnail = canvas.toDataURL('image/jpeg', 0.8);
        window.URL.revokeObjectURL(video.src);
        resolve(thumbnail);
      }
    };

    video.onerror = () => {
      window.URL.revokeObjectURL(video.src);
      reject(new Error('Failed to create video thumbnail'));
    };

    video.src = URL.createObjectURL(file);
  });
} 