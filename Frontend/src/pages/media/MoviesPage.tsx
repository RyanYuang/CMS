import {
  ArrowLeftOutlined,
  DeleteOutlined,
  DownOutlined,
  EditOutlined,
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
import type { UploadFile, UploadProps } from 'antd'
import { useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { assetsApi, moviesApi } from '../../services'
import type { CrewCreditEntry, Movie, MovieCreate } from '../../services'
import { extractApiErrorMessage } from '../../services/http'
import { hasPermission } from '../../utils/auth'
import { formatDate } from '../../utils/format'

type MovieFormValues = Omit<MovieCreate, 'cast' | 'genres' | 'tags'> & {
  cast?: string[]
  genres?: string[]
  stills?: string[]
  tags?: string[]
  crew_credits?: CrewCreditEntry[]
}

const MOVIE_STILL_MAX_MB = 5
const MOVIE_STILL_MAX_COUNT = 20
const ALLOWED_STILL_MIME_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp'])
const CREW_SHEET_ACCEPT = '.xlsx,.xlsm,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

const WORK_CATEGORY_OPTIONS = [
  { value: 'feature', label: '长片' },
  { value: 'short', label: '短片' },
  { value: 'media', label: '自媒体' },
] as const

const WORK_CATEGORY_LABEL: Record<string, string> = {
  feature: '长片',
  short: '短片',
  media: '自媒体',
}

const ensureStringArray = (value: unknown): string[] => {
  if (Array.isArray(value)) {
    return value.map((item) => String(item)).filter(Boolean)
  }
  if (typeof value === 'string' && value.trim()) {
    try {
      const parsed = JSON.parse(value)
      if (Array.isArray(parsed)) {
        return parsed.map((item) => String(item)).filter(Boolean)
      }
    } catch {
      return []
    }
  }
  return []
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
  const [crewSheetUploading, setCrewSheetUploading] = useState(false)
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
    form.setFieldsValue({
      title: '',
      synopsis: '',
      cast: [],
      genres: [],
      stills: [],
      tags: [],
      crew_credits: [],
      work_category: 'feature',
      pinned: false,
    })
    setModalOpen(true)
  }

  const openEdit = (movie: Movie) => {
    setEditing(movie)
    form.resetFields()
    form.setFieldsValue({
      title: movie.title,
      original_title: movie.original_title ?? undefined,
      director: movie.director ?? undefined,
      cast: ensureStringArray(movie.cast),
      genres: ensureStringArray(movie.genres),
      year: movie.year ?? undefined,
      duration_minutes: movie.duration_minutes ?? undefined,
      rating: movie.rating ?? undefined,
      work_category: movie.work_category ?? 'feature',
      synopsis: movie.synopsis,
      cover_url: movie.cover_url ?? undefined,
      production_sheet_url: movie.production_sheet_url ?? undefined,
      video_url: movie.video_url ?? undefined,
      stills: ensureStringArray(movie.stills),
      tags: ensureStringArray(movie.tags),
      crew_credits: movie.crew_credits ?? [],
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
      work_category: values.work_category ?? 'feature',
      synopsis: values.synopsis ?? '',
      cover_url: values.cover_url?.trim() || null,
      production_sheet_url: values.production_sheet_url?.trim() || null,
      video_url: values.video_url?.trim() || null,
      stills: values.stills ?? [],
      tags: values.tags ?? [],
      crew_credits: values.crew_credits ?? [],
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

  const productionSheetUrl = Form.useWatch('production_sheet_url', form)
  const crewCredits = (Form.useWatch('crew_credits', form) ?? []) as CrewCreditEntry[]

  const handleCrewSheetUpload = async (file: File) => {
    setCrewSheetUploading(true)
    try {
      if (editing) {
        const updated = await moviesApi.uploadCrewSheet(editing.id, file)
        form.setFieldValue('crew_credits', updated.crew_credits ?? [])
        setMovies((prev) => prev.map((row) => (row.id === updated.id ? updated : row)))
        message.success(`演职员表已解析并保存（${updated.crew_credits?.length ?? 0} 项）`)
        return
      }
      const parsed = await moviesApi.parseCrewSheet(file)
      form.setFieldValue('crew_credits', parsed.crew_credits)
      message.success(`演职员表已解析（${parsed.row_count} 项），保存电影后生效`)
    } catch (err) {
      message.error(extractApiErrorMessage(err))
    } finally {
      setCrewSheetUploading(false)
    }
  }

  const uploadField = (
    field: 'cover_url' | 'video_url' | 'production_sheet_url',
    accept: string,
  ): UploadProps => ({
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

  const stills = Form.useWatch('stills', form)
  const stillsSafe = ensureStringArray(stills)
  if (stills !== undefined && !Array.isArray(stills)) {
    // #region agent log
    fetch('http://127.0.0.1:7473/ingest/7897f39d-d50b-4fd8-bb95-8efbd575b269', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '308264' },
      body: JSON.stringify({
        sessionId: '308264',
        runId: 'frontend-post-fix',
        hypothesisId: 'F5',
        location: 'src/pages/media/MoviesPage.tsx:stills.watch',
        message: 'stills value is not an array, normalized',
        data: { stillsType: typeof stills, stillsValue: String(stills).slice(0, 120) },
        timestamp: Date.now(),
      }),
    }).catch(() => {})
    // #endregion
  }
  const stillUploadFileList: UploadFile[] = stillsSafe.map((url, index) => ({
    uid: `${index}-${url}`,
    name: `still-${index + 1}`,
    status: 'done',
    url,
  }))

  const moveStill = (index: number, direction: 'up' | 'down') => {
    const current = [...(form.getFieldValue('stills') ?? [])] as string[]
    const target = direction === 'up' ? index - 1 : index + 1
    if (target < 0 || target >= current.length) return
    ;[current[index], current[target]] = [current[target], current[index]]
    form.setFieldValue('stills', current)
  }

  const removeStill = (url: string) => {
    const current = [...(form.getFieldValue('stills') ?? [])] as string[]
    form.setFieldValue(
      'stills',
      current.filter((item) => item !== url),
    )
  }

  const stillUploadProps: UploadProps = {
    accept: 'image/jpeg,image/png,image/webp',
    showUploadList: false,
    beforeUpload: (file) => {
      if (!ALLOWED_STILL_MIME_TYPES.has(file.type)) {
        message.error('静帧仅支持 jpg/png/webp')
        return Upload.LIST_IGNORE
      }
      const tooLarge = file.size > MOVIE_STILL_MAX_MB * 1024 * 1024
      if (tooLarge) {
        message.error(`单张静帧不能超过 ${MOVIE_STILL_MAX_MB}MB`)
        return Upload.LIST_IGNORE
      }
      const current = (form.getFieldValue('stills') ?? []) as string[]
      if (current.length >= MOVIE_STILL_MAX_COUNT) {
        message.error(`静帧最多 ${MOVIE_STILL_MAX_COUNT} 张`)
        return Upload.LIST_IGNORE
      }
      return true
    },
    customRequest: ({ file, onSuccess, onError }) => {
      assetsApi
        .upload(file as File)
        .then((asset) => {
          const rawCurrent = form.getFieldValue('stills')
          const current = [...ensureStringArray(rawCurrent), asset.public_url]
          // #region agent log
          fetch('http://127.0.0.1:7473/ingest/7897f39d-d50b-4fd8-bb95-8efbd575b269', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-Debug-Session-Id': '308264' },
            body: JSON.stringify({
              sessionId: '308264',
              runId: 'frontend-post-fix',
              hypothesisId: 'F6',
              location: 'src/pages/media/MoviesPage.tsx:stillUploadProps.customRequest',
              message: 'append still after upload',
              data: {
                rawType: typeof rawCurrent,
                normalizedLength: current.length,
                appendedUrl: asset.public_url,
              },
              timestamp: Date.now(),
            }),
          }).catch(() => {})
          // #endregion
          form.setFieldValue('stills', current)
          onSuccess?.({})
          message.success('静帧上传成功')
        })
        .catch((err) => {
          onError?.(err as Error)
        })
    },
  }

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
    {
      title: '作品分类',
      dataIndex: 'work_category',
      width: 100,
      render: (value: string) => <Tag>{WORK_CATEGORY_LABEL[value] ?? value}</Tag>,
    },
    { title: '内容分级', dataIndex: 'rating', width: 90, render: (value: string | null) => value || '-' },
    {
      title: '制作表',
      dataIndex: 'production_sheet_url',
      width: 90,
      render: (value: string | null) => (value ? <Tag color="blue">已上传</Tag> : <Tag>无</Tag>),
    },
    {
      title: '演职员表',
      dataIndex: 'crew_credits',
      width: 100,
      render: (value: CrewCreditEntry[] | undefined) =>
        value && value.length > 0 ? <Tag color="green">{value.length} 项</Tag> : <Tag>无</Tag>,
    },
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
        <Form form={form} layout="vertical" initialValues={{ pinned: false, work_category: 'feature' }}>
          <Form.Item name="stills" hidden>
            <Input />
          </Form.Item>
          <Form.Item name="crew_credits" hidden noStyle />
          <Form.Item label="电影标题" name="title" rules={[{ required: true, message: '请输入电影标题' }]}>
            <Input maxLength={200} />
          </Form.Item>
          <Form.Item label="原始标题" name="original_title"><Input maxLength={200} /></Form.Item>
          <Form.Item label="导演" name="director"><Input maxLength={120} /></Form.Item>
          <Form.Item label="主演" name="cast"><Select mode="tags" placeholder="输入后回车添加" /></Form.Item>
          <Form.Item label="类型" name="genres"><Select mode="tags" placeholder="输入后回车添加" /></Form.Item>
          <Form.Item label="年份" name="year"><InputNumber min={1900} max={2100} style={{ width: '100%' }} /></Form.Item>
          <Form.Item label="时长（分钟）" name="duration_minutes"><InputNumber min={1} style={{ width: '100%' }} /></Form.Item>
          <Form.Item
            label="作品分类"
            name="work_category"
            rules={[{ required: true, message: '请选择作品分类' }]}
          >
            <Select options={[...WORK_CATEGORY_OPTIONS]} />
          </Form.Item>
          <Form.Item label="内容分级" name="rating" extra="如 PG-13，与长片/短片/自媒体分类无关">
            <Input maxLength={20} placeholder="可选" />
          </Form.Item>
          <Form.Item label="简介" name="synopsis"><Input.TextArea rows={4} /></Form.Item>
          <Form.Item label="封面 URL" name="cover_url"><Input placeholder="https://..." /></Form.Item>
          <Form.Item><Upload {...uploadField('cover_url', 'image/*')}><Button icon={<UploadOutlined />}>上传封面</Button></Upload></Form.Item>
          <Form.Item
            label="电影制作表"
            name="production_sheet_url"
            extra="支持 JPG / PNG / WebP 图片或 PDF，将显示在前台影片详情页"
          >
            <Input placeholder="https://..." />
          </Form.Item>
          <Form.Item>
            <Space align="start" wrap>
              <Upload {...uploadField('production_sheet_url', 'image/*,.pdf,application/pdf')}>
                <Button icon={<UploadOutlined />}>上传制作表</Button>
              </Upload>
              {productionSheetUrl ? (
                /\.pdf(\?|$)/i.test(productionSheetUrl) ? (
                  <Typography.Link href={productionSheetUrl} target="_blank" rel="noreferrer">
                    预览 PDF 制作表
                  </Typography.Link>
                ) : (
                  <Image src={productionSheetUrl} width={88} height={120} style={{ objectFit: 'cover', borderRadius: 4 }} />
                )
              ) : (
                <Typography.Text type="secondary">上传后在此预览</Typography.Text>
              )}
            </Space>
          </Form.Item>
          <Form.Item
            label="演职员表（Excel）"
            extra="格式：A 列为职位，B 列起为人员（首行可为「职位 | 人员」表头）。支持 CN / EN / JP 职位翻译。"
          >
            <Space direction="vertical" style={{ width: '100%' }} size={10}>
              <Upload
                accept={CREW_SHEET_ACCEPT}
                showUploadList={false}
                disabled={!canWrite || crewSheetUploading}
                beforeUpload={(file) => {
                  const name = file.name.toLowerCase()
                  if (!name.endsWith('.xlsx') && !name.endsWith('.xlsm')) {
                    message.error('请上传 .xlsx 或 .xlsm 文件')
                    return Upload.LIST_IGNORE
                  }
                  void handleCrewSheetUpload(file as File)
                  return false
                }}
              >
                <Button icon={<UploadOutlined />} loading={crewSheetUploading}>
                  上传并解析演职员表
                </Button>
              </Upload>
              {crewCredits.length > 0 ? (
                <Table
                  size="small"
                  pagination={false}
                  rowKey={(_, index) => String(index)}
                  dataSource={crewCredits}
                  columns={[
                    {
                      title: '职位（中）',
                      dataIndex: ['role', 'CN'],
                      width: 120,
                    },
                    {
                      title: 'EN',
                      dataIndex: ['role', 'EN'],
                      width: 120,
                    },
                    {
                      title: 'JP',
                      dataIndex: ['role', 'JP'],
                      width: 120,
                    },
                    {
                      title: '人员',
                      dataIndex: 'names',
                      render: (names: string[]) => names.join('、'),
                    },
                  ]}
                />
              ) : (
                <Typography.Text type="secondary">尚未上传演职员表</Typography.Text>
              )}
              {crewCredits.length > 0 && (
                <Button
                  danger
                  size="small"
                  onClick={() => {
                    form.setFieldValue('crew_credits', [])
                    message.info('已清空演职员表，保存电影后生效')
                  }}
                >
                  清空演职员表
                </Button>
              )}
            </Space>
          </Form.Item>
          <Form.Item label="视频 URL" name="video_url"><Input placeholder="https://..." /></Form.Item>
          <Form.Item><Upload {...uploadField('video_url', 'video/*')}><Button icon={<UploadOutlined />}>上传视频</Button></Upload></Form.Item>
          <Form.Item label={`静帧（最多 ${MOVIE_STILL_MAX_COUNT} 张，单张 <= ${MOVIE_STILL_MAX_MB}MB）`}>
            <Space direction="vertical" style={{ width: '100%' }} size={10}>
              <Upload {...stillUploadProps}>
                <Button icon={<UploadOutlined />}>上传静帧</Button>
              </Upload>
              {stillUploadFileList.length > 0 ? (
                <Space direction="vertical" style={{ width: '100%' }} size={8}>
                  {stillUploadFileList.map((file, index) => (
                    <Card key={file.uid} size="small">
                      <Space style={{ justifyContent: 'space-between', width: '100%' }} align="center">
                        <Space align="center">
                          <Image src={file.url} width={88} height={56} style={{ objectFit: 'cover', borderRadius: 4 }} />
                          <Typography.Text ellipsis style={{ maxWidth: 320 }}>{file.url}</Typography.Text>
                        </Space>
                        <Space>
                          <Button icon={<UpOutlined />} size="small" disabled={index === 0} onClick={() => moveStill(index, 'up')} />
                          <Button icon={<DownOutlined />} size="small" disabled={index === stillUploadFileList.length - 1} onClick={() => moveStill(index, 'down')} />
                          <Button icon={<DeleteOutlined />} size="small" danger onClick={() => removeStill(file.url ?? '')} />
                        </Space>
                      </Space>
                    </Card>
                  ))}
                </Space>
              ) : (
                <Typography.Text type="secondary">暂无静帧，可上传后拖动按钮调整顺序</Typography.Text>
              )}
            </Space>
          </Form.Item>
          <Form.Item label="标签" name="tags"><Select mode="tags" placeholder="输入后回车添加" /></Form.Item>
        </Form>
      </Modal>

      <Modal open={Boolean(preview)} title={preview?.title ?? '视频预览'} onCancel={() => setPreview(null)} footer={null} width={920} destroyOnHidden>
        {preview?.video_url ? <video controls autoPlay className="cms-movie-preview-video" src={preview.video_url} /> : <Empty description="暂无视频地址" />}
      </Modal>
    </Space>
  )
}
