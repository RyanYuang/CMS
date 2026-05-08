import { PlusOutlined } from '@ant-design/icons'
import { Button, Checkbox, Form, Input, Modal, Popconfirm, Space, Table, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useMemo, useState } from 'react'
import { PageSectionCard } from '../../components/PageSectionCard'
import { rolesApi } from '../../services'
import type { Permission, Role } from '../../services'
import { hasPermission } from '../../utils/auth'

export function RolesPage() {
  const [form] = Form.useForm()
  const [roles, setRoles] = useState<Role[]>([])
  const [permissions, setPermissions] = useState<Permission[]>([])
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editing, setEditing] = useState<Role | null>(null)
  const canWrite = hasPermission('role:write')

  const groupedPermissions = useMemo(() => {
    const grouped: Record<string, Permission[]> = {}
    permissions.forEach((perm) => {
      const key = perm.code.split(':')[0]
      grouped[key] = grouped[key] || []
      grouped[key].push(perm)
    })
    return grouped
  }, [permissions])

  const load = () => {
    rolesApi.list().then(setRoles)
    rolesApi.listPermissions().then(setPermissions)
  }

  useEffect(() => {
    load()
  }, [])

  const openDialog = (role?: Role) => {
    setEditing(role ?? null)
    setDialogOpen(true)
    form.setFieldsValue({
      name: role?.name,
      description: role?.description,
      permission_codes: role?.permissions.map((item) => item.code) ?? [],
    })
  }

  const save = async () => {
    const values = await form.validateFields()
    if (editing) {
      await rolesApi.update(editing.id, {
        description: values.description,
        permission_codes: values.permission_codes,
      })
    } else {
      await rolesApi.create({
        name: values.name,
        description: values.description,
        permission_codes: values.permission_codes,
      })
    }
    setDialogOpen(false)
    load()
  }

  const columns: ColumnsType<Role> = [
    { title: '角色名', dataIndex: 'name' },
    { title: '成员数', dataIndex: 'member_count' },
    { title: '描述', dataIndex: 'description' },
    {
      title: '内置',
      dataIndex: 'is_builtin',
      render: (value: boolean) => (value ? <Tag color="purple">Built-in</Tag> : <Tag>Custom</Tag>),
    },
    {
      title: '权限数',
      render: (_, row) => <Tag>{row.permissions.length}</Tag>,
    },
    {
      title: '操作',
      render: (_, row) => (
        <Space>
          <Button type="link" onClick={() => openDialog(row)} disabled={!canWrite}>
            编辑
          </Button>
          {!row.is_builtin ? (
            <Popconfirm title="确认删除该角色？" onConfirm={() => void rolesApi.remove(row.id).then(load)} disabled={!canWrite}>
              <Button type="link" danger>
                删除
              </Button>
            </Popconfirm>
          ) : null}
        </Space>
      ),
    },
  ]

  return (
    <PageSectionCard
      title="Roles & Permissions"
      description="Manage RBAC roles and operational access."
      extra={
        <Button type="primary" icon={<PlusOutlined />} onClick={() => openDialog()} disabled={!canWrite}>
          Add Role
        </Button>
      }
    >
      <Table columns={columns} dataSource={roles} pagination={false} rowKey="id" />
      <Modal
        title={editing ? '编辑角色' : '新建角色'}
        open={dialogOpen}
        onCancel={() => setDialogOpen(false)}
        onOk={() => void save()}
      >
        <Form form={form} layout="vertical">
          <Form.Item name="name" label="角色名" rules={[{ required: true }]}>
            <Input disabled={Boolean(editing)} />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <Input />
          </Form.Item>
          <Form.Item name="permission_codes" label="权限">
            <Checkbox.Group style={{ width: '100%' }}>
              <Space direction="vertical" style={{ width: '100%' }}>
                {Object.entries(groupedPermissions).map(([group, items]) => (
                  <div key={group}>
                    <Tag>{group}</Tag>
                    <Checkbox.Group
                      options={items.map((item) => ({ label: item.code, value: item.code }))}
                      value={form.getFieldValue('permission_codes')}
                      onChange={(next) => form.setFieldValue('permission_codes', next)}
                    />
                  </div>
                ))}
              </Space>
            </Checkbox.Group>
          </Form.Item>
        </Form>
      </Modal>
    </PageSectionCard>
  )
}
