import { PlusOutlined } from '@ant-design/icons'
import { Button, Input, Space, Table, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useState } from 'react'
import { PageSectionCard } from '../../components/PageSectionCard'
import { fetchUsers } from '../../services/api'

type UserRow = {
  id: string
  name: string
  role: string
  email: string
  status: 'Active' | 'Pending' | 'Suspended'
}

const columns: ColumnsType<UserRow> = [
  { title: 'User ID', dataIndex: 'id' },
  { title: 'Name', dataIndex: 'name' },
  { title: 'Role', dataIndex: 'role' },
  { title: 'Email', dataIndex: 'email' },
  {
    title: 'Status',
    dataIndex: 'status',
    render: (status: UserRow['status']) => {
      const color = status === 'Active' ? 'green' : status === 'Pending' ? 'gold' : 'red'
      return <Tag color={color}>{status}</Tag>
    },
  },
]

export function UsersPage() {
  const [keyword, setKeyword] = useState('')
  const [rows, setRows] = useState<UserRow[]>([])

  useEffect(() => {
    void fetchUsers().then(setRows)
  }, [])

  const filteredRows = rows.filter(
    (row) =>
      row.name.toLowerCase().includes(keyword.toLowerCase()) ||
      row.email.toLowerCase().includes(keyword.toLowerCase()),
  )

  return (
    <PageSectionCard
      title="User Management"
      description="View and manage all CMS user accounts."
      extra={
        <Space>
          <Input
            allowClear
            placeholder="Search user"
            value={keyword}
            onChange={(event) => setKeyword(event.target.value)}
          />
          <Button type="primary" icon={<PlusOutlined />}>
            New User
          </Button>
        </Space>
      }
    >
      <Table<UserRow> rowKey="id" columns={columns} dataSource={filteredRows} />
    </PageSectionCard>
  )
}
