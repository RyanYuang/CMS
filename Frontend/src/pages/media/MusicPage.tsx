import {
  ArrowLeftOutlined,
  DeleteOutlined,
  DownOutlined,
  EditOutlined,
  PauseCircleOutlined,
  PlayCircleOutlined,
  PlusOutlined,
  PushpinFilled,
  PushpinOutlined,
  SearchOutlined,
  UpOutlined,
  UploadOutlined,
} from '@ant-design/icons'
import {
  App,
  Avatar,
  Button,
  Card,
  Empty,
  Form,
  Image,
  Input,
  InputNumber,
  Modal,
  Select,
  Space,
  Tag,
  Typography,
  Upload,
} from 'antd'
import type { UploadFile, UploadProps } from 'antd'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { assetsApi, musicApi } from '../../services'
import type { MusicStory, MusicTrack, MusicTrackCreate } from '../../services'
import { hasPermission } from '../../utils/auth'
import { formatDate } from '../../utils/format'

const NETEASE_IFRAME_SRC_RE = /<iframe\b[^>]*\bsrc=(['"])([^"']+)\1[^>]*>\s*<\/iframe>/i
const PHOTO_MAX_MB = 5
const PHOTO_MAX_COUNT = 20
const ALLOWED_PHOTO_MIME_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp'])

type MusicFormValues = MusicTrackCreate & {
  photos?: string[]
  story?: MusicStory
}

const ensureStringArray = (value: unknown): string[] => {
  if (Array.isArray(value)) {
    return value.map((item) => String(item)).filter(Boolean)
  }
  return []
}

function extractIframeSrc(value?: string | null): string | null {
  if (!value) return null
  const match = value.trim().match(NETEASE_IFRAME_SRC_RE)
  if (!match?.[2]) return null
  const src = match[2].trim()
  if (!src) return null
  if (src.startsWith('//')) return `https:${src}`
  return src
}

function normalizeStory(value: unknown): MusicStory {
  if (!value || typeof value !== 'object') return {}
  const raw = value as Record<string, unknown>
  const story: MusicStory = {}
  if (typeof raw.CN === 'string' && raw.CN.trim()) story.CN = raw.CN.trim()
  if (typeof raw.EN === 'string' && raw.EN.trim()) story.EN = raw.EN.trim()
  if (typeof raw.JP === 'string' && raw.JP.trim()) story.JP = raw.JP.trim()
  return story
}

export function MusicPage() {
  const navigate = useNavigate()
  const { message, modal } = App.useApp()
  const canWrite = hasPermission('music:write')
  const canDelete = hasPermission('music:delete')

  const [keyword, setKeyword] = useState('')
  const [rows, setRows] = useState<MusicTrack[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<MusicTrack | null>(null)
  const [playing, setPlaying] = useState<MusicTrack | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [pinningId, setPinningId] = useState<number | null>(null)
  const [form] = Form.useForm<MusicFormValues>()

  const loadMusic = (kw?: string) => {
    setLoading(true)
    musicApi
      .list({ keyword: kw, page: 1, page_size: 200 })
      .then((resp) => setRows(resp.items))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    const handle = window.setTimeout(() => loadMusic(keyword.trim() || undefined), 250)
    return () => window.clearTimeout(handle)
  }, [keyword])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ title: '', tags: [], photos: [], story: {}, pinned: false })
    setModalOpen(true)
  }

  const openEdit = (item: MusicTrack) => {
    setEditing(item)
    form.resetFields()
    form.setFieldsValue({
      title: item.title,
      artist: item.artist ?? undefined,
      album: item.album ?? undefined,
      genre: item.genre ?? undefined,
      year: item.year ?? undefined,
      duration_seconds: item.duration_seconds ?? undefined,
      cover_url: item.cover_url ?? undefined,
      audio_url: item.audio_url ?? undefined,
      photos: ensureStringArray(item.photos),
      story: normalizeStory(item.story),
      tags: item.tags,
      pinned: item.pinned,
    })
    setModalOpen(true)
  }

  const submit = async () => {
    const values = await form.validateFields()
    const story = normalizeStory(values.story)
    const payload: MusicTrackCreate = {
      title: values.title?.trim() ?? '',
      artist: values.artist?.trim() || null,
      album: values.album?.trim() || null,
      genre: values.genre?.trim() || null,
      year: values.year ?? null,
      duration_seconds: values.duration_seconds ?? null,
      cover_url: values.cover_url?.trim() || null,
      audio_url: values.audio_url?.trim() || null,
      photos: values.photos ?? [],
      story,
      tags: values.tags ?? [],
      pinned: Boolean(values.pinned),
    }
    setSubmitting(true)
    try {
      if (editing) {
        const updated = await musicApi.update(editing.id, payload)
        setRows((prev) => prev.map((row) => (row.id === updated.id ? updated : row)))
        message.success('音乐已更新')
      } else {
        const created = await musicApi.create(payload)
        setRows((prev) => [created, ...prev])
        message.success('音乐已创建')
      }
      setModalOpen(false)
      setEditing(null)
      form.resetFields()
    } finally {
      setSubmitting(false)
    }
  }

  const onDelete = (item: MusicTrack) => {
    modal.confirm({
      title: '确认删除该歌曲？',
      content: '此操作无法撤销，将永久删除该歌曲。',
      okText: '删除',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: async () => {
        setDeletingId(item.id)
        try {
          await musicApi.remove(item.id)
          setRows((prev) => prev.filter((row) => row.id !== item.id))
          message.success('歌曲已删除')
        } finally {
          setDeletingId(null)
        }
      },
    })
  }

  const onTogglePin = async (item: MusicTrack) => {
    setPinningId(item.id)
    try {
      const updated = await musicApi.togglePin(item.id)
      setRows((prev) => prev.map((row) => (row.id === updated.id ? updated : row)))
      message.success(updated.pinned ? '已置顶' : '已取消置顶')
    } finally {
      setPinningId(null)
    }
  }

  const uploadField = (field: 'cover_url' | 'audio_url', accept: string): UploadProps => ({
    accept,
    showUploadList: false,
    customRequest: ({ file, onSuccess, onError }) => {
      assetsApi
        .upload(file as File)
        .then((asset) => {
          form.setFieldValue(field, asset.public_url)
          onSuccess?.({})
          message.success('上传成功')
        })
        .catch((err) => onError?.(err as Error))
    },
  })

  const photos = Form.useWatch('photos', form)
  const photosSafe = ensureStringArray(photos)
  const coverUrl = Form.useWatch('cover_url', form)

  const photoUploadFileList: UploadFile[] = photosSafe.map((url, index) => ({
    uid: `${url}-${index}`,
    name: url.split('/').pop() ?? `photo-${index + 1}`,
    status: 'done',
    url,
  }))

  const movePhoto = (index: number, direction: 'up' | 'down') => {
    const current = [...(form.getFieldValue('photos') ?? [])] as string[]
    const target = direction === 'up' ? index - 1 : index + 1
    if (target < 0 || target >= current.length) return
    ;[current[index], current[target]] = [current[target], current[index]]
    form.setFieldValue('photos', current)
  }

  const removePhoto = (url: string) => {
    const current = (form.getFieldValue('photos') ?? []) as string[]
    form.setFieldValue(
      'photos',
      current.filter((item) => item !== url),
    )
  }

  const photoUploadProps: UploadProps = {
    accept: 'image/*',
    showUploadList: false,
    beforeUpload: (file) => {
      if (!ALLOWED_PHOTO_MIME_TYPES.has(file.type)) {
        message.error('照片仅支持 JPG / PNG / WebP')
        return Upload.LIST_IGNORE
      }
      const tooLarge = file.size > PHOTO_MAX_MB * 1024 * 1024
      if (tooLarge) {
        message.error(`单张照片不能超过 ${PHOTO_MAX_MB}MB`)
        return Upload.LIST_IGNORE
      }
      const current = (form.getFieldValue('photos') ?? []) as string[]
      if (current.length >= PHOTO_MAX_COUNT) {
        message.error(`照片最多 ${PHOTO_MAX_COUNT} 张`)
        return Upload.LIST_IGNORE
      }
      return true
    },
    customRequest: ({ file, onSuccess, onError }) => {
      assetsApi
        .upload(file as File)
        .then((asset) => {
          const current = ensureStringArray(form.getFieldValue('photos'))
          form.setFieldValue('photos', [...current, asset.public_url])
          onSuccess?.({})
          message.success('照片上传成功')
        })
        .catch((err) => onError?.(err as Error))
    },
  }

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card className="cms-card">
        <Space style={{ justifyContent: 'space-between', width: '100%' }} align="start">
          <Space align="center" size={8}>
            <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => navigate('/media')} />
            <Space direction="vertical" size={2}>
              <Typography.Title level={3} style={{ margin: 0 }}>音乐管理</Typography.Title>
              <Typography.Paragraph type="secondary" style={{ margin: 0 }}>管理您的音频和音乐文件</Typography.Paragraph>
            </Space>
          </Space>
          <Button type="primary" icon={<PlusOutlined />} disabled={!canWrite} onClick={openCreate}>添加歌曲</Button>
        </Space>
      </Card>

      <Card className="cms-card">
        <Input allowClear size="large" prefix={<SearchOutlined />} placeholder="搜索歌曲、艺人、专辑或标签..." value={keyword} onChange={(e) => setKeyword(e.target.value)} />
      </Card>

      <Card className="cms-card">
        {loading ? <Typography.Text type="secondary">加载中...</Typography.Text> : null}
        {!loading && rows.length === 0 ? (
          <Empty description="暂无歌曲数据" />
        ) : (
          <Space direction="vertical" size={10} style={{ width: '100%' }}>
            {rows.map((item) => (
              <Card key={item.id} size="small" className="cms-music-row-card">
                <Space style={{ justifyContent: 'space-between', width: '100%' }} align="center">
                  <Space>
                    <Button
                      type="text"
                      icon={playing?.id === item.id ? <PauseCircleOutlined /> : <PlayCircleOutlined />}
                      onClick={() => setPlaying(playing?.id === item.id ? null : item)}
                      disabled={!item.audio_url}
                    />
                    <Avatar shape="square" size={54} src={item.cover_url ?? undefined}>{item.title.slice(0, 1)}</Avatar>
                    <Space direction="vertical" size={1}>
                      <Typography.Text strong>{item.title}</Typography.Text>
                      <Typography.Text type="secondary">{item.artist || '未知艺人'} · {item.album || '未知专辑'}</Typography.Text>
                      {ensureStringArray(item.photos).length > 0 ? (
                        <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                          {ensureStringArray(item.photos).length} 张照片
                        </Typography.Text>
                      ) : null}
                    </Space>
                  </Space>
                  <Space wrap>
                    {item.genre ? <Tag>{item.genre}</Tag> : null}
                    {item.duration_seconds ? <Tag>{Math.floor(item.duration_seconds / 60)}:{String(item.duration_seconds % 60).padStart(2, '0')}</Tag> : null}
                    {item.pinned ? <Tag color="orange">置顶</Tag> : null}
                    <Typography.Text type="secondary">更新于 {formatDate(item.updated_at)}</Typography.Text>
                    <Button icon={<EditOutlined />} size="small" disabled={!canWrite} onClick={() => openEdit(item)}>编辑</Button>
                    <Button icon={item.pinned ? <PushpinFilled /> : <PushpinOutlined />} size="small" loading={pinningId === item.id} disabled={!canWrite} onClick={() => void onTogglePin(item)} />
                    <Button danger icon={<DeleteOutlined />} size="small" loading={deletingId === item.id} disabled={!canDelete} onClick={() => onDelete(item)} />
                  </Space>
                </Space>
              </Card>
            ))}
          </Space>
        )}
      </Card>

      <Modal open={modalOpen} title={editing ? '编辑歌曲' : '添加歌曲'} onCancel={() => setModalOpen(false)} onOk={() => void submit()} confirmLoading={submitting} width={760} destroyOnHidden>
        <Form form={form} layout="vertical" initialValues={{ pinned: false, photos: [], story: {} }}>
          <Form.Item name="photos" hidden>
            <Input />
          </Form.Item>
          <Form.Item label="歌曲标题" name="title" rules={[{ required: true, message: '请输入歌曲标题' }]}><Input maxLength={200} /></Form.Item>
          <Form.Item label="艺人" name="artist"><Input maxLength={200} /></Form.Item>
          <Form.Item
            label="专辑"
            name="album"
            extra="可填普通专辑名。若需展示网易云播放器，请在下方“音频 URL”粘贴 iframe 代码。"
          >
            <Input maxLength={200} placeholder="专辑名称（可选）" />
          </Form.Item>
          <Form.Item label="流派" name="genre"><Input maxLength={80} /></Form.Item>
          <Form.Item label="年份" name="year"><InputNumber min={1900} max={2100} style={{ width: '100%' }} /></Form.Item>
          <Form.Item label="时长（秒）" name="duration_seconds"><InputNumber min={1} style={{ width: '100%' }} /></Form.Item>
          <Form.Item label="专辑封面" name="cover_url">
            <Input placeholder="https://..." />
          </Form.Item>
          <Form.Item>
            <Space align="start" wrap>
              <Upload {...uploadField('cover_url', 'image/*')}>
                <Button icon={<UploadOutlined />}>上传封面</Button>
              </Upload>
              {coverUrl ? (
                <Image src={coverUrl} width={88} height={88} style={{ objectFit: 'cover', borderRadius: 4 }} />
              ) : (
                <Typography.Text type="secondary">上传后在此预览</Typography.Text>
              )}
            </Space>
          </Form.Item>
          <Form.Item
            label={`照片集（最多 ${PHOTO_MAX_COUNT} 张，单张 <= ${PHOTO_MAX_MB}MB）`}
            extra="将显示在音乐详情页的照片集区域"
          >
            <Space direction="vertical" style={{ width: '100%' }} size={10}>
              <Upload {...photoUploadProps}>
                <Button icon={<UploadOutlined />}>上传照片</Button>
              </Upload>
              {photoUploadFileList.length > 0 ? (
                <Space direction="vertical" style={{ width: '100%' }} size={8}>
                  {photoUploadFileList.map((file, index) => (
                    <Card key={file.uid} size="small">
                      <Space style={{ justifyContent: 'space-between', width: '100%' }} align="center">
                        <Space align="center">
                          <Image src={file.url} width={88} height={66} style={{ objectFit: 'cover', borderRadius: 4 }} />
                          <Typography.Text ellipsis style={{ maxWidth: 320 }}>{file.url}</Typography.Text>
                        </Space>
                        <Space>
                          <Button icon={<UpOutlined />} size="small" disabled={index === 0} onClick={() => movePhoto(index, 'up')} />
                          <Button icon={<DownOutlined />} size="small" disabled={index === photoUploadFileList.length - 1} onClick={() => movePhoto(index, 'down')} />
                          <Button icon={<DeleteOutlined />} size="small" danger onClick={() => removePhoto(file.url ?? '')} />
                        </Space>
                      </Space>
                    </Card>
                  ))}
                </Space>
              ) : (
                <Typography.Text type="secondary">暂无照片，可上传多张展示在音乐详情页</Typography.Text>
              )}
            </Space>
          </Form.Item>
          <Form.Item label="故事（中文）" name={['story', 'CN']}>
            <Input.TextArea rows={4} placeholder="音乐背后的故事（中文）" />
          </Form.Item>
          <Form.Item label="故事（英文）" name={['story', 'EN']}>
            <Input.TextArea rows={3} placeholder="Optional English story" />
          </Form.Item>
          <Form.Item label="故事（日文）" name={['story', 'JP']}>
            <Input.TextArea rows={3} placeholder="日本語のストーリー（任意）" />
          </Form.Item>
          <Form.Item
            label="音频 URL"
            name="audio_url"
            extra="支持两种格式：1) 直连音频 URL；2) 网易云 iframe 代码（推荐）。前台会自动识别并渲染播放器。"
          >
            <Input placeholder="https://... 或 <iframe ...></iframe>" />
          </Form.Item>
          <Form.Item><Upload {...uploadField('audio_url', 'audio/*')}><Button icon={<UploadOutlined />}>上传音频</Button></Upload></Form.Item>
          <Form.Item label="标签" name="tags"><Select mode="tags" placeholder="输入后回车添加" /></Form.Item>
        </Form>
      </Modal>

      <Modal open={Boolean(playing)} title={playing?.title ?? '播放'} onCancel={() => setPlaying(null)} footer={null} destroyOnHidden>
        {(() => {
          const iframeSrc = extractIframeSrc(playing?.audio_url)
          if (iframeSrc) {
            return (
              <iframe
                title="netease-player"
                src={iframeSrc}
                width={330}
                height={450}
                frameBorder="no"
                style={{ width: '100%', border: 0 }}
                allow="autoplay"
              />
            )
          }
          return playing?.audio_url ? (
            <audio src={playing.audio_url} controls autoPlay style={{ width: '100%' }} />
          ) : (
            <Empty description="暂无音频地址" />
          )
        })()}
      </Modal>
    </Space>
  )
}
