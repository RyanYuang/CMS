import { EyeOutlined, FilterOutlined } from '@ant-design/icons'
import { Button, Select, Space, Table, Tag } from 'antd'
import type { ColumnsType } from 'antd/es/table'
import { useEffect, useState } from 'react'
import { PageSectionCard } from '../../components/PageSectionCard'
import { fetchOrders } from '../../services/api'

type OrderRow = {
  id: string
  customer: string
  amount: number
  status: 'Paid' | 'Processing' | 'Refunded'
  createdAt: string
}

const columns: ColumnsType<OrderRow> = [
  { title: 'Order ID', dataIndex: 'id' },
  { title: 'Customer', dataIndex: 'customer' },
  { title: 'Amount', dataIndex: 'amount', render: (value: number) => `$${value}` },
  {
    title: 'Status',
    dataIndex: 'status',
    render: (status: OrderRow['status']) => {
      const color = status === 'Paid' ? 'green' : status === 'Refunded' ? 'red' : 'blue'
      return <Tag color={color}>{status}</Tag>
    },
  },
  { title: 'Created At', dataIndex: 'createdAt' },
  {
    title: 'Actions',
    key: 'actions',
    render: () => (
      <Button type="link" icon={<EyeOutlined />}>
        Details
      </Button>
    ),
  },
]

export function OrdersPage() {
  const [statusFilter, setStatusFilter] = useState<string>('All')
  const [rows, setRows] = useState<OrderRow[]>([])

  useEffect(() => {
    void fetchOrders().then(setRows)
  }, [])

  const dataSource = statusFilter === 'All' ? rows : rows.filter((row) => row.status === statusFilter)

  return (
    <PageSectionCard
      title="Order Center"
      description="Track transactions and fulfillment states."
      extra={
        <Space>
          <FilterOutlined />
          <Select
            value={statusFilter}
            style={{ width: 160 }}
            onChange={setStatusFilter}
            options={[
              { label: 'All', value: 'All' },
              { label: 'Paid', value: 'Paid' },
              { label: 'Processing', value: 'Processing' },
              { label: 'Refunded', value: 'Refunded' },
            ]}
          />
        </Space>
      }
    >
      <Table<OrderRow> rowKey="id" columns={columns} dataSource={dataSource} />
    </PageSectionCard>
  )
}
