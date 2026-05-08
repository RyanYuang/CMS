import { ArrowLeftOutlined, DeleteOutlined, PictureOutlined, SearchOutlined, UploadOutlined } from '@ant-design/icons'
import { App, Button, Card, Col, Empty, Image, Input, Row, Space, Spin, Typography, Upload } from 'antd'
import type { UploadProps } from 'antd'
import { useCallback, useEffect, useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { assetsApi } from '../../services'
import type { AssetItem } from '../../services'
import { hasPermission } from '../../utils/auth'

export function MediaCategoryPage() {
  const navigate = useNavigate()
  const { message, modal } = App.useApp()
  const [keyword, setKeyword] = useState('')
  const [rows, setRows] = useState<AssetItem[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const canUpload = hasPermission('asset:write')
  const canDelete = hasPermission('asset:delete')

  const loadAssets = useCallback((showLoading = true) => {
    if (showLoading) {
      setLoading(true)
    }
    assetsApi
      .list({ page: 1, page_size: 200, kind: 'image' })
      .then((resp) => {
        setRows(resp.items)
      })
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    let active = true
    assetsApi
      .list({ page: 1, page_size: 200, kind: 'image' })
      .then((resp) => {
        if (active) {
          setRows(resp.items)
        }
      })
      .finally(() => {
        if (active) {
          setLoading(false)
        }
      })
    return () => {
      active = false
    }
  }, [])

  const filtered = useMemo(() => {
    const kw = keyword.trim().toLowerCase()
    if (!kw) return rows
    return rows.filter((item) => item.filename.toLowerCase().includes(kw) || item.mime_type.toLowerCase().includes(kw))
  }, [keyword, rows])

  const removeAsset = (item: AssetItem) => {
    modal.confirm({
      title: '确认删除该图片？',
      content: '此操作无法撤销，将永久删除该图片文件。',
      okText: '删除',
      okButtonProps: { danger: true },
      cancelText: '取消',
      onOk: async () => {
        setDeletingId(item.id)
        try {
          await assetsApi.remove(item.id)
          setRows((prev) => prev.filter((row) => row.id !== item.id))
          message.success('图片已删除')
        } finally {
          setDeletingId(null)
        }
      },
    })
  }

  const uploadProps: UploadProps = {
    accept: 'image/*',
    showUploadList: false,
    customRequest: ({ file, onSuccess, onError }) => {
      setUploading(true)
      assetsApi
        .upload(file as File)
        .then(() => {
          onSuccess?.({})
          message.success('上传成功')
          loadAssets()
        })
        .catch((error) => {
          onError?.(error as Error)
          message.error('上传失败，请稍后重试')
        })
        .finally(() => setUploading(false))
    },
  }

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
                照片管理
              </Typography.Title>
              <Typography.Paragraph type="secondary" style={{ margin: 0 }}>
                管理图片和摄影资源
              </Typography.Paragraph>
            </Space>
          </Space>
          <Upload {...uploadProps}>
            <Button type="primary" icon={<UploadOutlined />} loading={uploading} disabled={!canUpload}>
              上传图片
            </Button>
          </Upload>
        </Space>
      </Card>

      <Card className="cms-card">
        <Input
          allowClear
          size="large"
          prefix={<SearchOutlined />}
          placeholder="搜索图片名称或格式..."
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
        />
      </Card>

      {loading ? (
        <div style={{ textAlign: 'center', padding: 48 }}>
          <Spin />
        </div>
      ) : filtered.length === 0 ? (
        <Card className="cms-card" style={{ padding: '48px 0' }}>
          <Empty
            image={<PictureOutlined style={{ fontSize: 64, color: '#bfbfbf' }} />}
            imageStyle={{ height: 80 }}
            description={keyword.trim() ? '没有匹配的图片' : '还没有照片资源'}
          />
        </Card>
      ) : (
        <Row gutter={[16, 16]}>
          {filtered.map((item) => (
            <Col xs={24} md={12} lg={8} xl={6} key={item.id}>
              <Card
                hoverable
                className="cms-card cms-media-card"
                cover={<Image src={item.public_url} height={180} style={{ objectFit: 'cover' }} preview={false} />}
                actions={[
                  <Button
                    key="delete"
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    loading={deletingId === item.id}
                    disabled={!canDelete}
                    onClick={() => removeAsset(item)}
                  >
                    删除
                  </Button>,
                ]}
              >
                <Space direction="vertical" size={4}>
                  <Typography.Text strong ellipsis={{ tooltip: item.filename }}>
                    {item.filename}
                  </Typography.Text>
                  <Typography.Text type="secondary">{item.mime_type}</Typography.Text>
                </Space>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </Space>
  )
}
