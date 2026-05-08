import {
  ArrowLeftOutlined,
  DeleteOutlined,
  EditOutlined,
  PlayCircleOutlined,
  PlusOutlined,
  PushpinFilled,
  PushpinOutlined,
  SearchOutlined,
  UploadOutlined,
} from '@ant-design/icons'
import {
  App,
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
  Table,
  Tag,
  Typography,
  Upload,
} from 'antd'
import type { UploadProps } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { assetsApi, moviesApi } from '../../services'
import type { Movie, MovieCreate } from '../../services'
import { hasPermission } from '../../utils/auth'
import { formatDate } from '../../utils/format'

type MovieFormValues = Omit<MovieCreate, 'cast' | 'genres' | 'tags'> & {
  cast?: string[]
  genres?: string[]
  tags?: string[]
}

export function MoviesPage() {
  const navigate = useNavigate()
  const { message, modal } = App.useApp()
  const canWrite = hasPermission('movie:write')
  const canDelete = hasPermission('movie:delete')

  const [keyword, setKeyword] = useState('')
  const [movies, setMovies] = useState<Movie[]>([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [pinningId, setPinningId] = useState<number | null>(null)
  const [editing, setEditing] = useState<Movie | null>(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [preview, setPreview] = useState<Movie | null>(null)
  const [form] = Form.useForm<MovieFormValues>()

  const loadMovies = (kw?: string) => {
    setLoading(true)
    moviesApi
      .list({ keyword: kw, page: 1, page_size: 200 })
      .then((resp) => setMovies(resp.items))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    const handle = window.setTimeout(() => loadMovies(keyword.trim() || undefined), 250)
    return () => window.clearTimeout(handle)
  }, [keyword])

  const rows = useMemo(() => movies, [movies])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ title: '', synopsis: '', cast: [], genres: [], tags: [], pinned: false })
    setModalOpen(true)
  }

  const openEdit = (movie: Movie) => {
    setEditing(movie)
    form.resetFields()
    form.setFieldsValue({
      title: movie.title,
      original_title: movie.original_title ?? undefined,
      director: movie.director ?? undefined,
      cast: movie.cast,
      genres: movie.genres,
      year: movie.year ?? undefined,
      duration_minutes: movie.duration_minutes ?? undefined,
      rating: movie.rating ?? undefined,
      synopsis: movie.synopsis,
      cover_url: movie.cover_url ?? undefined,
      video_url: movie.video_url ?? undefined,
      tags: movie.tags,
      pinned: movie.pinned,
    })
    setModalOpen(true)
  }

  const submit = async () => {
    const values = await form.validateFields()
    const payload: MovieCreate = {
      title: values.title?.trim() ?? '',
      original_title: values.original_title?.trim() || null,
      director: values.director?.trim() || null,
      cast: values.cast ?? [],
      genres: values.genres ?? [],
      year: values.year ?? null,
      duration_minutes: values.duration_minutes ?? null,
      rating: values.rating?.trim() || null,
      synopsis: values.synopsis ?? '',
      cover_url: values.cover_url?.trim() || null,
      video_url: values.video_url?.trim() || null,
      tags: values.tags ?? [],
      pinned: Boolean(values.pinned),
    }
    setSubmitting(true)
    try {
      if (editing) {
        const updated = await moviesApi.update(editing.id, payload)
        setMovies((prev) => prev.map((row) => (row.id === updated.id ? updated : row)))
        message.success('电影已更新')
      } else {
        const created = await moviesApi.create(payload)
        setMovies((prev) => [created, ...prev])
        message.success('电影已创建')
      }
      setModalOpen(false)
      setEditing(null)
      form.resetFields()
    } finally {
      setSubmitting(false)
    }
  }

  const onDelete = (movie: Movie) => {
    modal.confirm({
      title: '确认删除该电影？',
      content: '此操作无法撤销，将永久删除该电影。',
      okText: '删除',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: async () => {
        setDeletingId(movie.id)
        try {
          await moviesApi.remove(movie.id)
          setMovies((prev) => prev.filter((row) => row.id !== movie.id))
          message.success('电影已删除')
        } finally {
          setDeletingId(null)
        }
      },
    })
  }

  const onTogglePin = async (movie: Movie) => {
    setPinningId(movie.id)
    try {
      const updated = await moviesApi.togglePin(movie.id)
      setMovies((prev) => prev.map((row) => (row.id === updated.id ? updated : row)))
      message.success(updated.pinned ? '已置顶' : '已取消置顶')
    } finally {
      setPinningId(null)
    }
  }

  const uploadField = (field: 'cover_url' | 'video_url', accept: string): UploadProps => ({
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
        .catch((err) => {
          onError?.(err as Error)
        })
    },
  })

  const columns = [
    {
      title: '海报',
      dataIndex: 'cover_url',
      width: 90,
      render: (_: unknown, row: Movie) =>
        row.cover_url ? <Image width={48} height={64} src={row.cover_url} style={{ objectFit: 'cover', borderRadius: 6 }} /> : <Tag>无海报</Tag>,
    },
    { title: '标题', dataIndex: 'title', render: (_: unknown, row: Movie) => <Typography.Text strong>{row.title}</Typography.Text> },
    { title: '年份', dataIndex: 'year', width: 90, render: (value: number | null) => value ?? '-' },
    { title: '导演', dataIndex: 'director', width: 160, render: (value: string | null) => value || '-' },
    { title: '类型', dataIndex: 'genres', render: (value: string[]) => <Space wrap>{value.map((g) => <Tag key={g}>{g}</Tag>)}</Space> },
    { title: '时长', dataIndex: 'duration_minutes', width: 90, render: (value: number | null) => (value ? `${value}分钟` : '-') },
    { title: '分级', dataIndex: 'rating', width: 90, render: (value: string | null) => value || '-' },
    {
      title: '状态',
      dataIndex: 'pinned',
      width: 90,
      render: (value: boolean) => (value ? <Tag color="orange">置顶</Tag> : <Tag>普通</Tag>),
    },
    { title: '更新时间', dataIndex: 'updated_at', width: 160, render: (value: string) => formatDate(value) },
    {
      title: '操作',
      key: 'actions',
      width: 200,
      render: (_: unknown, row: Movie) => (
        <Space>
          <Button icon={<PlayCircleOutlined />} size="small" onClick={() => setPreview(row)} disabled={!row.video_url}>
            预览
          </Button>
          <Button icon={<EditOutlined />} size="small" onClick={() => openEdit(row)} disabled={!canWrite}>
            编辑
          </Button>
          <Button
            icon={row.pinned ? <PushpinFilled /> : <PushpinOutlined />}
            size="small"
            onClick={() => void onTogglePin(row)}
            loading={pinningId === row.id}
            disabled={!canWrite}
          />
          <Button danger icon={<DeleteOutlined />} size="small" loading={deletingId === row.id} onClick={() => onDelete(row)} disabled={!canDelete} />
        </Space>
      ),
    },
  ]

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card className="cms-card">
        <Space style={{ justifyContent: 'space-between', width: '100%' }} align="start">
          <Space align="center" size={8}>
            <Button type="text" icon={<ArrowLeftOutlined />} onClick={() => navigate('/media')} />
            <Space direction="vertical" size={2}>
              <Typography.Title level={3} style={{ margin: 0 }}>电影管理</Typography.Title>
              <Typography.Paragraph type="secondary" style={{ margin: 0 }}>管理您的视频和影片资源</Typography.Paragraph>
            </Space>
          </Space>
          <Button type="primary" icon={<PlusOutlined />} disabled={!canWrite} onClick={openCreate}>添加电影</Button>
        </Space>
      </Card>

      <Card className="cms-card">
        <Input allowClear size="large" prefix={<SearchOutlined />} placeholder="搜索电影名称、导演、类型或标签..." value={keyword} onChange={(e) => setKeyword(e.target.value)} />
      </Card>

      <Card className="cms-card">
        <Table<Movie>
          rowKey="id"
          loading={loading}
          columns={columns}
          dataSource={rows}
          pagination={false}
          locale={{ emptyText: <Empty description="暂无电影数据" /> }}
        />
      </Card>

      <Modal open={modalOpen} title={editing ? '编辑电影' : '添加电影'} onCancel={() => setModalOpen(false)} onOk={() => void submit()} confirmLoading={submitting} width={760} destroyOnHidden>
        <Form form={form} layout="vertical" initialValues={{ pinned: false }}>
          <Form.Item label="电影标题" name="title" rules={[{ required: true, message: '请输入电影标题' }]}>
            <Input maxLength={200} />
          </Form.Item>
          <Form.Item label="原始标题" name="original_title"><Input maxLength={200} /></Form.Item>
          <Form.Item label="导演" name="director"><Input maxLength={120} /></Form.Item>
          <Form.Item label="主演" name="cast"><Select mode="tags" placeholder="输入后回车添加" /></Form.Item>
          <Form.Item label="类型" name="genres"><Select mode="tags" placeholder="输入后回车添加" /></Form.Item>
          <Form.Item label="年份" name="year"><InputNumber min={1900} max={2100} style={{ width: '100%' }} /></Form.Item>
          <Form.Item label="时长（分钟）" name="duration_minutes"><InputNumber min={1} style={{ width: '100%' }} /></Form.Item>
          <Form.Item label="分级" name="rating"><Input maxLength={20} /></Form.Item>
          <Form.Item label="简介" name="synopsis"><Input.TextArea rows={4} /></Form.Item>
          <Form.Item label="封面 URL" name="cover_url"><Input placeholder="https://..." /></Form.Item>
          <Form.Item><Upload {...uploadField('cover_url', 'image/*')}><Button icon={<UploadOutlined />}>上传封面</Button></Upload></Form.Item>
          <Form.Item label="视频 URL" name="video_url"><Input placeholder="https://..." /></Form.Item>
          <Form.Item><Upload {...uploadField('video_url', 'video/*')}><Button icon={<UploadOutlined />}>上传视频</Button></Upload></Form.Item>
          <Form.Item label="标签" name="tags"><Select mode="tags" placeholder="输入后回车添加" /></Form.Item>
        </Form>
      </Modal>

      <Modal open={Boolean(preview)} title={preview?.title ?? '视频预览'} onCancel={() => setPreview(null)} footer={null} width={920} destroyOnHidden>
        {preview?.video_url ? <video controls autoPlay className="cms-movie-preview-video" src={preview.video_url} /> : <Empty description="暂无视频地址" />}
      </Modal>
    </Space>
  )
}
