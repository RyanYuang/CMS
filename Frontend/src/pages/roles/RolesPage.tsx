import { PlusOutlined } from '@ant-design/icons'
import { Button, Switch, Table, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { PageSectionCard } from '../../components/PageSectionCard'

type RoleRow = {
  key: string
  role: string
  members: number
  critical: boolean
  status: 'Enabled' | 'Limited'
}

const roles: RoleRow[] = [
  { key: '1', role: 'Super Admin', members: 2, critical: true, status: 'Enabled' },
  { key: '2', role: 'Operations', members: 14, critical: false, status: 'Enabled' },
  { key: '3', role: 'Content Editor', members: 21, critical: false, status: 'Limited' },
]

const columns: ColumnsType<RoleRow> = [
  { title: 'Role', dataIndex: 'role' },
  { title: 'Members', dataIndex: 'members' },
  {
    title: 'Scope',
    dataIndex: 'critical',
    render: (value: boolean) => (value ? <Tag color="magenta">Critical</Tag> : <Tag>General</Tag>),
  },
  {
    title: 'Status',
    dataIndex: 'status',
    render: (value: RoleRow['status']) => <Switch checked={value === 'Enabled'} />,
  },
]

export function RolesPage() {
  return (
    <PageSectionCard
      title="Roles & Permissions"
      description="Manage RBAC roles and operational access."
      extra={
        <Button type="primary" icon={<PlusOutlined />}>
          Add Role
        </Button>
      }
    >
      <Table columns={columns} dataSource={roles} pagination={false} />
    </PageSectionCard>
  )
}
