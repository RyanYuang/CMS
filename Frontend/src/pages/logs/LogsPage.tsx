import { Empty, Space } from 'antd'
import { PageSectionCard } from '../../components/PageSectionCard'

export function LogsPage() {
  return (
    <Space direction="vertical" size={20} className="w-full">
      <PageSectionCard title="操作日志">
        <Empty description="该模块尚未启用，敬请期待" />
      </PageSectionCard>
    </Space>
  )
}
