import { PlusOutlined } from '@ant-design/icons'
import { Button, Form, Input, Modal, Popconfirm, Select, Space, Switch, Table, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useCallback, useEffect, useState } from 'react'
import { PageSectionCard } from '../../components/PageSectionCard'
import { rolesApi, usersApi } from '../../services'
import type { Role, UserItem } from '../../services'
import { hasPermission } from '../../utils/auth'

export function UsersPage() {
  const [form] = Form.useForm()
  const [keyword, setKeyword] = useState('')
  const [rows, setRows] = useState<UserItem[]>([])
  const [roles, setRoles] = useState<Role[]>([])
  const [roleId, setRoleId] = useState<number | undefined>()
  const [isActive, setIsActive] = useState<boolean | undefined>()
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [total, setTotal] = useState(0)
  const [dialogOpen, setDialogOpen] = useState(false)
  const canWrite = hasPermission('user:write')

  const loadUsers = useCallback(() => {
    usersApi
      .list({ keyword, role_id: roleId, is_active: isActive, page, page_size: pageSize })
      .then((resp) => {
        setRows(resp.items)
        setTotal(resp.meta.total)
      })
  }, [isActive, keyword, page, pageSize, roleId])

  useEffect(() => {
    loadUsers()
  }, [loadUsers])

  useEffect(() => {
    rolesApi.list().then(setRoles)
  }, [])

  const createUser = async () => {
    const values = await form.validateFields()
    await usersApi.create({
      username: values.username,
      email: values.email,
      password: values.password,
      full_name: values.full_name,
      role_id: values.role_id,
      is_active: true,
    })
    setDialogOpen(false)
    form.resetFields()
    loadUsers()
  }

  const toggleUser = async (row: UserItem, next: boolean) => {
    await usersApi.update(row.id, { is_active: next })
    loadUsers()
  }

  const removeUser = async (id: number) => {
    await usersApi.remove(id)
    loadUsers()
  }

  const columns: ColumnsType<UserItem> = [
    { title: 'ID', dataIndex: 'id' },
    { title: '用户名', dataIndex: 'username' },
    { title: '昵称', dataIndex: 'full_name' },
    { title: '角色', render: (_, row) => row.role?.name || '-' },
    { title: '邮箱', dataIndex: 'email' },
    {
      title: '状态',
      dataIndex: 'is_active',
      render: (status: boolean) => <Tag color={status ? 'green' : 'red'}>{status ? '启用' : '停用'}</Tag>,
    },
    {
      title: '启停',
      render: (_, row) => (
        <Switch checked={row.is_active} disabled={!canWrite} onChange={(checked) => void toggleUser(row, checked)} />
      ),
    },
    {
      title: '操作',
      render: (_, row) => (
        <Popconfirm title="确认删除该用户？" onConfirm={() => void removeUser(row.id)} disabled={!canWrite}>
          <Button type="link" danger>
            删除
          </Button>
        </Popconfirm>
      ),
    },
  ]

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
            onChange={(event) => {
              setKeyword(event.target.value)
              setPage(1)
            }}
          />
          <Select
            allowClear
            placeholder="按角色筛选"
            style={{ width: 180 }}
            value={roleId}
            onChange={(value) => setRoleId(value)}
            options={roles.map((role) => ({ label: role.name, value: role.id }))}
          />
          <Select
            allowClear
            placeholder="按状态筛选"
            style={{ width: 140 }}
            value={isActive}
            onChange={(value) => setIsActive(value)}
            options={[
              { label: '启用', value: true },
              { label: '停用', value: false },
            ]}
          />
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setDialogOpen(true)} disabled={!canWrite}>
            新建用户
          </Button>
        </Space>
      }
    >
      <Table<UserItem>
        rowKey="id"
        columns={columns}
        dataSource={rows}
        pagination={{
          current: page,
          pageSize,
          total,
          onChange: (nextPage, nextPageSize) => {
            setPage(nextPage)
            setPageSize(nextPageSize)
          },
        }}
      />
      <Modal
        title="新建用户"
        open={dialogOpen}
        onCancel={() => setDialogOpen(false)}
        onOk={() => void createUser()}
        okText="创建"
      >
        <Form form={form} layout="vertical">
          <Form.Item name="username" label="用户名" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="email" label="邮箱" rules={[{ required: true, type: 'email' }]}>
            <Input />
          </Form.Item>
          <Form.Item name="password" label="密码" rules={[{ required: true, min: 6 }]}>
            <Input.Password />
          </Form.Item>
          <Form.Item name="full_name" label="昵称">
            <Input />
          </Form.Item>
          <Form.Item name="role_id" label="角色">
            <Select allowClear options={roles.map((role) => ({ label: role.name, value: role.id }))} />
          </Form.Item>
        </Form>
      </Modal>
    </PageSectionCard>
  )
}
