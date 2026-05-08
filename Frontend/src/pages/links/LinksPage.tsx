import type { LinkStatus } from '../../services'
import {
  DeleteOutlined,
  EditOutlined,
  PlusOutlined,
  SearchOutlined,
  UpOutlined,
  DownOutlined,
} from '@ant-design/icons'
import { Button, Form, Image, Input, Modal, Popconfirm, Space, Spin, Switch, Table, Tag, message } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useMemo, useState } from 'react'
import { linksApi } from '../../services'
import { formatDate } from '../../utils/format'
import { hasPermission } from '../../utils/auth'

type LinkRow = Awaited<ReturnType<typeof linksApi.list>>[number]

export function LinksPage() {
  const [form] = Form.useForm()
  const [rows, setRows] = useState<LinkRow[]>([])
  const [loading, setLoading] = useState(true)
  const [keyword, setKeyword] = useState('')
  const [statusFilter, setStatusFilter] = useState<'all' | 'online' | 'offline'>('all')
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [editingRow, setEditingRow] = useState<LinkRow | null>(null)
  const canWrite = hasPermission('link:write')

  const loadLinks = () => {
    linksApi
      .list()
      .then((resp) => {
        setRows(resp.sort((a, b) => a.sort_order - b.sort_order))
      })
      .finally(() => {
        setLoading(false)
      })
  }

  useEffect(() => {
    loadLinks()
  }, [])

  const filteredRows = useMemo(() => {
    return rows.filter((row) => {
      const matchesKeyword =
        row.title.toLowerCase().includes(keyword.toLowerCase()) ||
        row.url.toLowerCase().includes(keyword.toLowerCase())
      const matchesStatus = statusFilter === 'all' || row.status === statusFilter
      return matchesKeyword && matchesStatus
    })
  }, [rows, keyword, statusFilter])

  const openDialog = (row?: LinkRow) => {
    if (row) {
      setEditingRow(row)
      form.setFieldsValue({
        title: row.title,
        url: row.url,
        cover: row.cover,
        status: row.status === 'online',
        order: row.sort_order,
      })
    } else {
      setEditingRow(null)
      form.setFieldsValue({
        title: '',
        url: '',
        cover: '',
        status: true,
        order: rows.length + 1,
      })
    }
    setIsDialogOpen(true)
  }

  const saveLink = async () => {
    const values = await form.validateFields()
    const payload = {
      title: values.title,
      url: values.url,
      cover: values.cover,
      status: (values.status ? 'online' : 'offline') as LinkStatus,
      sort_order: Number(values.order) || 1,
    }
    if (editingRow) {
      await linksApi.update(editingRow.id, payload)
      message.success('链接已更新')
    } else {
      await linksApi.create(payload)
      message.success('链接已创建')
    }
    loadLinks()
    setIsDialogOpen(false)
  }

  const removeLink = async (id: number) => {
    await linksApi.remove(id)
    loadLinks()
    message.success('链接已删除')
  }

  const moveLink = async (id: number, direction: 'up' | 'down') => {
    const index = filteredRows.findIndex((row) => row.id === id)
    if ((direction === 'up' && index === 0) || (direction === 'down' && index === filteredRows.length - 1)) {
      return
    }
    const nextIndex = direction === 'up' ? index - 1 : index + 1
    const nextRows = [...filteredRows]
    ;[nextRows[index], nextRows[nextIndex]] = [nextRows[nextIndex], nextRows[index]]
    await linksApi.reorder(nextRows.map((item) => item.id))
    loadLinks()
    message.success('排序已更新')
  }

  const columns: ColumnsType<LinkRow> = [
    {
      title: '排序',
      key: 'orderActions',
      render: (_, row, index) => (
        <Space direction="vertical" size={2}>
          <Button
            size="small"
            icon={<UpOutlined />}
            disabled={index === 0 || !canWrite}
            onClick={() => void moveLink(row.id, 'up')}
          />
          <Button
            size="small"
            icon={<DownOutlined />}
            disabled={index === filteredRows.length - 1 || !canWrite}
            onClick={() => void moveLink(row.id, 'down')}
          />
        </Space>
      ),
    },
    { title: '封面', dataIndex: 'cover', render: (cover) => <Image width={48} height={48} src={cover} /> },
    { title: '标题', dataIndex: 'title' },
    { title: 'URL', dataIndex: 'url' },
    {
      title: '状态',
      dataIndex: 'status',
      render: (status: LinkRow['status']) => (
        <Tag color={status === 'online' ? 'green' : 'default'}>
          {status === 'online' ? '已上线' : '已下线'}
        </Tag>
      ),
    },
    { title: '更新时间', dataIndex: 'updated_at', render: (value: string) => formatDate(value) },
    {
      title: '操作',
      key: 'actions',
      render: (_, row) => (
        <Space>
          <Button type="text" icon={<EditOutlined />} onClick={() => openDialog(row)} disabled={!canWrite} />
          <Popconfirm title="确认删除" description="此操作无法撤销" onConfirm={() => void removeLink(row.id)} disabled={!canWrite}>
            <Button danger type="text" icon={<DeleteOutlined />} />
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <Space direction="vertical" size={24} className="w-full">
      <Space className="w-full" style={{ justifyContent: 'space-between' }}>
        <Space direction="vertical" size={2}>
          <h1 style={{ margin: 0, fontSize: 30, fontWeight: 500 }}>链接管理</h1>
          <span style={{ color: '#737373' }}>管理您的外链资源</span>
        </Space>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => openDialog()} disabled={!canWrite}>
          新增链接
        </Button>
      </Space>
      <Space className="w-full" style={{ justifyContent: 'space-between' }}>
        <Input
          style={{ maxWidth: 420 }}
          prefix={<SearchOutlined />}
          placeholder="搜索标题或 URL..."
          value={keyword}
          onChange={(event) => setKeyword(event.target.value)}
        />
        <Space>
          <Button type={statusFilter === 'all' ? 'primary' : 'default'} onClick={() => setStatusFilter('all')}>
            全部
          </Button>
          <Button type={statusFilter === 'online' ? 'primary' : 'default'} onClick={() => setStatusFilter('online')}>
            已上线
          </Button>
          <Button type={statusFilter === 'offline' ? 'primary' : 'default'} onClick={() => setStatusFilter('offline')}>
            已下线
          </Button>
        </Space>
      </Space>
      {loading ? <Spin /> : null}
      <Table<LinkRow> rowKey="id" columns={columns} dataSource={filteredRows} pagination={false} className="cms-card" />
      <Modal
        title={editingRow ? '编辑链接' : '新增链接'}
        open={isDialogOpen}
        onCancel={() => setIsDialogOpen(false)}
        onOk={saveLink}
        okText={editingRow ? '保存' : '创建'}
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="title" label="标题" rules={[{ required: true, message: '请输入标题' }]}>
            <Input placeholder="请输入标题" />
          </Form.Item>
          <Form.Item name="url" label="URL" rules={[{ required: true, message: '请输入 URL' }]}>
            <Input placeholder="https://example.com" />
          </Form.Item>
          <Form.Item name="cover" label="封面图片 URL">
            <Input placeholder="https://example.com/image.jpg" />
          </Form.Item>
          <Form.Item name="order" label="排序">
            <Input type="number" />
          </Form.Item>
          <Form.Item name="status" label="上线状态" valuePropName="checked">
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </Space>
  )
}
