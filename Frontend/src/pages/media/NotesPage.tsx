import {
  ArrowLeftOutlined,
  DeleteOutlined,
  FileTextOutlined,
  PlusOutlined,
  PushpinFilled,
  PushpinOutlined,
  SearchOutlined,
} from '@ant-design/icons'
import {
  App,
  Button,
  Card,
  Checkbox,
  Col,
  DatePicker,
  Empty,
  Form,
  Input,
  Modal,
  Row,
  Space,
  Spin,
  Tag,
  Typography,
} from 'antd'
import dayjs, { type Dayjs } from 'dayjs'
import { useCallback, useEffect, useMemo, useState } from 'react'
import ReactMarkdown from 'react-markdown'
import { useNavigate } from 'react-router-dom'
import remarkGfm from 'remark-gfm'
import { notesApi } from '../../services'
import type { Note } from '../../services'
import { hasPermission } from '../../utils/auth'
import { formatDate } from '../../utils/format'

type NoteFormValues = {
  title: string
  content: string
  category?: string
  writtenAt?: Dayjs | null
  tagsText?: string
  pinned?: boolean
}

function tagsToText(tags: string[] | null | undefined): string {
  return (tags ?? []).join(', ')
}

function textToTags(value: string | undefined): string[] {
  if (!value) {
    return []
  }
  return value
    .split(',')
    .map((t) => t.trim())
    .filter(Boolean)
}

export function NotesPage() {
  const navigate = useNavigate()
  const { message, modal } = App.useApp()
  const canWrite = hasPermission('note:write')
  const canDelete = hasPermission('note:delete')

  const [keyword, setKeyword] = useState('')
  const [notes, setNotes] = useState<Note[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [editing, setEditing] = useState<Note | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [pinningId, setPinningId] = useState<number | null>(null)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [form] = Form.useForm<NoteFormValues>()
  const watchedContent = Form.useWatch('content', form)

  const sorted = useMemo(() => {
    const list = [...notes]
    list.sort((a, b) => {
      if (a.pinned !== b.pinned) {
        return a.pinned ? -1 : 1
      }
      const aDate = a.written_at ?? a.created_at
      const bDate = b.written_at ?? b.created_at
      return new Date(bDate).getTime() - new Date(aDate).getTime()
    })
    return list
  }, [notes])

  const loadNotes = useCallback(
    (kw?: string) => {
      setLoading(true)
      notesApi
        .list({ keyword: kw, page: 1, page_size: 200 })
        .then((resp) => setNotes(resp.items))
        .finally(() => setLoading(false))
    },
    [],
  )

  useEffect(() => {
    const handle = window.setTimeout(() => {
      loadNotes(keyword.trim() || undefined)
    }, 250)
    return () => window.clearTimeout(handle)
  }, [keyword, loadNotes])

  const openCreate = () => {
    setEditing(null)
    form.resetFields()
    form.setFieldsValue({ title: '', content: '', category: '', tagsText: '', pinned: false })
    setModalOpen(true)
  }

  const openEdit = (note: Note) => {
    setEditing(note)
    form.resetFields()
    form.setFieldsValue({
      title: note.title,
      content: note.content,
      category: note.category ?? '',
      writtenAt: note.written_at ? dayjs(note.written_at) : null,
      tagsText: tagsToText(note.tags),
      pinned: note.pinned,
    })
    setModalOpen(true)
  }

  const submit = async () => {
    const values = await form.validateFields()
    const payload = {
      title: values.title.trim(),
      content: values.content,
      category: values.category?.trim() ? values.category.trim() : null,
      written_at: values.writtenAt ? values.writtenAt.startOf('day').toISOString() : null,
      pinned: Boolean(values.pinned),
      tags: textToTags(values.tagsText),
    }
    setSubmitting(true)
    try {
      if (editing) {
        const updated = await notesApi.update(editing.id, payload)
        setNotes((prev) => prev.map((n) => (n.id === updated.id ? updated : n)))
        message.success('已保存')
      } else {
        const created = await notesApi.create(payload)
        setNotes((prev) => [created, ...prev])
        message.success('笔记已创建')
      }
      setModalOpen(false)
      form.resetFields()
      setEditing(null)
    } finally {
      setSubmitting(false)
    }
  }

  const togglePin = async (note: Note) => {
    setPinningId(note.id)
    try {
      const updated = await notesApi.togglePin(note.id)
      setNotes((prev) => prev.map((n) => (n.id === updated.id ? updated : n)))
      message.success(updated.pinned ? '已置顶' : '已取消置顶')
    } finally {
      setPinningId(null)
    }
  }

  const confirmDelete = (note: Note) => {
    modal.confirm({
      title: '确认删除该笔记？',
      content: '此操作无法撤销，将永久删除该笔记。',
      okText: '删除',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: async () => {
        setDeletingId(note.id)
        try {
          await notesApi.remove(note.id)
          setNotes((prev) => prev.filter((n) => n.id !== note.id))
          message.success('笔记已删除')
        } finally {
          setDeletingId(null)
        }
      },
    })
  }

  const renderEmpty = () => (
    <Card className="cms-card" style={{ padding: '48px 0' }}>
      <Empty
        image={<FileTextOutlined style={{ fontSize: 64, color: '#bfbfbf' }} />}
        imageStyle={{ height: 80 }}
        description={
          <Space direction="vertical" size={4}>
            <Typography.Text>{keyword.trim() ? '没有匹配的笔记' : '还没有笔记'}</Typography.Text>
            <Typography.Text type="secondary">
              {keyword.trim() ? '换个关键词试试' : '点击下方按钮新建第一条笔记'}
            </Typography.Text>
          </Space>
        }
      >
        {!keyword.trim() && canWrite ? (
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreate}>
            新建第一条笔记
          </Button>
        ) : null}
      </Empty>
    </Card>
  )

  return (
    <Space direction="vertical" size={16} style={{ width: '100%' }}>
      <Card className="cms-card">
        <Space style={{ justifyContent: 'space-between', width: '100%' }} align="start">
          <Space align="center" size={8}>
            <Button
              type="text"
              icon={<ArrowLeftOutlined />}
              onClick={() => navigate('/media')}
              aria-label="返回"
            />
            <Space direction="vertical" size={2}>
              <Typography.Title level={3} style={{ margin: 0 }}>
                笔记管理
              </Typography.Title>
              <Typography.Paragraph type="secondary" style={{ margin: 0 }}>
                管理您的文档和笔记内容
              </Typography.Paragraph>
            </Space>
          </Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={openCreate}
            disabled={!canWrite}
          >
            新建笔记
          </Button>
        </Space>
      </Card>

      <Card className="cms-card">
        <Input
          allowClear
          size="large"
          prefix={<SearchOutlined />}
          placeholder="搜索笔记标题、内容或标签..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
        />
      </Card>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 48 }}>
          <Spin />
        </div>
      ) : sorted.length === 0 ? (
        renderEmpty()
      ) : (
        <Row gutter={[16, 16]}>
          {sorted.map((note) => (
            <Col key={note.id} xs={24} md={12} lg={8} xl={6}>
              <NoteCard
                note={note}
                canWrite={canWrite}
                canDelete={canDelete}
                pinning={pinningId === note.id}
                deleting={deletingId === note.id}
                onOpen={() => openEdit(note)}
                onPin={() => void togglePin(note)}
                onDelete={() => confirmDelete(note)}
              />
            </Col>
          ))}
        </Row>
      )}

      <Modal
        width={720}
        title={editing ? '编辑笔记' : '新建笔记'}
        open={modalOpen}
        onCancel={() => {
          setModalOpen(false)
          form.resetFields()
          setEditing(null)
        }}
        onOk={() => void submit()}
        confirmLoading={submitting}
        okText={editing ? '保存' : '创建'}
        cancelText="取消"
        destroyOnHidden
        maskClosable={false}
      >
        <Form form={form} layout="vertical" initialValues={{ pinned: false }}>
          <Form.Item
            label="标题"
            name="title"
            rules={[
              { required: true, message: '请输入标题' },
              { max: 200, message: '标题最多 200 个字符' },
            ]}
          >
            <Input placeholder="给你的笔记起个标题" maxLength={200} />
          </Form.Item>
          <Form.Item
            label="内容（支持 Markdown）"
            name="content"
            rules={[{ required: true, message: '请输入内容' }]}
          >
            <Input.TextArea
              rows={10}
              placeholder={'# 标题\n\n在这里写下你的想法...\n\n- 支持 **Markdown** 格式\n- 列表、代码块、链接等'}
              style={{ fontFamily: 'ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace' }}
            />
          </Form.Item>
          {watchedContent ? (
            <Form.Item label="预览">
              <Card size="small" style={{ background: 'var(--ant-color-fill-quaternary, #fafafa)' }}>
                <div className="cms-markdown">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{watchedContent}</ReactMarkdown>
                </div>
              </Card>
            </Form.Item>
          ) : null}
          <Form.Item
            label="写作日期"
            name="writtenAt"
            extra="可选。填写后前台文学页将显示该日期；不填则使用创建日期。"
          >
            <DatePicker style={{ width: '100%' }} format="YYYY-MM-DD" />
          </Form.Item>
          <Form.Item label="分类" name="category" rules={[{ max: 80, message: '分类最多 80 个字符' }]}>
            <Input placeholder="例如：学习 / 工作 / 灵感" maxLength={80} />
          </Form.Item>
          <Form.Item label="标签（逗号分隔）" name="tagsText">
            <Input placeholder="例如：技术, React, 前端" />
          </Form.Item>
          <Form.Item name="pinned" valuePropName="checked">
            <Checkbox>置顶此笔记</Checkbox>
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}

type NoteCardProps = {
  note: Note
  canWrite: boolean
  canDelete: boolean
  pinning: boolean
  deleting: boolean
  onOpen: () => void
  onPin: () => void
  onDelete: () => void
}

function NoteCard({ note, canWrite, canDelete, pinning, deleting, onOpen, onPin, onDelete }: NoteCardProps) {
  const [hover, setHover] = useState(false)

  const stop = (e: React.MouseEvent) => {
    e.stopPropagation()
  }

  return (
    <Card
      hoverable
      className="cms-card cms-note-card"
      onClick={onOpen}
      onMouseEnter={() => setHover(true)}
      onMouseLeave={() => setHover(false)}
      style={{ height: '100%' }}
      styles={{ body: { display: 'flex', flexDirection: 'column', gap: 8, height: '100%' } }}
    >
      <Space style={{ justifyContent: 'space-between', alignItems: 'start', width: '100%' }} align="start">
        <Typography.Title level={5} style={{ margin: 0, flex: 1 }} ellipsis={{ rows: 2 }}>
          {note.title || '未命名笔记'}
        </Typography.Title>
        <Space size={4} onClick={stop}>
          {note.pinned ? (
            <PushpinFilled
              style={{ color: '#fa8c16', fontSize: 16 }}
              aria-label="已置顶"
            />
          ) : null}
          {(hover || note.pinned) && canWrite ? (
            <Button
              type="text"
              size="small"
              icon={note.pinned ? <PushpinFilled style={{ color: '#fa8c16' }} /> : <PushpinOutlined />}
              loading={pinning}
              onClick={(e) => {
                stop(e)
                onPin()
              }}
              aria-label={note.pinned ? '取消置顶' : '置顶'}
            />
          ) : null}
          {hover && canDelete ? (
            <Button
              type="text"
              size="small"
              danger
              icon={<DeleteOutlined />}
              loading={deleting}
              onClick={(e) => {
                stop(e)
                onDelete()
              }}
              aria-label="删除"
            />
          ) : null}
        </Space>
      </Space>

      <div
        className="cms-markdown cms-note-preview"
        style={{
          color: 'rgba(0,0,0,0.65)',
          fontSize: 13,
          lineHeight: 1.6,
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden',
        }}
      >
        {note.content?.trim() ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{note.content}</ReactMarkdown>
        ) : (
          <Typography.Text type="secondary">（暂无内容）</Typography.Text>
        )}
      </div>

      <Space size={[4, 4]} wrap style={{ marginTop: 'auto' }}>
        {note.category ? <Tag color="default" bordered>{note.category}</Tag> : null}
        {note.tags?.map((t) => (
          <Tag key={t}>{t}</Tag>
        ))}
      </Space>
      <Typography.Text type="secondary" style={{ fontSize: 12 }}>
        {note.written_at ? `写作于 ${formatDate(note.written_at)}` : `创建于 ${formatDate(note.created_at)}`}
        {note.written_at && note.updated_at !== note.written_at
          ? ` · 更新于 ${formatDate(note.updated_at)}`
          : null}
      </Typography.Text>
    </Card>
  )
}
