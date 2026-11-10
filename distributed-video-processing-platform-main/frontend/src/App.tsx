
import { useEffect, useState, useCallback } from 'react'

import {
  UploadCloud,
  RefreshCw,
  Film,
  CheckCircle2,
  Play,
  Clock3,
  AlertCircle,
  Loader2,
} from 'lucide-react'

const API = (
  import.meta.env.VITE_API_URL || 'http://localhost:8000'
).replace(/\/$/, '')

const MEDIA_API = 'http://localhost:8006'

type Video = {
  video_id: string
  filename: string
  size: number
  status: string
  created_at?: string
}

type Output = {
  resolution: string
  url: string
  size: number
}

export default function App() {
  const [videos, setVideos] = useState<Video[]>([])
  const [file, setFile] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [message, setMessage] = useState('')
  const [messageType, setMessageType] = useState<
    'success' | 'error' | 'info'
  >('info')

  const [selected, setSelected] = useState<Video | null>(null)
  const [outputs, setOutputs] = useState<Output[]>([])
  const [thumb, setThumb] = useState('')
  const [thumbnails, setThumbnails] = useState<
    Record<string, string>
  >({})

  const [resolutions, setResolutions] = useState<string[]>([
    '360p',
    '720p',
  ])

  const fmt = (n: number) =>
    `${(n / 1024 / 1024).toFixed(1)} MB`

  const showMessage = (
    text: string,
    type: 'success' | 'error' | 'info' = 'info'
  ) => {
    setMessage(text)
    setMessageType(type)
  }

  // Fetch video library and thumbnails
  const refresh = useCallback(async () => {
    setRefreshing(true)

    try {
      const response = await fetch(`${API}/videos`)

      if (!response.ok) {
        throw new Error(
          `API request failed with status ${response.status}`
        )
      }

      const data: Video[] = await response.json()
      const videoList = Array.isArray(data) ? data : []

      setVideos(videoList)
      setMessage('')

      // Fetch thumbnails for all videos
      const thumbnailEntries = await Promise.all(
        videoList.map(async (video) => {
          try {
            const response = await fetch(
              `${MEDIA_API}/videos/${video.video_id}/thumbnails`
            )

            if (!response.ok) {
              return [video.video_id, ''] as const
            }

            const data = await response.json()

            const thumbnailPath =
              data.url || data.thumbnail_url || ''

            return [
              video.video_id,
              thumbnailPath
                ? `${MEDIA_API}${thumbnailPath}`
                : '',
            ] as const
          } catch {
            return [video.video_id, ''] as const
          }
        })
      )

      setThumbnails(Object.fromEntries(thumbnailEntries))
    } catch (error) {
      console.error('Failed to fetch videos:', error)

      showMessage(
        'Unable to connect to API Gateway. Check that Docker services are running and CORS is configured.',
        'error'
      )
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  // Upload video
  async function upload() {
    if (!file || busy) return

    setBusy(true)
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await fetch(`${API}/videos/upload`, {
        method: 'POST',
        body: formData,
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || `Upload failed (${response.status})`
        )
      }

      showMessage(
        `Video uploaded successfully! Video ID: ${data.video_id}`,
        'success'
      )

      setFile(null)

      // Refresh library after upload
      await refresh()
    } catch (error) {
      console.error('Upload error:', error)

      showMessage(
        error instanceof Error
          ? error.message
          : 'Upload failed. Please check your API connection.',
        'error'
      )
    } finally {
      setBusy(false)
    }
  }

  // Start video processing
  async function process(video: Video) {
    if (resolutions.length === 0) {
      showMessage(
        'Please select at least one output resolution.',
        'error'
      )
      return
    }

    try {
      const queryParams = resolutions
        .map(
          (resolution) =>
            `resolutions=${encodeURIComponent(resolution)}`
        )
        .join('&')

      const response = await fetch(
        `${API}/videos/${video.video_id}/process?${queryParams}`,
        {
          method: 'POST',
        }
      )

      const data = await response.json()

      if (!response.ok) {
        throw new Error(
          data.detail || `Processing failed (${response.status})`
        )
      }

      showMessage(
        `Processing job queued successfully! Job ID: ${data.job_id}`,
        'success'
      )

      await refresh()
    } catch (error) {
      console.error('Processing error:', error)

      showMessage(
        error instanceof Error
          ? error.message
          : 'Could not start processing.',
        'error'
      )
    }
  }

  // Fetch output details and thumbnail
  async function details(video: Video) {
    setSelected(video)
    setOutputs([])
    setThumb('')

    try {
      const [outputsResponse, thumbnailsResponse] =
        await Promise.all([
          fetch(`${API}/videos/${video.video_id}/outputs`),
          fetch(
            `${MEDIA_API}/videos/${video.video_id}/thumbnails`
          ),
        ])

      if (outputsResponse.ok) {
        const outputsData = await outputsResponse.json()

        setOutputs(
          Array.isArray(outputsData) ? outputsData : []
        )
      }

      if (thumbnailsResponse.ok) {
        const thumbnailData =
          await thumbnailsResponse.json()

        const thumbnailUrl =
          thumbnailData.url ||
          thumbnailData.thumbnail_url ||
          ''

        setThumb(
          thumbnailUrl
            ? `${MEDIA_API}${thumbnailUrl}`
            : ''
        )
      }
    } catch (error) {
      console.error(
        'Failed to fetch video details:',
        error
      )

      showMessage(
        'Unable to load video details.',
        'error'
      )
    }
  }

  // Toggle output resolution
  function toggleResolution(
    resolution: string,
    checked: boolean
  ) {
    setResolutions((previous) =>
      checked
        ? [...previous, resolution]
        : previous.filter(
            (item) => item !== resolution
          )
    )
  }

  return (
    <main className="shell">
      {/* Header */}
      <header>
        <div className="brand">
          <div className="logo">
            <Film />
          </div>

          <div>
            <h1>Video Processing Studio</h1>
            <p>Distributed transcoding · Media pipeline</p>
          </div>
        </div>

        <button
          className="ghost"
          onClick={refresh}
          disabled={refreshing}
        >
          <RefreshCw
            size={16}
            className={refreshing ? 'spin' : ''}
          />
          {refreshing ? 'Refreshing…' : 'Refresh'}
        </button>
      </header>

      {/* Hero */}
      <section className="hero">
        <div>
          <span className="eyebrow">MEDIA WORKSPACE</span>

          <h2>
            Upload once.
            <br />
            <em>Transcode everywhere.</em>
          </h2>

          <p>
            Manage your video pipeline from upload to delivery.
          </p>
        </div>

        <div className="heroicon">
          <Film size={64} />
        </div>
      </section>

      {/* Upload Section */}
      <section className="upload panel">
        <div>
          <h3>Upload a video</h3>
          <p>
            MP4, MOV, MKV, WEBM or AVI · Maximum 500 MB
          </p>
        </div>

        <label className="drop">
          <UploadCloud size={23} />

          <span>
            {file ? file.name : 'Choose a video file'}
          </span>

          <input
            type="file"
            accept="video/mp4,video/quicktime,video/x-matroska,video/webm,video/x-msvideo"
            onChange={(event) =>
              setFile(event.target.files?.[0] || null)
            }
          />
        </label>

        <button
          className="primary"
          disabled={!file || busy}
          onClick={upload}
        >
          {busy ? (
            <>
              <Loader2 size={16} className="spin" />
              Uploading…
            </>
          ) : (
            <>
              <UploadCloud size={16} />
              Upload video
            </>
          )}
        </button>
      </section>

      {/* Output Settings */}
      <section className="panel settings">
        <div>
          <h3>Output presets</h3>
          <p>Select renditions to create when processing</p>
        </div>

        {['360p', '720p', '1080p'].map((resolution) => (
          <label className="check" key={resolution}>
            <input
              type="checkbox"
              checked={resolutions.includes(resolution)}
              onChange={(event) =>
                toggleResolution(
                  resolution,
                  event.target.checked
                )
              }
            />
            {resolution}
          </label>
        ))}
      </section>

      {/* Notifications */}
      {message && (
        <div className={`notice ${messageType}`}>
          {messageType === 'error' ? (
            <AlertCircle size={18} />
          ) : messageType === 'success' ? (
            <CheckCircle2 size={18} />
          ) : null}

          <span>{message}</span>
        </div>
      )}

      {/* Video Library Header */}
      <section className="sectionhead">
        <div>
          <h2>Your library</h2>
          <p>
            {videos.length} uploaded video
            {videos.length !== 1 ? 's' : ''}
          </p>
        </div>
      </section>

      {/* Video Library */}
      <section className="library">
        {loading ? (
          <div className="empty">
            <Loader2 size={36} className="spin" />
            <h3>Loading your video library…</h3>
            <p>Please wait while we connect to the API.</p>
          </div>
        ) : videos.length > 0 ? (
          videos.map((video) => (
            <article
              className="video-card"
              key={video.video_id}
            >
              <div className="preview">
                {thumbnails[video.video_id] ? (
                  <img
                    src={thumbnails[video.video_id]}
                    alt={`${video.filename} preview`}
                    className="video-thumbnail"
                  />
                ) : (
                  <Film size={32} />
                )}

                <span className={`status ${video.status}`}>
                  {video.status}
                </span>
              </div>

              <div className="cardbody">
                <h3 title={video.filename}>
                  {video.filename}
                </h3>

                <p>{fmt(video.size)}</p>

                <div className="actions">
                  <button
                    onClick={() => process(video)}
                    className="primary small"
                  >
                    <Play size={14} />
                    Process
                  </button>

                  <button
                    onClick={() => details(video)}
                    className="ghost small"
                  >
                    View outputs
                  </button>
                </div>
              </div>
            </article>
          ))
        ) : (
          <div className="empty">
            <Film size={36} />
            <h3>Your videos will appear here</h3>
            <p>Upload a video to start the pipeline.</p>
          </div>
        )}
      </section>

      {/* Video Details */}
      {selected && (
        <section className="panel details">
          <button
            className="ghost close"
            onClick={() => setSelected(null)}
          >
            Close
          </button>

          <h2>Output details: {selected.filename}</h2>

          {thumb && (
            <img
              className="thumb"
              src={thumb}
              alt="Video thumbnail"
            />
          )}

          <h3>Available resolutions</h3>

          {outputs.length > 0 ? (
            outputs.map((output, index) => {
              // IMPORTANT: Media files are served from port 8006.
              const videoUrl = `${MEDIA_API}${output.url}`

              return (
                <div
                  className="output"
                  key={`${output.resolution}-${index}`}
                >
                  <span>
                    <CheckCircle2 size={16} />
                    {output.resolution} · {fmt(output.size)}
                  </span>

                  <video
                    controls
                    preload="metadata"
                    src={videoUrl}
                    onError={(event) => {
                      console.error(
                        'Video playback failed:',
                        event.currentTarget.error,
                        'URL:',
                        videoUrl
                      )
                    }}
                  />
                </div>
              )
            })
          ) : (
            <p>
              No transcoded outputs yet. Start processing
              and refresh shortly.
            </p>
          )}
        </section>
      )}

      {/* Footer */}
      <footer>
        <span>
          <Clock3 size={14} />
          Async pipeline dashboard
        </span>

        <span>FastAPI · RabbitMQ · FFmpeg</span>
      </footer>
    </main>
  )
}
