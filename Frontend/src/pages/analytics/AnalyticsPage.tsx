import { Empty, Space } from 'antd'
import { PageSectionCard } from '../../components/PageSectionCard'

export function AnalyticsPage() {
  return (
    <Space direction="vertical" size={20} className="w-full">
      <PageSectionCard title="Analytics">
        <Empty description="该模块尚未启用，敬请期待" />
      </PageSectionCard>
    </Space>
  )
}
