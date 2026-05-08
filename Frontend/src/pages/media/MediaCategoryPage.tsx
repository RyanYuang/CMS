import { DeleteOutlined, EditOutlined, UploadOutlined } from '@ant-design/icons'
import { Button, Card, Col, Form, Image, Input, Modal, Pagination, Popconfirm, Row, Select, Space, Spin, Typography, Upload, message } from 'antd'
import type { UploadProps } from 'antd'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useLocation } from 'react-router-dom'
import { assetsApi } from '../../services'
import type { AssetItem, AssetKind } from '../../services'
import { hasPermission } from '../../utils/auth'

const categoryMeta: Record<string, { title: string; description: string; kind: AssetKind }> = {
  photos: { title: '照片', description: '管理图片和摄影资源', kind: 'image' },
  movies: { title: '电影', description: '管理视频与影片文件', kind: 'video' },
  music: { title: '音乐', description: '管理音频与音乐资源', kind: 'audio' },
  notes: { title: '笔记', description: '管理文档与笔记内容', kind: 'document' },
}

export function MediaCategoryPage() {
  const location = useLocation()
  const category = useMemo(() => location.pathname.split('/').at(-1) ?? 'photos', [location.pathname])
  const isNotesCategory = category === 'notes'
  const meta = categoryMeta[category] ?? categoryMeta.photos
  const [kind, setKind] = useState<AssetKind>(meta.kind)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(12)
  const [rows, setRows] = useState<AssetItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [noteModalOpen, setNoteModalOpen] = useState(false)
  const [creatingNote, setCreatingNote] = useState(false)
  const [noteForm] = Form.useForm<{ title: string; content: string }>()
  const canUpload = hasPermission('asset:write')
  const canDelete = hasPermission('asset:delete')

  const loadAssets = useCallback((nextPage = page, nextSize = pageSize, nextKind = kind) => {
    assetsApi
      .list({ page: nextPage, page_size: nextSize, kind: nextKind })
      .then((resp) => {
        setRows(resp.items)
        setTotal(resp.meta.total)
      })
      .finally(() => setLoading(false))
  }, [kind, page, pageSize])

  useEffect(() => {
    loadAssets(page, pageSize, kind)
  }, [kind, loadAssets, page, pageSize])

  const removeAsset = async (id: number) => {
    await assetsApi.remove(id)
    message.success('文件已删除')
    loadAssets()
  }

  const uploadProps: UploadProps = {
    showUploadList: false,
    customRequest: ({ file, onSuccess, onError }) => {
      assetsApi
        .upload(file as File)
        .then(() => {
          onSuccess?.({})
          message.success('上传成功')
          setPage(1)
          loadAssets(1, pageSize, kind)
        })
        .catch((error) => {
          onError?.(error as Error)
        })
    },
  }

  const submitNote = async () => {
    const values = await noteForm.validateFields()
    const title = values.title
    const content = values.content
    const safeName = title.trim().replace(/[\\/:*?"<>|]+/g, '_').slice(0, 80) || 'note'
    const blob = new Blob([content], { type: 'text/markdown' })
    const file = new File([blob], `${safeName}.md`, { type: 'text/markdown' })

    setCreatingNote(true)
    try {
      await assetsApi.upload(file)
      message.success('笔记已保存')
      setNoteModalOpen(false)
      noteForm.resetFields()
      setPage(1)
      loadAssets(1, pageSize, kind)
    } finally {
      setCreatingNote(false)
    }
  }

  return (
    <Space direction="vertical" size={16} className="w-full">
      <Card className="cms-card">
        <Space className="w-full" style={{ justifyContent: 'space-between' }}>
          <Space direction="vertical" size={4}>
            <Typography.Title level={3} style={{ margin: 0 }}>
              {meta.title}管理
            </Typography.Title>
            <Typography.Paragraph type="secondary" style={{ margin: 0 }}>
              {meta.description}
            </Typography.Paragraph>
          </Space>
          <Space>
            <Select<AssetKind>
              value={kind}
              style={{ width: 180 }}
              onChange={(nextKind) => {
                setKind(nextKind)
                setPage(1)
              }}
              options={[
                { label: '图片', value: 'image' },
                { label: '视频', value: 'video' },
                { label: '音频', value: 'audio' },
                { label: '文档', value: 'document' },
                { label: '其他', value: 'other' },
              ]}
            />
            {isNotesCategory ? (
              <Button icon={<EditOutlined />} disabled={!canUpload} onClick={() => setNoteModalOpen(true)}>
                新建笔记
              </Button>
            ) : (
              <Upload {...uploadProps}>
                <Button icon={<UploadOutlined />} disabled={!canUpload}>
                  上传文件
                </Button>
              </Upload>
            )}
          </Space>
        </Space>
      </Card>
      {loading ? <Spin /> : null}
      <Row gutter={[16, 16]}>
        {rows.map((item) => (
          <Col xs={24} md={12} xl={6} key={item.id}>
            <Card
              hoverable
              className="cms-card"
              cover={
                item.kind === 'image' ? (
                  <Image src={item.public_url} height={160} style={{ objectFit: 'cover' }} />
                ) : undefined
              }
              actions={[
                <Popconfirm
                  key="delete"
                  title="确认删除该文件？"
                  onConfirm={() => void removeAsset(item.id)}
                  disabled={!canDelete}
                >
                  <Button type="text" danger icon={<DeleteOutlined />} disabled={!canDelete} />
                </Popconfirm>,
              ]}
            >
              <Space direction="vertical" size={4}>
                <Typography.Text strong ellipsis>
                  {isNotesCategory ? item.filename.replace(/\.md$/i, '') : item.filename}
                </Typography.Text>
                <Typography.Text type="secondary">{item.mime_type}</Typography.Text>
                <Typography.Text type="secondary">{item.size_bytes} bytes</Typography.Text>
              </Space>
            </Card>
          </Col>
        ))}
      </Row>
      <Pagination
        current={page}
        pageSize={pageSize}
        total={total}
        showSizeChanger
        onChange={(nextPage, nextPageSize) => {
          setPage(nextPage)
          setPageSize(nextPageSize)
        }}
      />
      <Modal
        title="新建笔记"
        open={noteModalOpen}
        onCancel={() => {
          setNoteModalOpen(false)
          noteForm.resetFields()
        }}
        onOk={() => void submitNote()}
        okText="保存"
        confirmLoading={creatingNote}
        destroyOnHidden
      >
        <Form form={noteForm} layout="vertical">
          <Form.Item
            label="标题"
            name="title"
            rules={[
              { required: true, message: '请输入标题' },
              { max: 80, message: '标题最多 80 个字符' },
            ]}
          >
            <Input maxLength={80} />
          </Form.Item>
          <Form.Item
            label="内容"
            name="content"
            rules={[
              { required: true, message: '请输入内容' },
              { max: 20000, message: '内容最多 20000 个字符' },
            ]}
          >
            <Input.TextArea rows={10} maxLength={20000} />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}
